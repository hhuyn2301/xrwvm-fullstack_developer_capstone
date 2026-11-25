#!/usr/bin/env bash
set -Eeuo pipefail
: "${DEPLOY_NAMESPACE:?Set DEPLOY_NAMESPACE}"
: "${WEB_IMAGE:?Set WEB_IMAGE}"
: "${BACKEND_IMAGE:?Set BACKEND_IMAGE}"
: "${SENTIMENT_IMAGE:?Set SENTIMENT_IMAGE}"
: "${PUBLIC_ORIGIN:?Set PUBLIC_ORIGIN}"
DEPLOY_SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
kubectl -n "$DEPLOY_NAMESPACE" get secret dealership-secrets -o name
DEPLOY_MANIFEST="$(mktemp)"
trap 'rm -f "$DEPLOY_MANIFEST"' EXIT
python3 "$DEPLOY_SCRIPT_DIR/render_kubernetes.py" > "$DEPLOY_MANIFEST"
kubectl -n "$DEPLOY_NAMESPACE" apply -f "$DEPLOY_MANIFEST"
for DEPLOY_COMPONENT in mongo backend sentiment web; do
  kubectl -n "$DEPLOY_NAMESPACE" rollout status "deployment/dealership-$DEPLOY_COMPONENT" --timeout=300s
done
kubectl -n "$DEPLOY_NAMESPACE" get deployments,services,pvc -l app.kubernetes.io/part-of=dealership
