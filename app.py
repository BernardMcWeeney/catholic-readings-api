# app.py

from flask import Flask, jsonify
from scraper import (
    scrape_sunday_homily,
    scrape_daily_readings,
    scrape_sunday_readings,
    scrape_saint_of_the_day
)
from storage import update_data, get_data
from datetime import datetime

app = Flask(__name__)

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

@app.route('/api/sunday-homily', methods=['GET'])
def get_sunday_homily():
    data = get_data('sunday_homily')
    if not data or is_data_stale(data['date'], interval='weekly'):
        homily = scrape_sunday_homily()
        update_data('sunday_homily', homily)
    else:
        homily = data['value']
    return jsonify({'homily': homily})

@app.route('/api/daily-readings', methods=['GET'])
def get_daily_readings():
    data = get_data('daily_readings')
    if not data or is_data_stale(data['date'], interval='daily'):
        readings = scrape_daily_readings()
        update_data('daily_readings', readings)
    else:
        readings = data['value']
    return jsonify({'readings': readings})

@app.route('/api/daily-readings/irish', methods=['GET'])
def get_daily_readings_irish():
    data = get_data('daily_readings_irish')
    if not data or is_data_stale(data['date'], interval='daily'):
        readings = scrape_daily_readings(lang='ga')
        update_data('daily_readings_irish', readings)
    else:
        readings = data['value']
    return jsonify({'readings': readings})

@app.route('/api/sunday-readings', methods=['GET'])
def get_sunday_readings():
    data = get_data('sunday_readings')
    if not data or is_data_stale(data['date'], interval='weekly'):
        readings = scrape_sunday_readings()
        update_data('sunday_readings', readings)
    else:
        readings = data['value']
    return jsonify({'readings': readings})

@app.route('/api/sunday-readings/irish', methods=['GET'])
def get_sunday_readings_irish():
    data = get_data('sunday_readings_irish')
    if not data or is_data_stale(data['date'], interval='weekly'):
        readings = scrape_sunday_readings(lang='ga')
        update_data('sunday_readings_irish', readings)
    else:
        readings = data['value']
    return jsonify({'readings': readings})

@app.route('/api/saint-of-the-day', methods=['GET'])
def get_saint_of_the_day():
    data = get_data('saint_of_the_day')
    if not data or is_data_stale(data['date'], interval='daily'):
        saint = scrape_saint_of_the_day()
        update_data('saint_of_the_day', saint)
    else:
        saint = data['value']
    return jsonify({'saint': saint})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)