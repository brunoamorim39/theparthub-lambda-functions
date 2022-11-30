import json
import requests
from bs4 import BeautifulSoup

#####################################
#### Corvette Central PN Scraper ####
#####################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.corvettecentral.com'
    query_url = f'{base_URL}/search?CurrentSearchCategoryId=&q={part_number}&count=10'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('ul', id='list-of-products')
        listings = container.find_all('li')
        for listing in listings:
            listing_obj = {}

            product_link = listing.find('a', class_='product-title')
            product_link_full = f'{base_URL}{product_link["href"]}'
            product_name = product_link.text.strip()
            try:
                photo_parent = listing.find('span', class_='thumbnail')
                product_photo = f"{base_URL}{photo_parent.find('img')['data-src']}"
            except (AttributeError, TypeError):
                product_photo = 'N/A'
            product_price = listing.find('span', class_='lbl-price').text.strip()
            if product_price == '$0.00':
                product_price ='N/A'

            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'corvette-central.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)