import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://lspd:lspd@localhost:5432/lspd_test")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_admin_cannot_self_register():
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Bad Admin",
            "email": "badadmin@example.com",
            "phone": "9999999999",
            "password": "StrongPass@123",
            "city": "Bhopal",
            "district": "Bhopal",
            "role": "admin",
        },
    )
    assert response.status_code == 403


def test_protected_admin_requires_auth():
    response = client.get("/api/admin/dashboard")
    assert response.status_code in {401, 403}
