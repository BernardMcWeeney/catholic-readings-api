# storage.py

import json
from datetime import datetime
import os

# Use the persistent data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DATA_FILE = os.path.join(DATA_DIR, 'data.json')

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def update_data(key, value):
    data = load_data()
    data[key] = {
        'value': value,
        'date': datetime.utcnow().isoformat()
    }
    save_data(data)

def get_data(key):
    data = load_data()
    return data.get(key)