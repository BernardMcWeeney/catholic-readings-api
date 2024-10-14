# app.py
from flask import Flask, jsonify, abort
from storage import load_data, load_all_data
import json

app = Flask(__name__)

@app.route('/api/v1/content', methods=['GET'])
def get_content_keys():
    """Get the list of available content keys."""
    all_data = load_all_data()
    keys = list(all_data.keys())
    return jsonify({'keys': keys}), 200

@app.route('/api/v1/content/<string:key>', methods=['GET'])
def get_content(key):
    """Get the content for a given key."""
    data = load_data(key)
    if data:
        return jsonify(data), 200
    else:
        abort(404, description=f"Content not found for key '{key}'")

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

if __name__ == '__main__':
    app.run(debug=True)