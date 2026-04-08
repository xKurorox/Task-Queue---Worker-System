from fastapi import Depends, HTTPException, APIRouter
from app.database import get_db
from app.pydantic_models import JobCreate, JobResponse
from sqlalchemy.orm import Session
from app.model import Job
from app.redis_client import redis_client
import json

router = APIRouter()

# POST /jobs/submit — accepts a job from the client, saves it to the DB, and pushes it onto the Redis queue
@router.post("/jobs/submit")
def job_submit(job: JobCreate, db: Session = Depends(get_db)):
    # Create a new Job record in the database with status "pending"
    new_job = Job(job_type=job.job_type, job_payload=job.job_payload)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)  # Refresh to get the auto-generated job_id

    # Serialize the job data to JSON and push it to the front of the Redis queue
    job_data = {"job_id": new_job.job_id, "job_type": new_job.job_type, "job_payload": new_job.job_payload}
    job_json = json.dumps(job_data)
    redis_client.lpush("job_queue", job_json)

    return {"job_id": new_job.job_id}


# GET /jobs/dashboard — returns a count of jobs in each status and how many are in each Redis queue
@router.get("/jobs/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    completed_count = db.query(Job).filter(Job.job_status == "completed").count()
    pending_count = db.query(Job).filter(Job.job_status == "pending").count()
    fail_count = db.query(Job).filter(Job.job_status == "failed").count()
    active_count = db.query(Job).filter(Job.job_status == "active").count()
    queue_count = redis_client.llen("job_queue")             # Jobs waiting to be processed
    dead_letter_count = redis_client.llen("dead_letter_queue")  # Jobs that failed after all retries

    return {
        "complete_count": completed_count,
        "pending_count": pending_count,
        "fail_count": fail_count,
        "active_count": active_count,
        "queue_count": queue_count,
        "dead_letter_count": dead_letter_count
    }


# GET /jobs/{job_id} — looks up a single job by ID and returns its current status
@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_status(job_id: int, db: Session = Depends(get_db)):
    user_entry = db.query(Job).filter(job_id == Job.job_id).first()
    if user_entry:
        return user_entry
    else:
        # Return a 404 if no job with that ID exists
        raise HTTPException(status_code=404, detail="Could not find status of job")
