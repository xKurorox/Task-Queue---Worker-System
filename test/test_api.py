from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
import pytest

# Use a separate test database so tests don't touch real data
test_engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=test_engine)

# autouse=True means this fixture runs automatically before every test
# It wipes and recreates all tables so each test starts with a clean database
@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=test_engine)   # Delete all tables
    Base.metadata.create_all(bind=test_engine)  # Recreate them fresh
    yield  # Run the test, then do nothing on teardown

# Create tables in the test database on module load
Base.metadata.create_all(bind=test_engine)

# Replace the real get_db dependency with one that uses the test database instead
def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

# Tell FastAPI to use the test database for all requests made during tests
app.dependency_overrides[get_db] = override_get_db

# TestClient lets us make HTTP requests to the app without running a real server
client = TestClient(app)


# --- JOB SUBMIT TESTS ---

# Happy path: submitting a valid job should return 200 and a job_id
def test_job_submit():
    response = client.post("/jobs/submit", json={"job_type": "test_job", "job_payload": "test_payload"})
    assert response.status_code == 200
    assert "job_id" in response.json()

# Missing required field: job_type is required, so an empty body should return 422 Unprocessable Entity
def test_submit_missing_job_type():
    response = client.post("/jobs/submit", json={})
    assert response.status_code == 422


# --- JOB STATUS TESTS ---

# Submit a job then fetch it — status should be "pending" since the worker hasn't touched it
def test_get_status():
    response = client.post("/jobs/submit", json={"job_type": "test_job"})
    job_id = response.json()["job_id"]
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_status"] == "pending"

# Check that the full response includes all expected fields
def test_get_status_full_response():
    response = client.post("/jobs/submit", json={"job_type": "test_job"})
    job_id = response.json()["job_id"]
    response = client.get(f"/jobs/{job_id}")
    assert "job_id" in response.json()
    assert "job_type" in response.json()
    assert "job_created_at" in response.json()

# Requesting a job ID that doesn't exist should return 404
def test_job_not_found():
    response = client.get("/jobs/9999")
    assert response.status_code == 404


# --- DASHBOARD TESTS ---

# Dashboard should return 200 and include all expected stat fields
def test_get_dashboard():
    response = client.get("/jobs/dashboard")
    assert response.status_code == 200
    assert "complete_count" in response.json()
    assert "pending_count" in response.json()
    assert "fail_count" in response.json()
    assert "active_count" in response.json()
    assert "queue_count" in response.json()
    assert "dead_letter_count" in response.json()

# Submit 2 jobs and confirm the dashboard pending count reflects them
def test_dashboard_counts():
    client.post("/jobs/submit", json={"job_type": "test_job"})
    client.post("/jobs/submit", json={"job_type": "test_job_2"})
    response = client.get("/jobs/dashboard")
    assert response.json()["pending_count"] == 2
