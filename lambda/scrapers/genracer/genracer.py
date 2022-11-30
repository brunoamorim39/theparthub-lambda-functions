import json
import requests
from bs4 import BeautifulSoup

#############################
#### Genracer PN Scraper ####
#############################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.genracer.com'
    query_url = f'{base_URL}/search.php?search_query={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('ul', class_='productGrid')
        listings = container.find_all('li', class_='product')
        for listing in listings:
            listing_obj = {}

            product_link = listing.find('h4', class_='card-title')
            product_link_full = f"{product_link.find('a', href=True)['href']}"
            product_name = product_link.text.strip()
            try:
                product_photo = listing.find('img', class_='lazyload')['data-src']
            except (AttributeError, TypeError, KeyError):
                continue
            product_price = listing.find('span', class_='price--withoutTax').text.strip()

            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'genracer.webp'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)