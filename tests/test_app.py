import pytest
from urllib.parse import quote


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, test_client):
        """Test that GET /activities returns all activities."""
        response = test_client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert len(activities) >= 9

    def test_activity_has_required_fields(self, test_client):
        """Test that each activity has all required fields."""
        response = test_client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_activities_have_participants(self, test_client):
        """Test that default activities have initial participants."""
        response = test_client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, test_client):
        """Test successful signup for an activity."""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        response = test_client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_adds_participant_to_activity(self, test_client):
        """Test that signup actually adds the participant to the activity."""
        activity_name = "Chess Club"
        email = "alice@mergington.edu"
        
        # Verify not yet signed up
        activities = test_client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]
        
        # Sign up
        test_client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify signed up
        activities = test_client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, test_client):
        """Test that signing up for a non-existent activity returns 404."""
        response = test_client.post("/activities/Fake Club/signup?email=test@mergington.edu")
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_returns_400(self, test_client):
        """Test that signing up twice for the same activity returns 400."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Try to sign up someone already signed up
        response = test_client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_increases_participant_count(self, test_client):
        """Test that signup increases the participant count."""
        activity_name = "Programming Class"
        initial_response = test_client.get("/activities").json()
        initial_count = len(initial_response[activity_name]["participants"])
        
        # Sign up new participant
        test_client.post(f"/activities/{activity_name}/signup?email=bob@mergington.edu")
        
        final_response = test_client.get("/activities").json()
        final_count = len(final_response[activity_name]["participants"])
        
        assert final_count == initial_count + 1

    def test_signup_with_url_encoding(self, test_client):
        """Test signup with special characters in email (URL encoded)."""
        activity_name = "Chess Club"
        email = "test+special@mergington.edu"
        encoded_email = quote(email, safe="")
        
        response = test_client.post(
            f"/activities/{activity_name}/signup?email={encoded_email}"
        )
        
        assert response.status_code == 200
        activities = test_client.get("/activities").json()
        assert email in activities[activity_name]["participants"]


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_unregister_success(self, test_client):
        """Test successful unregistration from an activity."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        response = test_client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["message"] == f"Removed {email} from {activity_name}"

    def test_unregister_removes_participant(self, test_client):
        """Test that unregister actually removes the participant."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Verify participant exists
        activities = test_client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
        
        # Unregister
        test_client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Verify removed
        activities = test_client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_participant_returns_404(self, test_client):
        """Test that unregistering a non-existent participant returns 404."""
        response = test_client.delete(
            "/activities/Chess Club/participants/ghost@mergington.edu"
        )
        
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity_returns_404(self, test_client):
        """Test that unregistering from a non-existent activity returns 404."""
        response = test_client.delete(
            "/activities/Fake Club/participants/test@mergington.edu"
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_decreases_participant_count(self, test_client):
        """Test that unregister decreases the participant count."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        initial_response = test_client.get("/activities").json()
        initial_count = len(initial_response[activity_name]["participants"])
        
        # Unregister
        test_client.delete(f"/activities/{activity_name}/participants/{email}")
        
        final_response = test_client.get("/activities").json()
        final_count = len(final_response[activity_name]["participants"])
        
        assert final_count == initial_count - 1

    def test_unregister_with_url_encoding(self, test_client):
        """Test unregister with special characters in email (URL encoded)."""
        activity_name = "Chess Club"
        email = "test+special@mergington.edu"
        encoded_email = quote(email, safe="")
        
        # First sign them up
        test_client.post(f"/activities/{activity_name}/signup?email={encoded_email}")
        
        # Then unregister
        response = test_client.delete(
            f"/activities/{activity_name}/participants/{encoded_email}"
        )
        
        assert response.status_code == 200
        activities = test_client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flows."""

    def test_signup_then_unregister_flow(self, test_client):
        """Test the full flow of signing up and then unregistering."""
        activity_name = "Art Workshop"
        email = "charlie@mergington.edu"
        
        # Sign up
        signup_response = test_client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup worked
        activities = test_client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
        
        # Unregister
        unregister_response = test_client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister worked
        activities = test_client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]

    def test_multiple_signups_and_unregisters(self, test_client):
        """Test multiple participants signing up and unregistering."""
        activity_name = "Drama Club"
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        
        # Sign up all participants
        for email in emails:
            response = test_client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all signed up
        activities = test_client.get("/activities").json()
        for email in emails:
            assert email in activities[activity_name]["participants"]
        
        # Unregister first participant
        test_client.delete(f"/activities/{activity_name}/participants/{emails[0]}")
        
        # Verify only first was removed
        activities = test_client.get("/activities").json()
        assert emails[0] not in activities[activity_name]["participants"]
        assert emails[1] in activities[activity_name]["participants"]
        assert emails[2] in activities[activity_name]["participants"]
