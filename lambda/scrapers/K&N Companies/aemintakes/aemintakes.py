import json
import requests
from bs4 import BeautifulSoup

################################
#### AEM Intakes PN Scraper ####
################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.aemintakes.com'
    query_url = f'{base_URL}/search/{part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('ol', class_='product-items')
        listings = container.find_all('li', class_='product-item')
        for listing in listings:
            listing_obj = {}
            try:
                product_link = listing.find('a', class_='product-item-link')['href']
                product_name = listing.find('strong', class_='product-item-name').text.strip()
                product_photo = listing.find('img', class_='product-image-photo')['data-original']
                product_price = listing.find('span', class_='price').text.strip()
            except (AttributeError, TypeError, KeyError):
                continue

            listing_obj['link'] = product_link
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'aemintakes.svg'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)