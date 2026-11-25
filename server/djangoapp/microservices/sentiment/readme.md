# Offline sentiment resource

The VADER lexicon archive is supplied by the IBM Skills Network starter project.
The service loads it relative to app.py; it does not download NLTK data at runtime.

Run: python app.py
Check: python -m unittest -v test_app.py
GET /analyze/Excellent%20service or POST /analyze with {"text":"Excellent service"}.

Classification uses VADER compound score: positive >= 0.05; negative <= -0.05;
neutral otherwise. These are model predictions, not verified customer intent.

Documentation:
https://www.nltk.org/api/nltk.sentiment.vader.html
https://github.com/cjhutto/vaderSentiment
