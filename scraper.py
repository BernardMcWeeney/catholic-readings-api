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

def clean_sunday_homily(content_div):
    """Clean Sunday Homily specific content."""
    if not content_div:
        return

    # Create a new BeautifulSoup object with the same parser
    soup = BeautifulSoup("", "html.parser")
    
    # Remove the "Sunday Homily" header
    header = content_div.find('h2', class_='inner_title')
    if header:
        header.decompose()
    
    # Transform post title links into plain titles
    title = content_div.find('h1', class_='title')
    if title and title.find('a'):
        link = title.find('a')
        title_text = link.get_text(strip=True)
        new_title = soup.new_tag('h1')
        new_title.string = title_text
        title.replace_with(new_title)

def clean_saint_of_day(content_div):
    """Clean Saint of the Day specific content."""
    if not content_div:
        return

    # Create a new BeautifulSoup object with the same parser
    soup = BeautifulSoup("", "html.parser")
    
    # Remove the "Saint of the day" header
    header = content_div.find('h2', class_='inner_title')
    if header:
        header.decompose()
    
    # First check for h2 with class title (current format)
    title = content_div.find('h2', class_='title')
    if not title:
        # If not found, try h1 with class title (alternate format)
        title = content_div.find('h1', class_='title')
    
    if title and title.find('a'):
        link = title.find('a')
        title_text = link.get_text(strip=True)
        # Use the same tag type as the original (h1 or h2)
        new_title = soup.new_tag(title.name)
        new_title.string = title_text
        title.replace_with(new_title)
    
    # Remove the archive link section
    archive_link = content_div.find('span', class_='more')
    if archive_link:
        parent_div = archive_link.find_parent('div')
        if parent_div:
            parent_div.decompose()
    
    # Remove the horizontal rule before the archive section
    hr = content_div.find('hr', class_='softd-sep')
    if hr:
        hr.decompose()

def transform_images(content_div):
    """Transform image tags into WordPress block format."""
    if not content_div:
        return
        
    # Create a new BeautifulSoup object with the same parser
    soup = BeautifulSoup("", "html.parser")
    
    for img in content_div.find_all('img'):
        try:
            # Create new figure element
            figure = soup.new_tag('figure', attrs={
                'class': 'wp-block-image aligncenter size-full is-resized'
            })
            
            # Update image attributes
            img['decoding'] = 'async'
            if not img.get('width'):
                img['width'] = '1120'
            if not img.get('height'):
                img['height'] = '653'
            
            # Add WordPress-specific classes and attributes
            img['class'] = 'wp-image-117'
            img['style'] = 'aspect-ratio:1.5;object-fit:contain;width:335px;height:auto'
            
            # Generate srcset (placeholder values since we can't generate actual resized images)
            src = img.get('src', '')
            if src:
                base_url = re.sub(r'\.[^.]+$', '', src)
                img['srcset'] = f"{src} 1120w, {base_url}-300x175.jpg 300w, {base_url}-1024x597.jpg 1024w, {base_url}-768x448.jpg 768w, {base_url}-200x117.jpg 200w"
                img['sizes'] = "(max-width: 1120px) 100vw, 1120px"
            
            # Wrap img in figure
            if img.parent:
                img.wrap(figure)
        except Exception as e:
            print(f"Error transforming image: {e}")
            continue

def scrape_content(key):
    """Scrape content for a given key and return cleaned HTML content."""
    if key not in URLS:
        print(f"Invalid key '{key}'. Valid keys are: {', '.join(URLS.keys())}")
        return None

    item = URLS[key]
    url = item['url']
    css_selector = item['css_selector']

    print(f"Scraping {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        content_div = soup.select_one(css_selector)
        
        if content_div:
            # Create a new BeautifulSoup object for the content
            new_soup = BeautifulSoup(str(content_div), 'html.parser')
            content_div = new_soup.div
            
            # Remove unwanted elements
            for element in content_div(['script', 'style', 'iframe', 'noscript']):
                element.decompose()
            
            # Remove comments
            for comment in content_div.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # Apply specific cleaning based on content type
            if key == 'sunday_homily':
                clean_sunday_homily(content_div)
            elif key == 'saint_of_the_day':
                clean_saint_of_day(content_div)
            
            # Transform images
            transform_images(content_div)
            
            # Remove mentions of 'Catholic Ireland'
            text = str(content_div)
            text = re.sub(r'(?i)catholic ireland', '', text)
            
            return text
        else:
            return 'No content found.'
    except requests.RequestException as e:
        print(f"Error fetching content: {e}")
        return None

def scrape_mass_reading_details():
    """Scrape mass reading details from the specified URL."""
    url = 'https://www.universalis.com/europe.ireland/0/mass.htm'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching mass reading details: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    readings = {}
    reading_fields_map = {
        'first_reading': 'First reading',
        'psalm': 'Responsorial Psalm',
        'second_reading': 'Second reading',
        'gospel_acclamation': 'Gospel Acclamation',
        'gospel': 'Gospel'
    }

    for key, field_label in reading_fields_map.items():
        th = soup.find('th', text=re.compile(f'^{re.escape(field_label)}$', re.I))
        if th:
            sibling_th = th.find_next_sibling('th', align='right')
            if sibling_th:
                readings[key] = sibling_th.get_text(strip=True)
            else:
                parent_tr = th.find_parent('tr')
                next_tr = parent_tr.find_next_sibling('tr') if parent_tr else None
                if next_tr:
                    right_th = next_tr.find('th', align='right')
                    if right_th:
                        readings[key] = right_th.get_text(strip=True)
                    else:
                        readings[key] = None
                else:
                    readings[key] = None
        else:
            readings[key] = None

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