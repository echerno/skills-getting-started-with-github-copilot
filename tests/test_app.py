import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": [],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app), activities


def test_get_activities_returns_activity_data(client):
    # Arrange
    test_client, activities = client

    # Act
    response = test_client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(client):
    # Arrange
    test_client, activities = client
    email = "student@example.edu"

    # Act
    response = test_client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert activities["Chess Club"]["participants"] == [email]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    test_client, _ = client

    # Act
    response = test_client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    test_client, activities = client
    email = "student@example.edu"
    activities["Chess Club"]["participants"].append(email)

    # Act
    response = test_client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activities["Chess Club"]["participants"] == [email]


def test_unregister_removes_participant(client):
    # Arrange
    test_client, activities = client
    email = "student@example.edu"
    activities["Chess Club"]["participants"].append(email)

    # Act
    response = test_client.delete(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    assert activities["Chess Club"]["participants"] == []


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    test_client, _ = client

    # Act
    response = test_client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unregistered_participant(client):
    # Arrange
    test_client, activities = client

    # Act
    response = test_client.delete(
        "/activities/Chess Club/signup",
        params={"email": "student@example.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activities["Chess Club"]["participants"] == []
