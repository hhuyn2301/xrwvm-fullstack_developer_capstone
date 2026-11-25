# Run, build and deploy

These files provide executable deployment support. They do not claim that your account
has already run GitHub Actions or deployed an application.

## 1. Docker Compose

From the repository root, copy .env.example to .env. Generate two independent random
strings and put them in DJANGO_SECRET_KEY and WRITE_API_TOKEN. For example:

~~~bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
~~~

Keep .env local. Set DJANGO_ALLOWED_HOSTS to actual hostnames and
DJANGO_CSRF_TRUSTED_ORIGINS to complete origins including scheme/port where applicable.
For the Skills Network proxy, use the exact host/origin displayed by the lab.
DJANGO_SECURE_COOKIES defaults to 0 in Compose for localhost HTTP; set it to 1 for HTTPS.

~~~bash
docker compose up --build
~~~

| Service | Local address |
|---|---|
| Django + React | http://localhost:8000 |
| Express/Mongo API | http://localhost:3030 |
| Sentiment API | http://localhost:5050 |

Mongo and Django data use named volumes. The web entrypoint runs migrations, seeds cars
idempotently and collects static files. Create your admin account interactively:

~~~bash
docker compose exec web python manage.py createsuperuser --username root
~~~

No default administrator password is created. Mongo is internal to the Compose network.
Django submits reviews with the configured internal write token; public GET endpoints
remain available for rubric screenshots.

## 2. Your public GitHub fork and CI

Fork the official starter into your own GitHub account:
https://github.com/ibm-developer-skills-network/xrwvm-fullstack_developer_capstone

Copy completed project files into your clone, preserving its .git directory. Review,
commit and push the code to your fork. Do not commit .env, SQLite databases, credentials
or node_modules.

The Capstone CI workflow runs on main pushes, pull requests and manual dispatch.
It checks Django migrations/tests, builds React, runs Express tests, checks sentiment
Python syntax, validates Compose and builds all three application images. It then starts the real stack,
exercises the React UI and captures the actual browser desktop under Xvfb. Download the
resulting dealership-local-evidence artifact from the run. These localhost images remain
local validation evidence; they do not prove an IBM Cloud deployment.

For Task 23, open your fork → Actions → Capstone CI → successful run. Capture the actual
green run with repository/workflow/commit visible. A local test report or an image of the
workflow YAML does not show a successful GitHub run.

## 3. Optional GitHub Container Registry publication

In your fork, manually run Publish capstone images. It reruns CI and publishes three
images under these naming patterns:

~~~text
ghcr.io/<lowercase-owner>/<lowercase-repository>/web:<commit-sha>
ghcr.io/<lowercase-owner>/<lowercase-repository>/backend:<commit-sha>
ghcr.io/<lowercase-owner>/<lowercase-repository>/sentiment:<commit-sha>
~~~

Use paths from your actual successful run. The workflow authenticates with GITHUB_TOKEN
and gives package-write permission only to publishing jobs. Publishing is manual.

For external deployment, make the intended image packages public or configure an image
pull secret in the cluster. Use the immutable commit tag for reproducibility.

## 4. Sentiment service on IBM Code Engine

Use the Code Engine project supplied by the current lab. Follow the course's login and
project selection steps. Set SENTIMENT_IMAGE to the image you actually published:

~~~bash
ibmcloud ce application create   --name dealership-sentiment   --image "$SENTIMENT_IMAGE"   --port 5050   --env PORT=5050
ibmcloud ce application get --name dealership-sentiment
~~~

The registry image must be accessible to Code Engine. If the lab requires IBM Container
Registry, push the same image to the assigned IBM namespace and use that reference.

Open IBM's returned application URL and append:

~~~text
/analyze/I%20love%20the%20excellent%20service
~~~

Capture the actual JSON response with the deployed URL for Task 16. To have Django use
that deployed service, set SENTIMENT_ANALYZER_URL to its real base URL. The Kubernetes
renderer defaults to an internal sentiment service; change that environment value if
the lab requires the external Code Engine service.

## 5. Full app on an existing Kubernetes lab cluster

This deployment uses one Django replica, Mongo, Express, sentiment, and two persistent
volumes. The namespace must already exist with a default storage class and quota that
can provision two 1 GiB volumes.

Create a private file outside Git containing these two environment entries:

~~~text
DJANGO_SECRET_KEY=<your-generated-secret>
WRITE_API_TOKEN=<your-independent-generated-token>
~~~

Set DEPLOY_NAMESPACE to your assigned namespace and create its secret from the file:

~~~bash
kubectl -n "$DEPLOY_NAMESPACE" create secret generic dealership-secrets   --from-env-file=/path/to/your/private/dealership-secrets.env
~~~

Do not submit the secret file, kubeconfig or secret values as screenshots. Set the actual
images and public/lab origin, then apply:

~~~bash
export DEPLOY_NAMESPACE='your-assigned-namespace'
export WEB_IMAGE='your-real-web-image:commit-tag'
export BACKEND_IMAGE='your-real-backend-image:commit-tag'
export SENTIMENT_IMAGE='your-real-sentiment-image:commit-tag'
export PUBLIC_ORIGIN='https://your-real-lab-proxy-host'
bash deploy/apply_kubernetes.sh
~~~

For private images, create a registry pull secret and set IMAGE_PULL_SECRET to its name.
The script renders Kubernetes JSON, applies it and waits for actual rollouts, failing
on errors. For failures, inspect pod events and PVC status.

To expose the deployed service through the Skills Network port launcher:

~~~bash
kubectl -n "$DEPLOY_NAMESPACE" port-forward   service/dealership-web 8000:8000 --address 0.0.0.0
~~~

Use Launch App for port 8000 in that lab, or its actual ingress URL. The renderer creates
internal Services; it does not invent a public hostname or create ingress automatically.

Create the deployed admin account if needed:

~~~bash
kubectl -n "$DEPLOY_NAMESPACE" exec -it deployment/dealership-web --   python manage.py createsuperuser --username root
~~~

Submit the actual deployment origin for Task 24. Capture Tasks 25–28 through that same
origin; dealer/review page paths may differ.

## 6. Optional GitHub Actions deployment

Deploy capstone to Kubernetes is a manual workflow. It needs a capstone GitHub Environment
and its KUBECONFIG_BASE64 secret (a base64-encoded kubeconfig authorized for your cluster).
The namespace and dealership-secrets Kubernetes Secret must already exist.

Use successful immutable image tags and the actual public origin as inputs. The GitHub
runner must reach the cluster. Some shared lab clusters allow access only from the lab;
in that case run apply_kubernetes.sh in the lab instead.

The workflow applies manifests and checks real rollout status. No success is reported
until those commands run. Never include kubeconfig/secret values in the peer submission.

## Primary documentation

- https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images
- https://github.com/actions/setup-node
- https://github.com/actions/setup-python
- https://github.com/Azure/setup-kubectl
- https://cloud.ibm.com/docs/codeengine?topic=codeengine-deploy-app
- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

Source app: IBM starter commit 6bf6c0a1d8dedb6d949c9878a99fafa33168319c.
The current course lab determines assigned namespace, credentials, quota, registry,
project and public endpoint.
