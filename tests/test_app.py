import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

# snapshot of initial activities state for resetting
INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict before each test."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_all():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # should include at least one known activity
    assert "Basketball" in data
    assert data["Basketball"]["description"] == "Learn basketball skills and play competitive games"


def test_signup_success():
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/Soccer/signup?email={email}")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    # verify participant added
    activities = client.get("/activities").json()
    assert email in activities["Soccer"]["participants"]


def test_signup_duplicate_fails():
    existing = "james@mergington.edu"
    response = client.post(f"/activities/Soccer/signup?email={existing}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_success():
    email = "sarah@mergington.edu"
    response = client.delete(f"/activities/Soccer/unregister?email={email}")
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]

    # verify removal
    activities = client.get("/activities").json()
    assert email not in activities["Soccer"]["participants"]


def test_unregister_not_signed_up():
    email = "not@here.edu"
    response = client.delete(f"/activities/Soccer/unregister?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_activity_not_found_on_signup():
    response = client.post(f"/activities/Nope/signup?email=test@x.com")
    assert response.status_code == 404


def test_activity_not_found_on_unregister():
    response = client.delete(f"/activities/Nope/unregister?email=test@x.com")
    assert response.status_code == 404
