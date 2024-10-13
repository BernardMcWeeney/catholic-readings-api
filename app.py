# app.py

from flask import Flask, jsonify, request, url_for
from flask_restful import Resource, Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from scraper import (
    scrape_sunday_homily,
    scrape_daily_readings,
    scrape_sunday_readings,
    scrape_saint_of_the_day
)
from storage import update_data, get_data
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
api = Api(app)

# Initialize Limiter for rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

def is_data_stale(data_date, interval='daily'):
    now = datetime.utcnow()
    data_datetime = datetime.fromisoformat(data_date)

    if interval == 'daily':
        return now.date() > data_datetime.date()
    elif interval == 'weekly':
        # Check if it's a new week or year
        current_week = now.isocalendar()[1]
        data_week = data_datetime.isocalendar()[1]
        return current_week > data_week or now.year > data_datetime.year
    else:
        # Default to data being stale
        return True

class SundayHomily(Resource):
    decorators = [limiter.limit("60 per hour")]

    def get(self):
        data = get_data('sunday_homily')
        if not data or is_data_stale(data['date'], interval='weekly'):
            homily = scrape_sunday_homily()
            if homily:
                update_data('sunday_homily', homily)
            else:
                return {'error': 'Unable to fetch Sunday Homily at this time.'}, 503
        else:
            homily = data['value']
        return {'homily': homily}

class DailyReadings(Resource):
    decorators = [limiter.limit("60 per hour")]

    def get(self):
        lang = request.args.get('lang', 'en')
        if lang not in ['en', 'ga']:
            return {'error': 'Invalid language code. Use "en" for English or "ga" for Irish.'}, 400

        key = 'daily_readings' if lang == 'en' else 'daily_readings_irish'
        data = get_data(key)
        if not data or is_data_stale(data['date'], interval='daily'):
            readings = scrape_daily_readings(lang=lang)
            if readings:
                update_data(key, readings)
            else:
                return {'error': 'Unable to fetch Daily Readings at this time.'}, 503
        else:
            readings = data['value']
        return {'readings': readings}

class SundayReadings(Resource):
    decorators = [limiter.limit("60 per hour")]

    def get(self):
        lang = request.args.get('lang', 'en')
        if lang not in ['en', 'ga']:
            return {'error': 'Invalid language code. Use "en" for English or "ga" for Irish.'}, 400

        key = 'sunday_readings' if lang == 'en' else 'sunday_readings_irish'
        data = get_data(key)
        if not data or is_data_stale(data['date'], interval='weekly'):
            readings = scrape_sunday_readings(lang=lang)
            if readings:
                update_data(key, readings)
            else:
                return {'error': 'Unable to fetch Sunday Readings at this time.'}, 503
        else:
            readings = data['value']
        return {'readings': readings}

class SaintOfTheDay(Resource):
    decorators = [limiter.limit("60 per hour")]

    def get(self):
        data = get_data('saint_of_the_day')
        if not data or is_data_stale(data['date'], interval='daily'):
            saint = scrape_saint_of_the_day()
            if saint:
                update_data('saint_of_the_day', saint)
            else:
                return {'error': 'Unable to fetch Saint of the Day at this time.'}, 503
        else:
            saint = data['value']
        return {'saint': saint}

class Root(Resource):
    def get(self):
        endpoints = {
            'sunday_homily': {
                'url': url_for('sundayhomily', _external=True),
                'methods': ['GET'],
                'description': 'Get the Sunday Homily.'
            },
            'daily_readings': {
                'url': url_for('dailyreadings', _external=True),
                'methods': ['GET'],
                'description': 'Get the Daily Readings.',
                'params': {
                    'lang': {
                        'type': 'string',
                        'description': 'Language code ("en" for English, "ga" for Irish).',
                        'default': 'en'
                    }
                }
            },
            'sunday_readings': {
                'url': url_for('sundayreadings', _external=True),
                'methods': ['GET'],
                'description': 'Get the Sunday Readings.',
                'params': {
                    'lang': {
                        'type': 'string',
                        'description': 'Language code ("en" for English, "ga" for Irish).',
                        'default': 'en'
                    }
                }
            },
            'saint_of_the_day': {
                'url': url_for('saintoftheday', _external=True),
                'methods': ['GET'],
                'description': 'Get information about the Saint of the Day.'
            }
        }
        return {'api_endpoints': endpoints}

# Registering resources with endpoints
api.add_resource(Root, '/')
api.add_resource(SundayHomily, '/api/sunday-homily')
api.add_resource(DailyReadings, '/api/daily-readings')
api.add_resource(SundayReadings, '/api/sunday-readings')
api.add_resource(SaintOfTheDay, '/api/saint-of-the-day')

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)