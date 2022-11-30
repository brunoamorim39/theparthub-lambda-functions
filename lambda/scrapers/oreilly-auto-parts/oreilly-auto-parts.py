import json
import requests
from bs4 import BeautifulSoup

########################################
#### O'Reilly Auto Parts PN Scraper ####
########################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']
    
    base_URL = 'https://www.oreillyauto.com'
    query_url = f'{base_URL}/search?q={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('div', class_='product-row_wrap')
        listings = container.find_all('article', class_='product product--plp product--interchange js-product')
        for listing in listings:
            listing_obj = {}

            product_link = listing.find('a', class_='js-product-link product__link')
            product_link_full = f'{base_URL}{product_link["href"]}'
            product_name = product_link.find('h2', class_='js-product-name js-ga-product-name product__name').text.strip()
            try:
                photo_parent = listing.find('div', class_='product__image-wrap')
                product_photo = f"https:{photo_parent.find('img')['data-original']}"
            except (AttributeError, TypeError):
                product_photo = 'N/A'
            product_price = listing.find('div', class_='pricing').text.strip()
            print(product_price)

            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'oreilly-auto-parts.png'
            
            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)