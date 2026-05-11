import os
import sys

# Ensure the backend package folder is on sys.path so imports work
# regardless of where pytest is invoked from.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient

# Try import from the local module first, fall back to package import
try:
    from main import app
except Exception:
    from backend.main import app


client = TestClient(app)


# Test de upload
def test_upload_file_without_auth():
    """Verificar que sin token no se puede subir"""
    response = client.post("/files/upload")
    assert response.status_code == 403  # Forbidden


def test_upload_file_with_auth():
    """Verificar que con token se puede subir"""
    # 1. Registrar usuario de test
    client.post("/auth/register", json={"username": "admin", "password": "1234"})

    # 2. Login
    login_response = client.post(
        "/auth/login", json={"username": "admin", "password": "1234"}
    )
    token = login_response.json()["access_token"]

    # 3. Crear archivo de test
    test_file_content = b"Este es un archivo de test"
    files = {"file": ("test.txt", test_file_content, "text/plain")}

    # 4. Subir archivo
    response = client.post(
        "/files/upload", files=files, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    assert "file_id" in response.json()


def test_list_files():
    """Verificar que se pueden listar archivos"""
    # Login
    login_response = client.post(
        "/auth/login", json={"username": "admin", "password": "1234"}
    )
    token = login_response.json()["access_token"]

    # Listar archivos
    response = client.get("/api/files", headers={"Authorization": f"Bearer {token}"})

    data = response.json()
    assert response.status_code == 200
    assert "archivos" in data
