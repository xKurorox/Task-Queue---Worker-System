# Task Queue & Worker System

A background job processing system built with FastAPI and Redis. Jobs are submitted via a REST API, queued in Redis, and processed asynchronously by a worker with retry logic and a dead letter queue.

## Features

- Submit jobs via REST API
- Asynchronous job processing via a background worker
- Job status tracking (pending, active, completed, failed)
- Automatic retries with exponential backoff (up to 3 attempts)
- Dead letter queue for permanently failed jobs
- Dashboard endpoint with live queue stats

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/jobs/submit` | Submit a new job |
| `GET` | `/jobs/{job_id}` | Get status of a specific job |
| `GET` | `/jobs/dashboard` | View queue stats and job counts |

## Setup

**1. Clone the repo and create a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

**2. Install dependencies**

```bash
pip install fastapi uvicorn redis sqlalchemy python-dotenv
```

**3. Create a `.env` file in the project root**

```
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite:///./jobs.db
```

**4. Start Redis**

```bash
# Docker
docker run -d -p 6379:6379 redis

# WSL
sudo service redis start
```

**5. Run the API server**

```bash
uvicorn app.main:app --reload
```

**6. Run the worker** (separate terminal)

```bash
python -m app.worker
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Usage Example

**Submit a job**

```bash
curl -X POST http://localhost:8000/jobs/submit \
  -H "Content-Type: application/json" \
  -d '{"job_type": "email", "job_payload": "hello world"}'
```

**Check job status**

```bash
curl http://localhost:8000/jobs/1
```

**View dashboard**

```bash
curl http://localhost:8000/jobs/dashboard
```

## Job Lifecycle

```
pending → active → completed
                 ↘ failed (retried up to 3x → dead letter queue)
```

## Running Tests

```bash
pytest app/test/test_api.py -v
```

## Tech Stack

- **FastAPI** — REST API and endpoint routing
- **Redis** — Job queue and dead letter queue
- **SQLAlchemy + SQLite** — Job persistence and status tracking
- **Pydantic** — Request and response validation
