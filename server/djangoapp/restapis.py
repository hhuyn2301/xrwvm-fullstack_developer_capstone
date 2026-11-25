"""HTTP clients for the Express/Mongo and sentiment microservices."""
from urllib.parse import quote
import requests
from django.conf import settings

class BackendError(Exception):
    """An upstream microservice could not fulfil the request."""
    def __init__(self, message, status=502):
        super().__init__(message)
        self.status = status

def request_json(method, url, **kwargs):
    try:
        response = requests.request(method, url, timeout=12, **kwargs)
        if response.status_code == 404:
            raise BackendError("Requested record was not found.", 404)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise BackendError("A backend service is unavailable. Please try again.") from exc

def get_request(endpoint, **params):
    return request_json("GET", f"{settings.BACKEND_URL}/{endpoint.lstrip('/')}", params=params)

def analyze_review_sentiments(text):
    return request_json(
        "GET", f"{settings.SENTIMENT_ANALYZER_URL}/analyze/{quote(text, safe='')}"
    )

def post_review(data_dict):
    headers = {}
    if settings.BACKEND_WRITE_API_TOKEN:
        headers["X-API-Key"] = settings.BACKEND_WRITE_API_TOKEN
    return request_json(
        "POST", f"{settings.BACKEND_URL}/insert_review", json=data_dict, headers=headers
    )
