FROM python:3.12-slim-bookworm
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=5050
EXPOSE 5050
RUN useradd --create-home service
USER service
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 app:app"]
