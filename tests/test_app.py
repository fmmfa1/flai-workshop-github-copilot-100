"""Tests for the FastAPI extracurricular activities app."""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_contains_activity_details(self, client, reset_activities):
        """Test that activities contain required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Tennis%20Team/signup?email=alice@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "alice@mergington.edu" in data["message"]
        assert "Tennis Team" in data["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant."""
        client.post("/activities/Tennis%20Team/signup?email=alice@mergington.edu")
        
        response = client.get("/activities")
        activities = response.json()
        assert "alice@mergington.edu" in activities["Tennis Team"]["participants"]

    def test_signup_prevents_duplicate_registration(self, client, reset_activities):
        """Test that a student cannot register twice for the same activity."""
        # First signup should succeed
        response1 = client.post(
            "/activities/Tennis%20Team/signup?email=alice@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Tennis%20Team/signup?email=alice@mergington.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_for_nonexistent_activity(self, client, reset_activities):
        """Test that signup fails for a non-existent activity."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=alice@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_students(self, client, reset_activities):
        """Test that multiple students can sign up for the same activity."""
        client.post("/activities/Tennis%20Team/signup?email=alice@mergington.edu")
        client.post("/activities/Tennis%20Team/signup?email=bob@mergington.edu")
        
        response = client.get("/activities")
        activities = response.json()
        participants = activities["Tennis Team"]["participants"]
        assert "alice@mergington.edu" in participants
        assert "bob@mergington.edu" in participants
        assert len(participants) == 2


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        # First signup
        client.post("/activities/Tennis%20Team/signup?email=alice@mergington.edu")
        
        # Then unregister
        response = client.delete(
            "/activities/Tennis%20Team/unregister?email=alice@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant."""
        # Signup then unregister
        client.post("/activities/Tennis%20Team/signup?email=alice@mergington.edu")
        client.delete("/activities/Tennis%20Team/unregister?email=alice@mergington.edu")
        
        # Verify participant is removed
        response = client.get("/activities")
        activities = response.json()
        assert "alice@mergington.edu" not in activities["Tennis Team"]["participants"]

    def test_unregister_from_nonexistent_activity(self, client, reset_activities):
        """Test that unregister fails for a non-existent activity."""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=alice@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_nonregistered_student(self, client, reset_activities):
        """Test that unregister fails for a student not signed up."""
        response = client.delete(
            "/activities/Tennis%20Team/unregister?email=alice@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering a participant that was already signed up."""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify removal
        response = client.get("/activities")
        activities = response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects(self, client, reset_activities):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
