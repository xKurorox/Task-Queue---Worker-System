from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    job_type: str
    job_payload: Optional[str] = None

class JobResponse(BaseModel):
    job_id: int 
    job_type: str
    job_status: str
    job_start: Optional[datetime] 
    job_finish: Optional[datetime]
    job_created_at: Optional[datetime]
    class Config:
        from_attributes = True