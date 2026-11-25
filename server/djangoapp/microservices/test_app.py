"""Behavioral checks of the real bundled sentiment model."""
import unittest

from app import app


class SentimentTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_positive(self):
        response = self.client.get("/analyze/Excellent friendly service!")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["sentiment"], "positive")
        self.assertGreaterEqual(response.json["scores"]["compound"], 0.05)

    def test_negative(self):
        response = self.client.get("/analyze/Terrible rude service. I hate it.")
        self.assertEqual(response.json["sentiment"], "negative")

    def test_neutral(self):
        response = self.client.get("/analyze/The car has four wheels.")
        self.assertEqual(response.json["sentiment"], "neutral")

    def test_blank_and_invalid_json(self):
        self.assertEqual(self.client.get("/analyze?text=%20").status_code, 400)
        self.assertEqual(self.client.post("/analyze", json=[]).status_code, 400)

    def test_json_and_length_limit(self):
        response = self.client.post("/analyze", json={"text": "I love the car!"})
        self.assertEqual(response.json["sentiment"], "positive")
        self.assertEqual(
            self.client.post("/analyze", json={"text": "x" * 5001}).status_code, 400
        )

    def test_health(self):
        self.assertEqual(self.client.get("/health").json["status"], "ok")


if __name__ == "__main__":
    unittest.main()
