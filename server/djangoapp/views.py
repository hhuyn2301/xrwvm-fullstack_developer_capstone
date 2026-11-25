"""Session authentication, catalogue and microservice proxy views."""
import json
import logging
from datetime import date
from urllib.parse import quote
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from .models import CarMake, CarModel
from .restapis import BackendError, get_request, post_review, analyze_review_sentiments

logger = logging.getLogger(__name__)

def error(message, status=400):
    return JsonResponse({"error": message}, status=status)

def json_body(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("A valid JSON object is required.") from exc
    if not isinstance(body, dict):
        raise ValueError("A JSON object is required.")
    return body

def text_field(body, key, limit=150, required=True):
    value = body.get(key, "")
    if not isinstance(value, str):
        raise ValueError(f"{key} must be text.")
    value = value.strip()
    if required and not value:
        raise ValueError(f"{key} is required.")
    if len(value) > limit:
        raise ValueError(f"{key} must contain at most {limit} characters.")
    return value

@require_GET
def health(request):
    return JsonResponse({"status": "ok", "service": "dealership-django"})

@require_GET
@ensure_csrf_cookie
def csrf_token(request):
    return JsonResponse({"status": "ok"})

@require_GET
@never_cache
@ensure_csrf_cookie
def session_user(request):
    authenticated = request.user.is_authenticated
    return JsonResponse({
        "authenticated": authenticated,
        "userName": request.user.username if authenticated else "",
        "firstName": request.user.first_name if authenticated else "",
    })

@require_GET
@ensure_csrf_cookie
def frontend(request, **kwargs):
    if not (settings.BASE_DIR / "frontend" / "build" / "index.html").exists():
        return error("Frontend is not built. Run npm ci and npm run build in server/frontend.", 503)
    return render(request, "index.html")

@require_POST
def login_user(request):
    try:
        body = json_body(request)
        username = text_field(body, "userName")
        password = body.get("password")
        if not isinstance(password, str) or not password:
            return error("password is required.")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return error("Invalid username or password.", 401)
        login(request, user)
        return JsonResponse({
            "status": "Authenticated", "authenticated": True,
            "userName": user.username, "firstName": user.first_name,
        })
    except ValueError as exc:
        return error(str(exc))

@require_POST
def logout_user(request):
    logout(request)
    return JsonResponse({"status": "Logged out", "authenticated": False})

@require_POST
def registration(request):
    try:
        body = json_body(request)
        username = text_field(body, "userName")
        first_name = text_field(body, "firstName", required=False)
        last_name = text_field(body, "lastName", required=False)
        email = text_field(body, "email", limit=254, required=False)
        password = body.get("password")
        if not isinstance(password, str):
            return error("password is required.")
        User._meta.get_field("username").run_validators(username)
        if email:
            validate_email(email)
        candidate = User(
            username=username, first_name=first_name, last_name=last_name, email=email
        )
        validate_password(password, user=candidate)
        with transaction.atomic():
            user = User.objects.create_user(
                username=username, password=password, first_name=first_name,
                last_name=last_name, email=email,
            )
        login(request, user)
        return JsonResponse({
            "status": "Authenticated", "authenticated": True,
            "userName": user.username, "firstName": user.first_name,
        }, status=201)
    except IntegrityError:
        return error("This username is already registered.", 409)
    except ValidationError as exc:
        return error(" ".join(exc.messages))
    except ValueError as exc:
        return error(str(exc))

@require_GET
def get_dealerships(request, state=None):
    try:
        endpoint = "fetchDealers"
        if state and state.lower() != "all":
            endpoint += "/" + quote(state, safe="")
        return JsonResponse({"status": 200, "dealers": get_request(endpoint)})
    except BackendError as exc:
        return error(str(exc), exc.status)

@require_GET
def get_dealer_details(request, dealer_id):
    try:
        return JsonResponse({
            "status": 200, "dealer": get_request(f"fetchDealer/{dealer_id}")
        })
    except BackendError as exc:
        return error(str(exc), exc.status)

@require_GET
def get_dealer_reviews(request, dealer_id):
    try:
        reviews = get_request(f"fetchReviews/dealer/{dealer_id}")
        for review in reviews:
            try:
                review["sentiment"] = analyze_review_sentiments(
                    review.get("review", "")
                )["sentiment"]
            except (BackendError, KeyError):
                review["sentiment"] = "unavailable"
        return JsonResponse({"status": 200, "reviews": reviews})
    except BackendError as exc:
        return error(str(exc), exc.status)

@require_GET
def get_cars(request):
    cars = [
        {
            "id": car.pk, "car_make": car.car_make.name, "name": car.name,
            "type": car.type, "year": car.year, "dealer_id": car.dealer_id,
        }
        for car in CarModel.objects.select_related("car_make").all()
    ]
    return JsonResponse({"status": 200, "cars": cars})

@require_GET
def get_makes(request):
    return JsonResponse({
        "status": 200,
        "car_makes": list(CarMake.objects.values("id", "name", "description")),
    })

@require_GET
def analyze_review(request, text):
    try:
        return JsonResponse(analyze_review_sentiments(text))
    except BackendError as exc:
        return error(str(exc), exc.status)

@require_POST
def add_review(request):
    if not request.user.is_authenticated:
        return error("Please log in before posting a review.", 401)
    try:
        body = json_body(request)
        dealer_id = body.get("dealership")
        if isinstance(dealer_id, bool):
            raise ValueError("dealership must be a positive integer.")
        dealer_id = int(dealer_id)
        if dealer_id < 1:
            raise ValueError("dealership must be a positive integer.")
        review_text = text_field(body, "review", limit=4000)
        purchase = body.get("purchase", False)
        if not isinstance(purchase, bool):
            raise ValueError("purchase must be true or false.")
        payload = {
            "name": request.user.username, "dealership": dealer_id,
            "review": review_text, "purchase": purchase,
            "purchase_date": "", "car_make": "", "car_model": "", "car_year": 0,
        }
        if purchase:
            make = text_field(body, "car_make", limit=100)
            model = text_field(body, "car_model", limit=100)
            year_value = body.get("car_year")
            if isinstance(year_value, bool):
                raise ValueError("car_year must be a valid year.")
            year = int(year_value)
            if not CarModel.objects.filter(
                car_make__name=make, name=model, year=year
            ).exists():
                raise ValueError("Choose a valid car make, model and year.")
            purchase_date = text_field(body, "purchase_date", limit=10)
            parsed_date = date.fromisoformat(purchase_date)
            if parsed_date > date.today():
                raise ValueError("Purchase date cannot be in the future.")
            payload.update(
                car_make=make, car_model=model, car_year=year,
                purchase_date=parsed_date.isoformat(),
            )
        get_request(f"fetchDealer/{dealer_id}")
        saved = post_review(payload)
        return JsonResponse({"status": 201, "review": saved}, status=201)
    except (TypeError, ValueError) as exc:
        return error(str(exc) or "Invalid review fields.")
    except BackendError as exc:
        return error(str(exc), exc.status)
