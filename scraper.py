# scraper.py

import requests
from bs4 import BeautifulSoup, Comment
import re

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
    """Scrape content for a given key and return cleaned HTML content."""
    if key not in URLS:
        print(f"Invalid key '{key}'. Valid keys are: {', '.join(URLS.keys())}")
        return None

    item = URLS[key]
    url = item['url']
    css_selector = item['css_selector']

    print(f"Scraping {url}...")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    content_div = soup.select_one(css_selector)
    if content_div:
        # Remove unwanted elements
        for element in content_div(['script', 'style', 'iframe', 'noscript']):
            element.decompose()
        # Remove comments
        for comment in content_div.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        # Remove mentions of 'Catholic Ireland'
        text = str(content_div)
        text = re.sub(r'(?i)catholic ireland', '', text)
        # Parse the cleaned text back into BeautifulSoup
        cleaned_soup = BeautifulSoup(text, 'html.parser')
        # Return the cleaned HTML content
        cleaned_html = cleaned_soup.prettify()
        return cleaned_html
    else:
        return 'No content found.'

def scrape_mass_reading_details():
    """Scrape mass reading details from the specified URL."""
    url = 'https://www.universalis.com/europe.ireland/0/mass.htm'
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Initialize a dictionary to hold the readings
    readings = {}

    # Example: Updated selectors based on the current HTML structure
    # Note: You need to inspect the actual webpage to get the correct selectors

    try:
        readings['first_reading'] = soup.find('th', text=re.compile(r'First Reading', re.I)).find_next_sibling('th').get_text(strip=True)
    except AttributeError:
        readings['first_reading'] = None
        logging.warning("First Reading not found.")

    try:
        readings['psalm'] = soup.find('th', text=re.compile(r'Responsorial Psalm', re.I)).find_next_sibling('th').get_text(strip=True)
    except AttributeError:
        readings['psalm'] = None
        logging.warning("Psalm not found.")

    try:
        readings['second_reading'] = soup.find('th', text=re.compile(r'Second Reading', re.I)).find_next_sibling('th').get_text(strip=True)
    except AttributeError:
        readings['second_reading'] = None
        logging.warning("Second Reading not found.")

    try:
        readings['gospel_acclamation'] = soup.find('th', text=re.compile(r'Gospel Acclamation', re.I)).find_next_sibling('th').get_text(strip=True)
    except AttributeError:
        readings['gospel_acclamation'] = None
        logging.warning("Gospel Acclamation not found.")

    try:
        readings['gospel'] = soup.find('th', text=re.compile(r'Gospel', re.I)).find_next_sibling('th').get_text(strip=True)
    except AttributeError:
        readings['gospel'] = None
        logging.warning("Gospel not found.")

    return readings


def scrape_all():
    """Scrape all URLs and save their content."""
    from storage import save_data
    for key in URLS.keys():
        content = scrape_content(key)
        if content:
            save_data(key, content)
            print(f"Saved content under key '{key}'")

if __name__ == '__main__':
    import argparse
    from storage import save_data, redis_client

    parser = argparse.ArgumentParser(description='Scrape content from CatholicIreland.net')
    parser.add_argument('keys', nargs='*', help='Keys to scrape. If none provided, all will be scraped.')
    args = parser.parse_args()

    if args.keys:
        for key in args.keys:
            content = scrape_content(key)
            if content:
                save_data(redis_client, key, content)
                print(f"Saved content under key '{key}'")
    else:
        scrape_all()