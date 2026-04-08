from app.redis_client import redis_client
from datetime import datetime, timezone
import time
import json
from app.database import SessionLocal
from app.model import Job
import random

# Continuously poll the Redis queue for new jobs
while True:
    # Pop a job from the right end of the queue (oldest job first)
    current_job = redis_client.rpop("job_queue")

    if current_job:
        db = SessionLocal()

        # Deserialize the job JSON back into a dictionary
        dict_job = json.loads(current_job)

        # Find the matching job record in the database
        job_entry = db.query(Job).filter(dict_job["job_id"] == Job.job_id).first()

        # Mark the job as active and record when it started
        job_entry.job_status = "active"
        job_entry.job_start = datetime.now(timezone.utc)
        db.commit()

        try:
            # Simulate a 50% chance of failure for testing retry logic
            if random.random() < 0.5:
                raise Exception("Simulated failure")

            # Simulate job processing time
            time.sleep(2)

            # Mark the job as completed and record the finish time
            job_entry.job_status = "completed"
            job_entry.job_finish = datetime.now(timezone.utc)
            print(f"Completed job {dict_job['job_id']}")
            db.commit()

        except Exception as e:
            print(f"Job {dict_job['job_id']} failed: {e}")

            if job_entry.job_retries < 3:
                # Increment the retry counter and wait with exponential backoff before re-queuing
                job_entry.job_retries += 1
                time.sleep(2 ** job_entry.job_retries)  # 2s, 4s, 8s between retries
                print(f"Retrying job {dict_job['job_id']}, attempt {job_entry.job_retries}")
                db.commit()

                # Push the job back onto the queue to be retried
                redis_client.lpush("job_queue", current_job)
            else:
                # Max retries reached — move the job to the dead letter queue and mark it failed
                redis_client.lpush("dead_letter_queue", current_job)
                job_entry.job_status = "failed"
                job_entry.job_finish = datetime.now(timezone.utc)
                db.commit()

        db.close()

    else:
        # No jobs in the queue — wait before polling again
        print("No jobs, waiting...")
        time.sleep(2)
