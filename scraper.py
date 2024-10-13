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

        # Find the main content container
        content_div = soup.find('div', class_='article', id='post-content')
        if content_div:
            homily = content_div.get_text(separator='\n', strip=True)
            return homily
        else:
            logging.error('Sunday homily content not found in the page.')
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

        # Find the main content container
        content_div = soup.find('div', class_='article', id='post-content')
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
    return scrape_daily_readings(lang=lang, feature='sunday')

def scrape_saint_of_the_day():
    try:
        url = 'https://www.catholicireland.net/saint-day/'
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        # Find the main article container
        article_div = soup.find('div', class_='article softd_single')
        if not article_div:
            logging.error('Article container not found.')
            return None

        # Extract the title
        title_div = article_div.find('div', id='softd_title')
        if title_div:
            title = title_div.get_text(separator='\n', strip=True)
        else:
            title = 'Saint of the Day'

        # Extract the content
        content_div = article_div.find('div', id='softd-content')
        if content_div:
            # Remove unwanted elements like scripts or styles
            for unwanted in content_div(['script', 'style']):
                unwanted.extract()
            content = content_div.get_text(separator='\n', strip=True)
        else:
            logging.error('Saint of the day content not found in the page.')
            return None

        # Combine the title and content
        saint_info = f"{title}\n\n{content}"
        return saint_info
    except Exception as e:
        logging.error(f"Error scraping Saint of the Day: {e}")
        return None
