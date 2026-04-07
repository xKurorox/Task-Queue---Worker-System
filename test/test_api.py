from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
import pytest

# Test database - separate from your real one
test_engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=test_engine)

@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield

# Create all tables in the test database
Base.metadata.create_all(bind=test_engine)

# Override the get_db dependency to use test database
def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# TEST JOB SUBMITS

def test_job_submit():
    response = client.post("/jobs/submit", json= {"job_type": "test_job", "job_payload": "test_payload"})
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_submit_missing_job_type():
    response = client.post("/jobs/submit", json= {})
    assert response.status_code == 422

# TEST GET JOB

def test_get_status():
    response = client.post("/jobs/submit", json={"job_type": "test_job"})
    job_id = response.json()["job_id"]
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_status"] == "pending"

def test_get_status_full_response():
    response = client.post("/jobs/submit", json={"job_type": "test_job"})
    job_id = response.json()["job_id"]
    response = client.get(f"/jobs/{job_id}")
    assert "job_id" in response.json()
    assert "job_type" in response.json()
    assert "job_created_at" in response.json()

def test_job_not_found():
    response = client.get("/jobs/9999")
    assert response.status_code == 404 

# TEST DASHBOARD

def test_get_dashboard():
    response = client.get("/jobs/dashboard")
    assert response.status_code == 200
    assert "complete_count" in response.json()
    assert "pending_count" in response.json()
    assert "fail_count" in response.json()
    assert "active_count" in response.json()
    assert "queue_count" in response.json()
    assert "dead_letter_count" in response.json() 

def test_dashboard_counts():
    client.post("/jobs/submit", json= {"job_type": "test_job"})
    client.post("/jobs/submit", json= {"job_type": "test_job_2"})
    response = client.get("/jobs/dashboard")
    assert response.json()["pending_count"] == 2