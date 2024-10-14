# app.py
from flask import Flask, jsonify, abort, url_for, render_template, request
from storage import load_data, load_all_data, save_data, is_data_valid
from scraper import scrape_content, URLS
import time

app = Flask(__name__)

# Maximum age for data in seconds (e.g., 1 day)
MAX_DATA_AGE = 24 * 60 * 60  # 1 day in seconds

# API Keys (simple example)
API_KEYS = {'your_api_key_here'}  # Replace 'your_api_key_here' with actual API keys

# Import for Rate Limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
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
    
    return render_template('index.html', endpoints=endpoints)

@app.route('/api/v1/content', methods=['GET'])
@limiter.limit("50 per hour")
def get_content_keys():
    """Get the list of available content keys."""
    api_key = request.args.get('api_key')
    if not api_key or api_key not in API_KEYS:
        abort(401, description="Unauthorized: Valid API key required.")
    
    keys = list(URLS.keys())
    return jsonify({'keys': keys}), 200

@app.route('/api/v1/content/<string:key>', methods=['GET'])
@limiter.limit("50 per hour")
def get_content(key):
    """Get the content for a given key, triggering a scrape if necessary."""
    api_key = request.args.get('api_key')
    if not api_key or api_key not in API_KEYS:
        abort(401, description="Unauthorized: Valid API key required.")
    
    # Check if the key is valid
    if key not in URLS:
        abort(404, description=f"Invalid key '{key}'. Use /api/v1/content to see available keys.")
    
    # Check if the data is valid
    if not is_data_valid(key, MAX_DATA_AGE):
        # Data is missing or outdated; trigger scraping
        content = scrape_content(key)
        if content:
            save_data(key, content)
        else:
            abort(500, description=f"Failed to scrape content for key '{key}'")
    else:
        data = load_data(key)
        content = data['content']
    
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
    app.run(debug=True)