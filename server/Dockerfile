FROM node:22-bookworm-slim AS frontend
WORKDIR /build/frontend
COPY server/frontend/package*.json ./
RUN npm ci
COPY server/frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/app/data/db.sqlite3
WORKDIR /app
COPY server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY server/ ./
COPY --from=frontend /build/frontend/build ./frontend/build
RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid 10001 --no-create-home appuser \
    && mkdir -p /app/data /app/staticfiles \
    && chmod +x /app/entrypoint.sh \
    && chown -R appuser:appuser /app
USER 10001:10001
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "djangoproj.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
