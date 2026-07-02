from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_them_from_activity():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

    unregister_response = client.delete(f"/activities/{activity_name}/participants/{email}")
    assert unregister_response.status_code == 200

    updated_activities = client.get("/activities").json()
    assert email not in updated_activities[activity_name]["participants"]


def test_unregister_unknown_participant_returns_not_found():
    response = client.delete("/activities/Chess Club/participants/ghost@mergington.edu")
    assert response.status_code == 404
