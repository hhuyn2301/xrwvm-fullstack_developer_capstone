"""Render Kubernetes objects as JSON without requiring extra Python packages."""
import json
import os
import re
from urllib.parse import urlsplit

namespace = os.environ["DEPLOY_NAMESPACE"]
if not re.fullmatch(r"[a-z0-9](?:[-a-z0-9]*[a-z0-9])?", namespace):
    raise SystemExit("Invalid Kubernetes namespace")
origin = os.environ["PUBLIC_ORIGIN"].rstrip("/")
url = urlsplit(origin)
if url.scheme not in {"http", "https"} or not url.hostname or url.path or url.query or url.fragment or url.username:
    raise SystemExit("PUBLIC_ORIGIN must be a plain http(s) origin")
images = {}
for component in ("web", "backend", "sentiment"):
    image = os.environ[component.upper() + "_IMAGE"]
    if not image or any(c.isspace() for c in image):
        raise SystemExit("Invalid image reference")
    images[component] = image
labels = {"app.kubernetes.io/part-of": "dealership"}
objects = []

def env(name, value):
    return {"name": name, "value": value}

def secret(name, key):
    return {"name": name, "valueFrom": {"secretKeyRef": {"name": "dealership-secrets", "key": key}}}

for volume in ("mongo", "django"):
    objects.append({
        "apiVersion": "v1", "kind": "PersistentVolumeClaim",
        "metadata": {"name": "dealership-" + volume, "namespace": namespace, "labels": labels},
        "spec": {"accessModes": ["ReadWriteOnce"], "resources": {"requests": {"storage": "1Gi"}}},
    })

configs = {
    "mongo": {
        "image": "mongo:7", "port": 27017,
        "mount": ("dealership-mongo", "/data/db"),
        "resources": {"requests": {"cpu": "100m", "memory": "256Mi"}, "limits": {"cpu": "500m", "memory": "768Mi"}},
    },
    "backend": {
        "image": images["backend"], "port": 3030,
        "env": [env("MONGODB_URI", "mongodb://dealership-mongo:27017/dealershipsDB"), env("PORT", "3030"), secret("WRITE_API_TOKEN", "WRITE_API_TOKEN")],
        "resources": {"requests": {"cpu": "50m", "memory": "96Mi"}, "limits": {"cpu": "500m", "memory": "256Mi"}},
    },
    "sentiment": {
        "image": images["sentiment"], "port": 5050,
        "env": [env("PORT", "5050")],
        "resources": {"requests": {"cpu": "50m", "memory": "128Mi"}, "limits": {"cpu": "500m", "memory": "384Mi"}},
    },
    "web": {
        "image": images["web"], "port": 8000,
        "mount": ("dealership-django", "/app/data"),
        "env": [
            env("DJANGO_DEBUG", "0"), env("DJANGO_SECURE_COOKIES", "1" if url.scheme == "https" else "0"), secret("DJANGO_SECRET_KEY", "DJANGO_SECRET_KEY"),
            env("DJANGO_ALLOWED_HOSTS", url.hostname + ",localhost,127.0.0.1"),
            env("DJANGO_CSRF_TRUSTED_ORIGINS", origin),
            env("DB_PATH", "/app/data/db.sqlite3"),
            env("BACKEND_URL", "http://dealership-backend:3030"),
            env("SENTIMENT_ANALYZER_URL", "http://dealership-sentiment:5050"),
            secret("BACKEND_WRITE_API_TOKEN", "WRITE_API_TOKEN"),
        ],
        "resources": {"requests": {"cpu": "100m", "memory": "128Mi"}, "limits": {"cpu": "1000m", "memory": "512Mi"}},
    },
}
for component, config in configs.items():
    name = "dealership-" + component
    selector = {"app": name}
    container = {
        "name": component, "image": config["image"],
        "ports": [{"containerPort": config["port"]}],
        "env": config.get("env", []), "resources": config["resources"],
    }
    pod = {"containers": [container]}
    if component != "mongo":
        container["readinessProbe"] = {"httpGet": {"path": "/health", "port": config["port"]}, "initialDelaySeconds": 10, "periodSeconds": 10, "failureThreshold": 12}
        if component == "web":
            container["readinessProbe"]["httpGet"]["httpHeaders"] = [{"name": "Host", "value": "localhost"}]
    if "mount" in config:
        claim, path = config["mount"]
        container["volumeMounts"] = [{"name": "data", "mountPath": path}]
        pod["volumes"] = [{"name": "data", "persistentVolumeClaim": {"claimName": claim}}]
    if component == "web":
        pod["securityContext"] = {"runAsUser": 10001, "runAsGroup": 10001, "fsGroup": 10001}
    pull_secret = os.environ.get("IMAGE_PULL_SECRET", "")
    if pull_secret and component != "mongo":
        pod["imagePullSecrets"] = [{"name": pull_secret}]
    objects.extend([
        {
            "apiVersion": "apps/v1", "kind": "Deployment",
            "metadata": {"name": name, "namespace": namespace, "labels": labels},
            "spec": {"replicas": 1, "strategy": {"type": "Recreate"},
                     "selector": {"matchLabels": selector},
                     "template": {"metadata": {"labels": {**selector, **labels}}, "spec": pod}},
        },
        {
            "apiVersion": "v1", "kind": "Service",
            "metadata": {"name": name, "namespace": namespace, "labels": labels},
            "spec": {"selector": selector, "ports": [{"port": config["port"], "targetPort": config["port"]}]},
        },
    ])
print(json.dumps({"apiVersion": "v1", "kind": "List", "items": objects}, indent=2))
