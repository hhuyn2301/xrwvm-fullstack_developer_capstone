"""Tests for user sessions, review authorization and catalogue persistence."""
from unittest.mock import patch
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase
from .models import CarMake, CarModel
from .restapis import BackendError

class PortalTests(TestCase):
    def setUp(self):
        self.password = "Capstone-test-pass-6942!"
        self.user = User.objects.create_user("reviewer", password=self.password)
        make = CarMake.objects.create(name="Toyota")
        CarModel.objects.create(
            car_make=make, name="Camry", type="Sedan", year=2023, dealer_id=30
        )

    def post(self, url, body):
        return self.client.post(url, body, content_type="application/json")

    def test_register_login_logout_and_session(self):
        result = self.post("/djangoapp/register", {
            "userName": "new_reviewer", "password": "Better-pass-3958!",
            "firstName": "New", "lastName": "Reviewer", "email": "",
        })
        self.assertEqual(result.status_code, 201)
        self.assertTrue(self.client.get("/djangoapp/session").json()["authenticated"])
        self.assertEqual(self.post("/djangoapp/logout", {}).status_code, 200)
        self.assertFalse(self.client.get("/djangoapp/session").json()["authenticated"])
        self.assertEqual(self.post("/djangoapp/login", {
            "userName": "new_reviewer", "password": "Better-pass-3958!"
        }).status_code, 200)

    def test_bad_login_and_non_object_json(self):
        self.assertEqual(self.post("/djangoapp/login", {
            "userName": "reviewer", "password": "wrong"
        }).status_code, 401)
        self.assertEqual(self.post("/djangoapp/login", []).status_code, 400)

    def test_duplicate_username_does_not_overwrite(self):
        response = self.post("/djangoapp/register", {
            "userName": "reviewer", "password": "Different-pass-8239!",
        })
        self.assertEqual(response.status_code, 409)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_csrf_is_required_for_authentication(self):
        client = Client(enforce_csrf_checks=True)
        body = {"userName": "reviewer", "password": self.password}
        self.assertEqual(client.post(
            "/djangoapp/login", body, content_type="application/json"
        ).status_code, 403)
        client.get("/djangoapp/csrf")
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(
            "/djangoapp/login", body, content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        ).status_code, 200)

    @patch("djangoapp.views.post_review")
    def test_anonymous_review_never_reaches_backend(self, post_mock):
        result = self.post("/djangoapp/add_review", {
            "dealership": 1, "review": "An anonymous attempt", "purchase": False,
        })
        self.assertEqual(result.status_code, 401)
        post_mock.assert_not_called()

    @patch("djangoapp.views.get_request", return_value={"id": 1})
    @patch("djangoapp.views.post_review", return_value={"id": 51})
    def test_review_author_is_from_authenticated_session(self, post_mock, get_mock):
        self.client.force_login(self.user)
        result = self.post("/djangoapp/add_review", {
            "name": "Someone Else", "dealership": 1,
            "review": "Helpful staff and a straightforward visit.", "purchase": False,
        })
        self.assertEqual(result.status_code, 201)
        self.assertEqual(post_mock.call_args.args[0]["name"], "reviewer")
        self.assertEqual(post_mock.call_args.args[0]["car_year"], 0)

    @patch("djangoapp.views.post_review")
    def test_invalid_car_cannot_be_posted(self, post_mock):
        self.client.force_login(self.user)
        result = self.post("/djangoapp/add_review", {
            "dealership": 1, "review": "A purchase review", "purchase": True,
            "car_make": "Toyota", "car_model": "Not in catalogue", "car_year": 2023,
            "purchase_date": "2023-01-01",
        })
        self.assertEqual(result.status_code, 400)
        post_mock.assert_not_called()

    @patch("djangoapp.views.get_request", side_effect=BackendError("Unavailable"))
    def test_upstream_failure_is_reported_without_fake_data(self, get_mock):
        result = self.client.get("/djangoapp/get_dealers")
        self.assertEqual(result.status_code, 502)
        self.assertIn("error", result.json())
        self.assertNotIn("dealers", result.json())

    def test_car_seed_is_idempotent(self):
        call_command("seed_cars", verbosity=0)
        first_count = CarModel.objects.count()
        self.assertGreater(first_count, 1)
        call_command("seed_cars", verbosity=0)
        self.assertEqual(CarModel.objects.count(), first_count)
        self.assertEqual(CarMake.objects.count(), 5)

    def test_car_catalogue_contains_make_and_model(self):
        result = self.client.get("/djangoapp/get_cars")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["cars"][0]["car_make"], "Toyota")
        self.assertEqual(result.json()["cars"][0]["name"], "Camry")
