"""Pruebas del CRUD de Tenants."""
from app.schemas.admin import AdminCreate
from app.services.admin_service import create_admin


def _login_superadmin(client, db_session):
    create_admin(
        db_session,
        AdminCreate(
            email="super@example.com", full_name="Super Admin",
            password="Sup3rSecret!", is_superadmin=True,
        ),
    )
    resp = client.post(
        "/api/v1/admin/auth/login",
        json={"email": "super@example.com", "password": "Sup3rSecret!"},
    )
    return resp.json()["access_token"]


def test_create_and_list_tenants(client, db_session):
    token = _login_superadmin(client, db_session)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        "/api/v1/tenants",
        json={
            "name": "Fisiolab Quito",
            "slug": "fisiolab-quito",
            "db_uri": "postgresql://user:pass@localhost:5432/fisiolab_quito",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["slug"] == "fisiolab-quito"

    list_resp = client.get("/api/v1/tenants", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_create_tenant_duplicate_slug_fails(client, db_session):
    token = _login_superadmin(client, db_session)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": "Fisiolab Quito",
        "slug": "fisiolab-quito",
        "db_uri": "postgresql://user:pass@localhost:5432/fisiolab_quito",
    }
    client.post("/api/v1/tenants", json=payload, headers=headers)
    dup_resp = client.post("/api/v1/tenants", json=payload, headers=headers)
    assert dup_resp.status_code == 409
