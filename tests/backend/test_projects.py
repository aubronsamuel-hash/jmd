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
    payload = response.json()
    assert payload["userId"]
    assert payload["organizationId"]
    assert payload["sessionToken"]
    return payload


def test_project_crud_flow(app: TestClient) -> None:
    owner = _register(
        app,
        email="owner@example.com",
        password="Password123!",
        organization_name="Orbit",
        organization_slug="orbit",
    )

    venue_response = app.post(
        "/api/v1/venues",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={"name": "Grand Theatre", "city": "Paris"},
    )
    assert venue_response.status_code == 201
    venue_data = venue_response.json()

    second_venue = app.post(
        "/api/v1/venues",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={"name": "Club Delta"},
    )
    assert second_venue.status_code == 201
    second_data = second_venue.json()

    project_response = app.post(
        "/api/v1/projects",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={
            "name": "Tournée Printemps",
            "description": "Concerts en tournée",
            "startDate": "2025-03-01",
            "endDate": "2025-05-01",
            "budgetCents": 25000000,
            "teamType": "Technique",
            "venueIds": [venue_data["id"]],
        },
    )
    assert project_response.status_code == 201, project_response.text
    project = project_response.json()
    assert project["name"] == "Tournée Printemps"
    assert len(project["venues"]) == 1
    assert project["venues"][0]["id"] == venue_data["id"]

    list_response = app.get(
        "/api/v1/projects",
        headers={"X-Session-Token": owner["sessionToken"]},
    )
    assert list_response.status_code == 200
    payload = list_response.json()
    assert len(payload) == 1

    update_response = app.put(
        f"/api/v1/projects/{project['id']}",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={
            "name": "Tournée Été",
            "budgetCents": 27500000,
            "venueIds": [venue_data["id"], second_data["id"]],
        },
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["name"] == "Tournée Été"
    assert updated["budgetCents"] == 27500000
    assert {venue["id"] for venue in updated["venues"]} == {venue_data["id"], second_data["id"]}

    delete_response = app.delete(
        f"/api/v1/projects/{project['id']}",
        headers={"X-Session-Token": owner["sessionToken"]},
    )
    assert delete_response.status_code == 204

    final_list = app.get(
        "/api/v1/projects",
        headers={"X-Session-Token": owner["sessionToken"]},
    )
    assert final_list.status_code == 200
    assert final_list.json() == []


def test_project_permissions(app: TestClient) -> None:
    owner = _register(
        app,
        email="leader@example.com",
        password="Password123!",
        organization_name="Nova",
        organization_slug="nova",
    )

    invitation = app.post(
        "/api/v1/auth/invitations",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={"email": "viewer@example.com", "role": Role.VIEWER.value},
    )
    assert invitation.status_code == 201
    invitation_token = invitation.json()["token"]

    acceptance = app.post(
        "/api/v1/auth/invitations/accept",
        json={
            "token": invitation_token,
            "email": "viewer@example.com",
            "password": "AnotherPass123!",
        },
    )
    assert acceptance.status_code == 200

    login = app.post(
        "/api/v1/auth/login",
        json={"email": "viewer@example.com", "password": "AnotherPass123!"},
    )
    assert login.status_code == 200
    viewer_session = login.json()["sessionToken"]

    forbidden = app.post(
        "/api/v1/projects",
        headers={"X-Session-Token": viewer_session},
        json={"name": "Projet interdit", "teamType": "Test"},
    )
    assert forbidden.status_code == 403

    allowed = app.get(
        "/api/v1/projects",
        headers={"X-Session-Token": viewer_session},
    )
    assert allowed.status_code == 200
    assert allowed.json() == []


def test_mission_template_flow(app: TestClient) -> None:
    owner = _register(
        app,
        email="rg@example.com",
        password="Password123!",
        organization_name="Regie",
        organization_slug="regie",
    )

    venue = app.post(
        "/api/v1/venues",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={"name": "Salle Polyvalente"},
    ).json()

    tag_one = app.post(
        "/api/v1/mission-tags",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={"slug": "lumiere", "label": "Lumière"},
    ).json()

    tag_update = app.put(
        f"/api/v1/mission-tags/{tag_one['id']}",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={"label": "Lumière principale"},
    )
    assert tag_update.status_code == 200
    tag_one = tag_update.json()

    tag_two = app.post(
        "/api/v1/mission-tags",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={"slug": "son", "label": "Son"},
    ).json()

    template_response = app.post(
        "/api/v1/mission-templates",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={
            "name": "Montage Lumière",
            "description": "Installation du kit lumière",
            "teamSize": 3,
            "requiredSkills": ["elec", "lumiere"],
            "defaultStartTime": "08:00:00",
            "defaultEndTime": "12:00:00",
            "defaultVenueId": venue["id"],
            "tagIds": [tag_one["id"], tag_two["id"]],
        },
    )
    assert template_response.status_code == 201, template_response.text
    template = template_response.json()
    assert template["defaultVenue"]["id"] == venue["id"]
    assert {tag["id"] for tag in template["tags"]} == {tag_one["id"], tag_two["id"]}

    list_templates = app.get(
        "/api/v1/mission-templates",
        headers={"X-Session-Token": owner["sessionToken"]},
    )
    assert list_templates.status_code == 200
    assert len(list_templates.json()) == 1

    update_template = app.put(
        f"/api/v1/mission-templates/{template['id']}",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={
            "teamSize": 4,
            "defaultEndTime": "13:30:00",
            "defaultVenueId": None,
            "tagIds": [tag_two["id"]],
        },
    )
    assert update_template.status_code == 200, update_template.text
    updated_template = update_template.json()
    assert updated_template["teamSize"] == 4
    assert updated_template["defaultVenue"] is None
    assert [tag["id"] for tag in updated_template["tags"]] == [tag_two["id"]]

    delete_template = app.delete(
        f"/api/v1/mission-templates/{template['id']}",
        headers={"X-Session-Token": owner["sessionToken"]},
    )
    assert delete_template.status_code == 204

    cleanup_tag = app.delete(
        f"/api/v1/mission-tags/{tag_two['id']}",
        headers={"X-Session-Token": owner["sessionToken"]},
    )
    assert cleanup_tag.status_code == 204

    tag_list = app.get(
        "/api/v1/mission-tags",
        headers={"X-Session-Token": owner["sessionToken"]},
    )
    assert tag_list.status_code == 200
    remaining_tags = tag_list.json()
    assert len(remaining_tags) == 1
    assert remaining_tags[0]["id"] == tag_one["id"]


def test_template_rejects_unknown_references(app: TestClient) -> None:
    owner = _register(
        app,
        email="check@example.com",
        password="Password123!",
        organization_name="Check",
        organization_slug="check",
    )

    bad_template = app.post(
        "/api/v1/mission-templates",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={
            "name": "Invalide",
            "teamSize": 2,
            "tagIds": ["non-existent"],
        },
    )
    assert bad_template.status_code == 404

    tag = app.post(
        "/api/v1/mission-tags",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={"slug": "plateau", "label": "Plateau"},
    ).json()

    bad_venue_template = app.post(
        "/api/v1/mission-templates",
        headers={"X-Session-Token": owner["sessionToken"]},
        json={
            "name": "Sans lieu",
            "teamSize": 2,
            "tagIds": [tag["id"]],
            "defaultVenueId": "unknown",
        },
    )
    assert bad_venue_template.status_code == 404
