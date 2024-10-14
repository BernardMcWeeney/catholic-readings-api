# storage.py
import json
import time
import os

DATA_FILE = 'data.json'

def save_data(key, data):
    """Save data under the given key to a JSON file with a timestamp."""
    try:
        with open(DATA_FILE, 'r') as f:
            all_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_data = {}
    all_data[key] = {
        'content': data,
        'timestamp': time.time()
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(all_data, f)

def load_data(key):
    """Load data for the given key from a JSON file."""
    if not os.path.exists(DATA_FILE):
        return None
    try:
        with open(DATA_FILE, 'r') as f:
            all_data = json.load(f)
            return all_data.get(key)
    except json.JSONDecodeError:
        return None

def load_all_data():
    """Load all data from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def is_data_valid(key, max_age_seconds):
    """Check if the data for the given key is valid (not older than max_age_seconds)."""
    data = load_data(key)
    if not data:
        return False
    timestamp = data.get('timestamp', 0)
    age = time.time() - timestamp
    return age < max_age_seconds