import json
import requests
from bs4 import BeautifulSoup

######################################
#### Condor Speed Shop PN Scraper ####
######################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.condorspeedshop.com'
    query_url = f'{base_URL}/search?type=product&q={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('div', class_='collection-listing')
        listings = container.find_all('div', class_='product-block')
        for listing in listings:
            listing_obj = {}

            product_link = listing.find('a', class_='product-link', href=True)
            product_link_full = f'{base_URL}{product_link["href"]}'
            product_name = product_link.find('div', class_='title').text.strip()
            try:
                product_photo = f"https:{product_link.find('img')['src']}"
            except (AttributeError, TypeError):
                product_photo = 'N/A'
            product_price = product_link.find('span', class_='price').text.strip()
            product_price = f"${product_price.split('$')[1]}"

            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'condor-speed-shop.webp'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)