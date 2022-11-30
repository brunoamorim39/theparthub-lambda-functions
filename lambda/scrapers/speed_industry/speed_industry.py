import json
import requests
from bs4 import BeautifulSoup

###################################
#### Speed Industry PN Scraper ####
###################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.speedindustry.com'
    query_url = f'{base_URL}/search?q={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('div', class_='item-grid')
        listings = container.find_all('div', class_='product-item')
        for listing in listings:
            listing_obj = {}
            try:
                product_link = listing.find('a')
                product_link_full = f"{base_URL}{product_link['href']}"
                product_name = listing.find('h2', class_='product-title').text.strip()
                product_photo = listing.find('img', class_='picture-img')['src']
                product_price = listing.find('span', class_='actual-price').text.strip()
            except (AttributeError, TypeError, KeyError):
                continue

            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'speed_industry.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)