# app.py

import os
from flask import Flask, jsonify, abort, request, render_template, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis_client import redis_client
from scraper import scrape_content, URLS, scrape_mass_reading_details
from storage import load_data, save_data, is_data_valid
import time

app = Flask(__name__)

# Maximum age for data in seconds (e.g., 1 day)
MAX_DATA_AGE = 12 * 60 * 60  # 12 hours

# Load API keys from environment variable
API_KEYS = set(os.getenv('API_KEYS', '').split(','))
API_KEYS = {key.strip() for key in API_KEYS if key.strip()}
if not API_KEYS:
    raise ValueError("No API keys set. Please set the 'API_KEYS' environment variable.")

# Construct Redis URI for Limiter
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
REDIS_HOST = os.getenv('REDIS_HOST', 'srv-captain--redis-rate-limiter')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
if REDIS_PASSWORD:
    REDIS_URI = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
else:
    REDIS_URI = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

# Initialize Limiter with Redis storage
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri=REDIS_URI
)

# Error handler for rate limit errors
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Rate limit exceeded. Please try again later."), 429

# Root URL with HTML documentation
@app.route('/', methods=['GET'])
def api_documentation():
    """Render API documentation as HTML."""
    endpoints = []
    for key in URLS.keys():
        endpoint = {
            'key': key,
            'url': url_for('get_content', key=key, _external=True),
            'description': f'Get the {key.replace("_", " ")} content.',
            'example_request': f'GET {url_for("get_content", key=key, _external=True)}?api_key=YOUR_API_KEY',
        }
        endpoints.append(endpoint)
    
    # Add mass_reading_details endpoint
    endpoints.append({
        'key': 'mass_reading_details',
        'url': url_for('get_mass_reading_details', _external=True),
        'description': 'Get the mass reading details.',
        'example_request': f'GET {url_for("get_mass_reading_details", _external=True)}?api_key=YOUR_API_KEY',
    })
    
    return render_template('index.html', endpoints=endpoints)

@app.route('/api/v1/content', methods=['GET'])
@limiter.limit("50 per hour")
def get_content_keys():
    """Get the list of available content keys."""
    api_key = request.args.get('api_key')
    if not api_key or api_key not in API_KEYS:
        abort(401, description="Unauthorized: Valid API key required.")
    
    keys = list(URLS.keys()) + ['mass_reading_details']
    return jsonify({'keys': keys}), 200

@app.route('/api/v1/content/<string:key>', methods=['GET'])
@limiter.limit("50 per hour")
def get_content(key):
    """Get the content for a given key, triggering a scrape if necessary."""
    api_key = request.args.get('api_key')
    if not api_key or api_key not in API_KEYS:
        abort(401, description="Unauthorized: Valid API key required.")
    
    # Check if the key is valid
    if key not in URLS and key != 'mass_reading_details':
        abort(404, description=f"Invalid key '{key}'. Use /api/v1/content to see available keys.")
    
    # Handle mass_reading_details separately
    if key == 'mass_reading_details':
        return get_mass_reading_details()
    
    # Check if the data is valid
    if not is_data_valid(redis_client, key, MAX_DATA_AGE):
        # Data is missing or outdated; trigger scraping
        content = scrape_content(key)
        if content:
            save_data(redis_client, key, content)
        else:
            abort(500, description=f"Failed to scrape content for key '{key}'")
    else:
        content = load_data(redis_client, key)
    
    return jsonify({'content': content}), 200

@app.route('/api/v1/mass_reading_details', methods=['GET'])
@limiter.limit("50 per hour")
def get_mass_reading_details():
    """Get the mass reading details."""
    api_key = request.args.get('api_key')
    if not api_key or api_key not in API_KEYS:
        abort(401, description="Unauthorized: Valid API key required.")
    
    # Check if the data is valid
    if not is_data_valid(redis_client, 'mass_reading_details', MAX_DATA_AGE):
        # Data is missing or outdated; trigger scraping
        content = scrape_mass_reading_details()
        if content:
            save_data(redis_client, 'mass_reading_details', content)
        else:
            abort(500, description="Failed to scrape mass reading details")
    else:
        content = load_data(redis_client, 'mass_reading_details')
    
    return jsonify({'content': content}), 200

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e.description)), 404

@app.errorhandler(401)
def unauthorized(e):
    return jsonify(error=str(e.description)), 401

@app.errorhandler(500)
def internal_error(e):
    return jsonify(error=str(e.description)), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)