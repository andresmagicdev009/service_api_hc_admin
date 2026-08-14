"""Pruebas del flujo de autenticación de AdminUsers (login/refresh/logout)."""
from app.schemas.admin import AdminCreate
from app.services.admin_service import create_admin


def _create_test_admin(db_session):
    return create_admin(
        db_session,
        AdminCreate(email="admin@example.com", full_name="Admin Test", password="Sup3rSecret!"),
    )


def test_login_success(client, db_session):
    _create_test_admin(db_session)
    response = client.post(
        "/api/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "Sup3rSecret!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_wrong_password(client, db_session):
    _create_test_admin(db_session)
    response = client.post(
        "/api/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "incorrecta"},
    )
    assert response.status_code == 401


def test_refresh_token_flow(client, db_session):
    _create_test_admin(db_session)
    login_resp = client.post(
        "/api/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "Sup3rSecret!"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    refresh_resp = client.post("/api/v1/admin/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 200

    # El refresh token original ya fue rotado/revocado: reutilizarlo debe fallar
    reuse_resp = client.post("/api/v1/admin/auth/refresh", json={"refresh_token": refresh_token})
    assert reuse_resp.status_code == 401
