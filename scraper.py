# scraper.py
import requests
from bs4 import BeautifulSoup
from storage import save_data
import argparse

URLS = {
    'daily_readings': {
        'url': 'https://www.catholicireland.net/readings/',
        'css_selector': 'div.article.softd_single',
    },
    'sunday_homily': {
        'url': 'https://www.catholicireland.net/sunday-homily/',
        'css_selector': 'div.article',
    },
    'saint_of_the_day': {
        'url': 'https://www.catholicireland.net/saint-day/',
        'css_selector': 'div.article.softd_single',
    },
    'next_sunday_reading': {
        'url': 'https://www.catholicireland.net/readings/?feature=sunday',
        'css_selector': 'div.article.softd_single',
    },
    'next_sunday_reading_irish': {
        'url': 'https://www.catholicireland.net/readings/?feature=sunday&lang=irish',
        'css_selector': 'div.article.softd_single',
    },
    'daily_readings_irish': {
        'url': 'https://www.catholicireland.net/readings/?feature=today&lang=irish',
        'css_selector': 'div.article.softd_single',
    },
}

def scrape_content(key):
    """Scrape content for a given key."""
    if key not in URLS:
        print(f"Invalid key '{key}'. Valid keys are: {', '.join(URLS.keys())}")
        return

    item = URLS[key]
    url = item['url']
    css_selector = item['css_selector']

    print(f"Scraping {url}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    content_div = soup.select_one(css_selector)
    if content_div:
        content = content_div.get_text(separator='\n', strip=True)
    else:
        content = 'No content found.'

    save_data(key, {'content': content})
    print(f"Saved content under key '{key}'")

def scrape_all():
    """Scrape all URLs and save their content."""
    for key in URLS.keys():
        scrape_content(key)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape content from CatholicIreland.net')
    parser.add_argument('keys', nargs='*', help='Keys to scrape. If none provided, all will be scraped.')
    args = parser.parse_args()

    if args.keys:
        for key in args.keys:
            scrape_content(key)
    else:
        scrape_all()