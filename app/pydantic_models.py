from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Schema for the request body when submitting a new job
class JobCreate(BaseModel):
    job_type: str                    # Required: type of job (e.g. "email", "report")
    job_payload: Optional[str] = None  # Optional: any extra data the job needs

# Schema for the response when fetching a job's status
class JobResponse(BaseModel):
    job_id: int
    job_type: str
    job_status: str
    job_start: Optional[datetime]      # None if the job hasn't started yet
    job_finish: Optional[datetime]     # None if the job hasn't finished yet
    job_created_at: Optional[datetime]

    class Config:
        from_attributes = True  # Allows Pydantic to read data from SQLAlchemy model objects
