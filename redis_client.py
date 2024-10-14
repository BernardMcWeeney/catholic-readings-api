# redis_client.py

import os
from redis import Redis

# Load Redis configuration from environment variables
REDIS_HOST = os.getenv('REDIS_HOST', 'srv-captain--redis-rate-limiter')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# Initialize Redis client
redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# Test Redis connection
try:
    redis_client.ping()
    print("Connected to Redis successfully!")
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    raise