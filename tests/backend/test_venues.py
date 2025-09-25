from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from backend.config import Settings
from backend.main import create_app
from backend.rbac import Role


@pytest.fixture()
def app() -> TestClient:
    settings = Settings(database_url="sqlite+pysqlite:///:memory:")
    application = create_app(settings=settings)
    with TestClient(application) as client:
        yield client


def _register(
    client: TestClient,
    *,
    email: str,
    password: str,
    organization_name: str,
    organization_slug: str,
) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "organizationName": organization_name,
            "organizationSlug": organization_slug,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_venue_crud_cycle(app: TestClient) -> None:
    owner = _register(
        app,
        email="owner@example.com",
        password="Password123!",
        organization_name="Orbit",
        organization_slug="orbit",
    )

    create_response = app.post(
        "/api/v1/venues",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={"name": "  Studio Nova  ", "city": "Lyon"},
    )
    assert create_response.status_code == 201, create_response.text
    venue = create_response.json()
    assert venue["name"] == "Studio Nova"
    assert venue["city"] == "Lyon"

    detail_response = app.get(
        f"/api/v1/venues/{venue['id']}",
        headers={"X-Session-Token": owner["sessionToken"]},
    )
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == venue["id"]

    update_response = app.put(
        f"/api/v1/venues/{venue['id']}",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={"name": "Grande Salle", "country": "France", "capacity": 900},
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["name"] == "Grande Salle"
    assert updated["country"] == "France"
    assert updated["capacity"] == 900

    list_response = app.get(
        "/api/v1/venues",
        headers={"X-Session-Token": owner["sessionToken"]},
    )
    assert list_response.status_code == 200
    venues = list_response.json()
    assert len(venues) == 1
    assert venues[0]["id"] == venue["id"]

    delete_response = app.delete(
        f"/api/v1/venues/{venue['id']}",
        headers={"X-Session-Token": owner["sessionToken"]},
    )
    assert delete_response.status_code == 204

    empty_response = app.get(
        "/api/v1/venues",
        headers={"X-Session-Token": owner["sessionToken"]},
    )
    assert empty_response.status_code == 200
    assert empty_response.json() == []


def test_duplicate_name_conflict_and_cross_org_allowed(app: TestClient) -> None:
    owner_one = _register(
        app,
        email="alpha@example.com",
        password="Password123!",
        organization_name="Alpha Co",
        organization_slug="alpha",
    )

    owner_two = _register(
        app,
        email="beta@example.com",
        password="Password123!",
        organization_name="Beta Co",
        organization_slug="beta",
    )

    first = app.post(
        "/api/v1/venues",
        headers={"X-Session-Token": owner_one["sessionToken"]},
        json={"name": "Le Cube"},
    )
    assert first.status_code == 201

    conflict = app.post(
        "/api/v1/venues",
        headers={"X-Session-Token": owner_one["sessionToken"]},
        json={"name": "Le Cube"},
    )
    assert conflict.status_code == 409

    other_org = app.post(
        "/api/v1/venues",
        headers={"X-Session-Token": owner_two["sessionToken"]},
        json={"name": "Le Cube"},
    )
    assert other_org.status_code == 201


def test_viewer_permissions_on_venues(app: TestClient) -> None:
    owner = _register(
        app,
        email="lead@example.com",
        password="Password123!",
        organization_name="Gamma",
        organization_slug="gamma",
    )

    invitation = app.post(
        "/api/v1/auth/invitations",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={"email": "viewer@example.com", "role": Role.VIEWER.value},
    )
    assert invitation.status_code == 201
    token = invitation.json()["token"]

    acceptance = app.post(
        "/api/v1/auth/invitations/accept",
        json={
            "token": token,
            "email": "viewer@example.com",
            "password": "ViewerPass123!",
        },
    )
    assert acceptance.status_code == 200

    login = app.post(
        "/api/v1/auth/login",
        json={"email": "viewer@example.com", "password": "ViewerPass123!"},
    )
    assert login.status_code == 200
    viewer_session = login.json()["sessionToken"]

    forbidden = app.post(
        "/api/v1/venues",
        headers={"X-Session-Token": viewer_session},
        json={"name": "Lieu secret"},
    )
    assert forbidden.status_code == 403

    allowed = app.get(
        "/api/v1/venues",
        headers={"X-Session-Token": viewer_session},
    )
    assert allowed.status_code == 200
    assert allowed.json() == []
