# Best Cars: Full-Stack Dealership Review Platform

A completed implementation of the IBM Full-Stack Developer capstone starter:
Django user management and car catalogue, a React UI, Express/MongoDB dealer and
review APIs, and an offline VADER sentiment microservice.

## Run with Docker Compose

Requirements: Docker Engine with Docker Compose v2 and Python 3.

~~~bash
python3 scripts/create_env.py
docker compose up --build
~~~

Open http://localhost:8000. The API services are available at
http://localhost:3030 and http://localhost:5050.

Create your own administrator account:

~~~bash
docker compose exec web python manage.py createsuperuser --username root
~~~

The environment initializer creates fresh secrets without replacing an existing
.env. Keep that file private. For a Skills Network proxy hostname, set the
actual host in DJANGO_ALLOWED_HOSTS and complete HTTPS origin in
DJANGO_CSRF_TRUSTED_ORIGINS, then restart the web service.

## Features

- React registration, login, logout alert and authenticated username.
- Anonymous dealer browsing; state filter and dealership details.
- Authenticated reviews with purchase date, vehicle make, model and year.
- Review author comes from the Django session, not a client-supplied name.
- Django admin for 5 course car makes and 153 course car-model records.
- Express returns the 50 course dealerships and starts with 50 course reviews.
- MongoDB seeding is repeatable and retains newly written reviews.
- Concurrent review creation uses an atomic counter for unique IDs.
- Sentiment analysis uses the bundled VADER lexicon with no runtime download.
- CSRF protection for state-changing Django requests; service token for writes.
- Persistent SQLite and MongoDB volumes in Compose/Kubernetes.

## Project layout

| Path | Purpose |
|---|---|
| server/djangoapp | Authentication, car models/admin, proxy APIs, Django tests |
| server/frontend | React source, Vite configuration and npm lockfile |
| server/database | Express/Mongoose API, course data and Node tests |
| server/djangoapp/microservices | Flask/VADER service, lexicon and tests |
| .github/workflows | CI, manual image publication and manual deployment |
| deploy | Kubernetes renderer and deployment instructions |
| docs/RUBRIC_CHECKLIST.md | All 28 submission fields and screenshot requirements |
| docs/validation | Results of actual local service/integration checks |

## Development without the web container

Start MongoDB, Express and sentiment first, using the service READMEs or Compose.
Build React, then run Django:

~~~bash
cd server/frontend
npm ci
npm run build
cd ..
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_cars
python manage.py createsuperuser --username root
python manage.py runserver 0.0.0.0:8000
~~~

Python 3.12 and Node 22.12+ were used for compatibility. Point BACKEND_URL at
the running Express service and SENTIMENT_ANALYZER_URL at the sentiment service.
When Express has WRITE_API_TOKEN configured, set Django's
BACKEND_WRITE_API_TOKEN to the same token. Environment variables take precedence
over server/.env and the repository .env.

## Validation performed

- 10 Django functional tests passed.
- 5 Node behavioral tests and 6 Flask tests passed.
- Real MongoDB 7.0.16 / Express / Flask integration passed.
- Real HTTP requests across Django and all microservices passed, including
  registration, session handling, catalogue queries, CSRF protection,
  authenticated review creation and exact persisted readback.
- React production build succeeded.

The reports describe their scope. A local build or test result does not establish
a successful Docker build, GitHub Actions run or public deployment. Run the
included workflows and deployment steps in your account to obtain those results.

## CI and deployment

See [deploy/README.md](deploy/README.md). The default CI runs tests, builds images and captures genuine local browser
screenshots as a downloadable dealership-local-evidence artifact. Image publication and Kubernetes deployment require an explicit manual
workflow dispatch. The application uses no default production administrator password.

## Submission

Project title: **Best Cars: Full-Stack Dealership Review Platform**

Use your own public fork URL and actual deployment URL. Follow
[the 28-task checklist](docs/RUBRIC_CHECKLIST.md), taking the required screenshots
from the lab/deployment specified by your course. Capture the filled review form
before submission and the matching stored review afterward.

## Source and license

Based on https://github.com/ibm-developer-skills-network/xrwvm-fullstack_developer_capstone
at commit 6bf6c0a1d8dedb6d949c9878a99fafa33168319c.

Original course assets/data are retained. Application code, user management,
models, APIs, frontend, tests and delivery configuration were completed or
updated in this version. Apache-2.0 license: see LICENSE.
