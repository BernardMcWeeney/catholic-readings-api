# scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_sunday_homily():
    url = 'https://www.catholicireland.net/sunday-homily/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    # Extract the homily content
    content_div = soup.find('div', class_='entry-content')
    if content_div:
        homily = content_div.get_text(separator='\n', strip=True)
        return homily
    return None

def scrape_daily_readings(lang='en', feature='today'):
    base_url = 'https://www.catholicireland.net/readings/'
    params = {
        'feature': feature,
        'lang': 'irish' if lang == 'ga' else 'english'
    }
    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.content, 'lxml')

    # Extract the readings content
    content_div = soup.find('div', class_='entry-content')
    if content_div:
        readings = content_div.get_text(separator='\n', strip=True)
        return readings
    return None

def scrape_sunday_readings(lang='en'):
    # Since Sunday readings are available one week in advance,
    # we can store the readings with the date
    return scrape_daily_readings(lang=lang, feature='sunday')

def scrape_saint_of_the_day():
    url = 'https://www.catholicireland.net/saint-day/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    # Extract the saint of the day content
    content_div = soup.find('div', class_='entry-content')
    if content_div:
        saint = content_div.get_text(separator='\n', strip=True)
        return saint
    return None

# Example usage
if __name__ == '__main__':
    homily = scrape_sunday_homily()
    print('Sunday Homily:', homily)

    daily_readings = scrape_daily_readings()
    print('Daily Readings:', daily_readings)

    saint = scrape_saint_of_the_day()
    print('Saint of the Day:', saint)