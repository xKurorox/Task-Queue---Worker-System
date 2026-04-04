from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime, timezone
from app.database import Base

class Job(Base):
    __tablename__ = "Jobs"
    job_id = Column(Integer, primary_key= True, index= True)
    job_type = Column(String, nullable= False)
    job_status = Column(String, default= "Pending")
    job_created_at = Column(DateTime, default= datetime.now(timezone.utc))
    job_start = Column(DateTime, nullable= True)
    job_finish = Column(DateTime, nullable= True)
    job_payload = Column(Text, nullable= True)
    job_retries = Column(Integer, default= 0)