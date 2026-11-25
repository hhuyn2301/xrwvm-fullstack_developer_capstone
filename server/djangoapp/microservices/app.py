"""Sentiment microservice using the course-provided offline VADER lexicon."""

import os
from pathlib import Path

from flask import Flask, jsonify, request
from nltk import data as nltk_data
from nltk.sentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
app.json.sort_keys = False
nltk_data.path.insert(0, str(Path(__file__).resolve().parent))
LEXICON = "sentiment/vader_lexicon.zip/vader_lexicon/vader_lexicon.txt"
analyzer = SentimentIntensityAnalyzer(lexicon_file=LEXICON)


def sentiment_result(text):
    """Classify VADER compound scores using its standard +/-0.05 thresholds."""
    if not isinstance(text, str) or not text.strip():
        return None, "Provide non-empty review text."
    if len(text) > 5000:
        return None, "Review text must not exceed 5000 characters."
    scores = analyzer.polarity_scores(text.strip())
    compound = scores["compound"]
    sentiment = "positive" if compound >= 0.05 else (
        "negative" if compound <= -0.05 else "neutral"
    )
    return {"sentiment": sentiment, "scores": scores}, None


@app.get("/")
def home():
    return jsonify(
        service="Review Sentiment Analyzer",
        method="NLTK VADER",
        endpoints=["/health", "/analyze/Excellent%20service", "/analyze?text=Excellent%20service"],
    )


@app.get("/health")
def health():
    return jsonify(status="ok", lexicon="bundled-vader")


@app.get("/analyze")
@app.get("/analyze/")
@app.get("/analyze/<path:input_txt>")
def analyze_sentiment(input_txt=None):
    text = input_txt if input_txt is not None else request.args.get("text", "")
    result, error = sentiment_result(text)
    if error:
        return jsonify(error=error), 400
    return jsonify(result)


@app.post("/analyze")
def analyze_json():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="A JSON object with a text field is required."), 400
    result, error = sentiment_result(data.get("text"))
    if error:
        return jsonify(error=error), 400
    return jsonify(result)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", os.getenv("SENTIMENT_PORT", "5050"))),
        debug=False,
    )
