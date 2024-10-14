# storage.py
import json

DATA_FILE = 'data.json'

def save_data(key, data):
    """Save data under the given key to a JSON file."""
    try:
        with open(DATA_FILE, 'r') as f:
            all_data = json.load(f)
    except FileNotFoundError:
        all_data = {}
    all_data[key] = data
    with open(DATA_FILE, 'w') as f:
        json.dump(all_data, f)

def load_data(key):
    """Load data for the given key from a JSON file."""
    try:
        with open(DATA_FILE, 'r') as f:
            all_data = json.load(f)
            return all_data.get(key)
    except FileNotFoundError:
        return None

def load_all_data():
    """Load all data from the JSON file."""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}