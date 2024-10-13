# scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; CatholicReadingsBot/1.0; +http://yourdomain.com/bot)'
}

def scrape_sunday_homily():
    try:
        url = 'https://www.catholicireland.net/sunday-homily/'
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        # Extract the homily content
        content_div = soup.find('div', class_='entry-content')
        if content_div:
            homily = content_div.get_text(separator='\n', strip=True)
            return homily
        else:
            logging.error('Homily content not found in the page.')
            return None
    except Exception as e:
        logging.error(f"Error scraping Sunday Homily: {e}")
        return None

def scrape_daily_readings(lang='en', feature='today'):
    try:
        base_url = 'https://www.catholicireland.net/readings/'
        params = {
            'feature': feature,
            'lang': 'irish' if lang == 'ga' else 'english'
        }
        response = requests.get(base_url, params=params, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        # Extract the readings content
        content_div = soup.find('div', class_='entry-content')
        if content_div:
            readings = content_div.get_text(separator='\n', strip=True)
            return readings
        else:
            logging.error('Daily readings content not found in the page.')
            return None
    except Exception as e:
        logging.error(f"Error scraping Daily Readings: {e}")
        return None

def scrape_sunday_readings(lang='en'):
    # Since Sunday readings are available one week in advance,
    # we can store the readings with the date
    return scrape_daily_readings(lang=lang, feature='sunday')

def scrape_saint_of_the_day():
    try:
        url = 'https://www.catholicireland.net/saint-day/'
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        # Extract the saint of the day content
        content_div = soup.find('div', class_='article', id='post-content')
        if content_div:
            saint = content_div.get_text(separator='\n', strip=True)
            return saint
        else:
            logging.error('Saint of the day content not found in the page.')
            return None
    except Exception as e:
        logging.error(f"Error scraping Saint of the Day: {e}")
        return None