import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Helper to reset activities state for each test (since it's in-memory)
@pytest.fixture(autouse=True)
def reset_activities():
    # Deep copy the original state for each test
    import copy
    orig = copy.deepcopy({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })
    activities.clear()
    activities.update(copy.deepcopy(orig))
    yield

# --- GET /activities ---
def test_get_activities():
    # Arrange: (nothing needed, uses fixture)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12

# --- POST /activities/{activity_name}/signup ---
def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    # Act
    response = client.post("/activities/Chess%20Club/signup?email=" + email)
    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate():
    # Arrange
    email = "michael@mergington.edu"
    # Act
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_not_found():
    # Arrange
    email = "someone@mergington.edu"
    # Act
    response = client.post(f"/activities/Nonexistent/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

# --- POST /activities/{activity_name}/unregister ---
def test_unregister_success():
    # Arrange
    email = "michael@mergington.edu"
    # Act
    response = client.post(f"/activities/Chess%20Club/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_not_registered():
    # Arrange
    email = "notregistered@mergington.edu"
    # Act
    response = client.post(f"/activities/Chess%20Club/unregister?email={email}")
    # Assert
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_unregister_activity_not_found():
    # Arrange
    email = "someone@mergington.edu"
    # Act
    response = client.post(f"/activities/Nonexistent/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
