"""Create local configuration without overwriting an existing .env."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
path = root / ".env"
if path.exists():
    raise SystemExit(".env already exists; kept unchanged.")
content = (
    "DJANGO_SECRET_KEY=" + secrets.token_urlsafe(48) + "\n"
    "WRITE_API_TOKEN=" + secrets.token_urlsafe(32) + "\n"
    "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1\n"
    "DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000\n"
    "DJANGO_SECURE_COOKIES=0\n"
)
path.write_text(content, encoding="utf-8")
path.chmod(0o600)
print("Created .env with fresh local secrets. Do not commit this file.")
