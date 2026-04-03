from app.redis_client import redis_client
from datetime import datetime, timezone
import time
import json
from app.database import SessionLocal
from app.model import Job

while True:
    current_job = redis_client.rpop("job_queue")
    if current_job:
        db = SessionLocal()
        dict_job = json.loads(current_job)
        job_entry = db.query(Job).filter(dict_job["job_id"] == Job.job_id).first()
        job_entry.job_status = "active"
        job_entry.job_start = datetime.now(timezone.utc)
        db.commit()
        time.sleep(2)
        job_entry.job_status = "completed"
        job_entry.job_finish = datetime.now(timezone.utc)
        print(f"Completed job {dict_job['job_id']}")
        db.commit()
        db.close()
    else:
        print("No jobs, waiting...")
        time.sleep(2)