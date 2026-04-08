import redis
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read the Redis URL from the environment
redis_url = os.getenv("REDIS_URL")

# Create a single Redis client instance shared across the app
redis_client = redis.from_url(redis_url)
