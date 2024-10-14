# storage.py

import time
import json
from redis_client import redis_client  # Import redis_client from redis_client.py

def save_data(redis_client, key, data):
    """Save data under the given key to Redis with a timestamp."""
    content = {
        'content': data,
        'timestamp': time.time()
    }
    redis_client.set(key, json.dumps(content))

def load_data(redis_client, key):
    """Load data for the given key from Redis."""
    value = redis_client.get(key)
    if value:
        content = json.loads(value)
        return content['content']
    else:
        return None

def is_data_valid(redis_client, key, max_age_seconds):
    """Check if the data for the given key is valid (not older than max_age_seconds)."""
    value = redis_client.get(key)
    if value:
        content = json.loads(value)
        timestamp = content.get('timestamp', 0)
        age = time.time() - timestamp
        return age < max_age_seconds
    else:
        return False

def load_all_data(redis_client):
    """Load all data from Redis."""
    keys = redis_client.keys()
    data = {}
    for key in keys:
        content = load_data(redis_client, key)
        data[key] = content
    return data