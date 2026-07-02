import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, get_default_activities


@pytest.fixture
def test_activities():
    """Fixture that provides a fresh copy of activities for each test."""
    return deepcopy(get_default_activities())


@pytest.fixture
def test_client(test_activities):
    """Fixture that provides a test client with isolated activity state."""
    # Set up isolated state
    app.state.activities = test_activities
    
    # Create and return test client
    client = TestClient(app)
    
    # Yield for the test to run
    yield client
    
    # Reset to default state after test
    app.state.activities = get_default_activities()
