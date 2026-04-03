from fastapi import Depends, HTTPException, APIRouter
from app.database import get_db
from app.pydantic_models import JobCreate, JobResponse
from sqlalchemy.orm import Session
from app.model import Job
from app.redis_client import redis_client
import json

router = APIRouter()

@router.post("/jobs/submit")
def job_submit(job: JobCreate, db: Session = Depends(get_db)):
    new_job = Job(job_type = job.job_type, job_payload = job.job_payload)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    job_data = {"job_id": new_job.job_id, "job_type": new_job.job_type, "job_payload": new_job.job_payload}
    job_json = json.dumps(job_data)
    redis_client.lpush("job_queue", job_json)
    return {"job_id": new_job.job_id}

@router.get("/jobs/{job_id}", response_model = JobResponse)
def get_status(job_id: int, db: Session = Depends(get_db)):
    user_entry = db.query(Job).filter(job_id == Job.job_id).first()
    if user_entry:
        return user_entry
    else:
        raise HTTPException(status_code= 404, detail= "Could not find status of job")
