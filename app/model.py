from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime, timezone
from app.database import Base

# Job represents a single job entry stored in the database
class Job(Base):
    __tablename__ = "Jobs"  # Name of the table in the database

    job_id = Column(Integer, primary_key=True, index=True)          # Unique ID for each job
    job_type = Column(String, nullable=False)                        # Type of job (e.g. "email")
    job_status = Column(String, default="pending")                   # Current status: pending, active, completed, failed
    job_created_at = Column(DateTime, default=datetime.now(timezone.utc))  # When the job was submitted
    job_start = Column(DateTime, nullable=True)                      # When the worker started processing it
    job_finish = Column(DateTime, nullable=True)                     # When the worker finished (or failed)
    job_payload = Column(Text, nullable=True)                        # Optional data the job needs to run
    job_retries = Column(Integer, default=0)                         # Number of times the job has been retried
