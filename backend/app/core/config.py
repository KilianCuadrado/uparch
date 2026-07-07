import os

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

DB_PATH = os.getenv("UPARCH_DB_PATH", os.path.join(BACKEND_DIR, "..", "uparch.db"))
UPLOAD_DIR = os.getenv("UPARCH_UPLOAD_DIR", os.path.join(BACKEND_DIR, "..", "uploads"))

SECRET_KEY = os.getenv(
    "UPARCH_SECRET_KEY", "dro1oXi-IIMg3mrB8zj7roN12nb4PUwV5D4XGgliS9Y"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("UPARCH_TOKEN_EXPIRE_HOURS", "24"))
