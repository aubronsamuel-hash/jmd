from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.config import Settings
from backend.main import create_app
from backend.rbac import Role


@pytest.fixture()
def app() -> TestClient:
    settings = Settings(database_url="sqlite+pysqlite:///:memory:")
    application = create_app(settings=settings)
    with TestClient(application) as client:
        yield client


def test_health_endpoint(app: TestClient) -> None:
    response = app.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
    payload = response.json()
    assert payload["userId"]
    assert payload["organizationId"]
    assert payload["sessionToken"]
    return payload


def test_register_and_login_flow(app: TestClient) -> None:
    register_payload = _register(
        app,
        email="alice@example.com",
        password="Password123!",
        organization_name="Acme",
        organization_slug="acme",
    )

    login_response = app.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "Password123!"},
    )
    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert login_payload["organizationId"] == register_payload["organizationId"]
    assert login_payload["role"] == Role.OWNER.value


def test_login_rejects_invalid_password(app: TestClient) -> None:
    _register(
        app,
        email="bob@example.com",
        password="SecurePass123!",
        organization_name="Bravo",
        organization_slug="bravo",
    )

    response = app.post(
        "/api/v1/auth/login",
        json={"email": "bob@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_magic_link_cycle(app: TestClient) -> None:
    register_payload = _register(
        app,
        email="carol@example.com",
        password="Password123!",
        organization_name="Charlie",
        organization_slug="charlie",
    )

    magic_link_response = app.post(
        "/api/v1/auth/magic-link",
        json={"email": "carol@example.com"},
    )
    assert magic_link_response.status_code == 201
    magic_data = magic_link_response.json()
    assert magic_data["organizationId"] == register_payload["organizationId"]

    verify_response = app.post(
        "/api/v1/auth/magic-link/verify",
        json={"token": magic_data["token"]},
    )
    assert verify_response.status_code == 200
    verified = verify_response.json()
    assert verified["organizationId"] == register_payload["organizationId"]


def test_invitation_acceptance_creates_new_user(app: TestClient) -> None:
    inviter_session = _register(
        app,
        email="dana@example.com",
        password="Password123!",
        organization_name="Delta",
        organization_slug="delta",
    )

    invitation_response = app.post(
        "/api/v1/auth/invitations",
        headers={"X-Session-Token": inviter_session["sessionToken"]},
        json={"email": "erin@example.com", "role": Role.MEMBER.value},
    )
    assert invitation_response.status_code == 201
    invitation_data = invitation_response.json()

    acceptance_response = app.post(
        "/api/v1/auth/invitations/accept",
        json={
            "token": invitation_data["token"],
            "email": "erin@example.com",
            "password": "AnotherPass123!",
        },
    )
    assert acceptance_response.status_code == 200
    acceptance_payload = acceptance_response.json()
    assert acceptance_payload["organizationId"] == inviter_session["organizationId"]
    assert acceptance_payload["role"] == Role.MEMBER.value

    login_response = app.post(
        "/api/v1/auth/login",
        json={"email": "erin@example.com", "password": "AnotherPass123!"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["organizationId"] == inviter_session["organizationId"]


def test_switch_organization_flow(app: TestClient) -> None:
    owner_one = _register(
        app,
        email="frank@example.com",
        password="Password123!",
        organization_name="Foxtrot",
        organization_slug="foxtrot",
    )

    owner_two = _register(
        app,
        email="grace@example.com",
        password="Password123!",
        organization_name="Golf",
        organization_slug="golf",
    )

    invitation = app.post(
        "/api/v1/auth/invitations",
        headers={"X-Session-Token": owner_two["sessionToken"]},
        json={"email": "frank@example.com", "role": Role.ADMIN.value},
    ).json()

    acceptance = app.post(
        "/api/v1/auth/invitations/accept",
        json={
            "token": invitation["token"],
            "email": "frank@example.com",
            "password": "Password123!",
        },
    )
    assert acceptance.status_code == 200
    org_two_id = acceptance.json()["organizationId"]

    login = app.post(
        "/api/v1/auth/login",
        json={"email": "frank@example.com", "password": "Password123!"},
    )
    assert login.status_code == 200
    login_payload = login.json()

    switch_response = app.post(
        "/api/v1/auth/switch",
        headers={"X-Session-Token": login_payload["sessionToken"]},
        json={"organizationId": org_two_id},
    )
    assert switch_response.status_code == 200
    switched = switch_response.json()
    assert switched["organizationId"] == org_two_id
    assert switched["role"] == Role.ADMIN.value

    # ensure old session cannot be reused
    forbidden = app.post(
        "/api/v1/auth/switch",
        headers={"X-Session-Token": login_payload["sessionToken"]},
        json={"organizationId": login_payload["organizationId"]},
    )
    assert forbidden.status_code == 401
    assert forbidden.json()["detail"] in {"Session revoked", "Session expired"}
