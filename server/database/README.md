# Dealership and review API

Run with real MongoDB:

    npm ci
    MONGODB_URI=mongodb://127.0.0.1:27017/dealershipsDB npm start

Or from this directory:

    docker compose up --build

The API listens on port 3030. MongoDB remains inside the Docker network.
The JSON files in data/ are the supplied course data (50 dealers, 50 reviews).
Startup inserts missing seed IDs only; it never deletes existing records.
A MongoDB counter allocates review IDs atomically for concurrent requests.

Endpoints:
- GET /health
- GET /fetchDealers
- GET /fetchDealers/Kansas
- GET /fetchDealer/15
- GET /fetchReviews
- GET /fetchReviews/dealer/15
- POST /insert_review

A write accepts a JSON object with name, dealership, review, purchase,
purchase_date, car_make, car_model and car_year. Set purchase to a Boolean.
For a purchase, use an actual YYYY-MM-DD date and a valid integer car year.
Without a purchase, vehicle fields can be omitted.

Set WRITE_API_TOKEN for deployment; then the Django proxy must send the same
value in the X-API-Key header (its BACKEND_WRITE_API_TOKEN setting).
Do not put that token in frontend JavaScript.

Run npm test for validation and HTTP error handling checks without a database.
No database connection or seeding occurs merely by importing app.js.

Useful screenshot data:
- Kansas: dealer 8, Bytecard Car Dealership.
- Dealer 15 has three supplied reviews.

This directory's compose file runs the database API only. The project-root
compose file runs the complete application and sentiment service.
