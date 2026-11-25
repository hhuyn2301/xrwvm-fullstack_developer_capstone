"""Course-compatible HTTP endpoint names."""
from django.urls import path
from . import views

app_name = "djangoapp"
urlpatterns = [
    path("csrf", views.csrf_token, name="csrf"),
    path("session", views.session_user, name="session"),
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("register", views.registration, name="register"),
    path("registration", views.registration, name="registration"),
    path("get_dealers", views.get_dealerships, name="get_dealers"),
    path("get_dealers/<str:state>", views.get_dealerships, name="get_dealers_state"),
    path("dealer/<int:dealer_id>", views.get_dealer_details, name="dealer"),
    path("reviews/dealer/<int:dealer_id>", views.get_dealer_reviews, name="reviews"),
    path("review/dealer/<int:dealer_id>", views.get_dealer_reviews, name="review"),
    path("get_cars", views.get_cars, name="get_cars"),
    path("get_car_makes", views.get_makes, name="get_car_makes"),
    path("add_review", views.add_review, name="add_review"),
    path("analyze/<path:text>", views.analyze_review, name="analyze"),
]
