import json
import requests
from bs4 import BeautifulSoup

###################################
#### 034 Motorsport PN Scraper ####
###################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']
    
    base_URL = 'https://store.034motorsport.com'
    query_url = f'{base_URL}/catalogsearch/result/?q={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('ol', class_='product-items')
        listings = container.find_all('li', class_='product-item')
        for listing in listings:
            listing_obj = {}
            product_link = listing.find('a', class_='product-item-link')
            product_link_full = f'{base_URL}{product_link.find("a", href=True)["href"]}'
            product_name = product_link.text.strip()
            try:
                photo_parent = listing.find('a', class_='product-item-photo')
                product_photo = f'{base_URL}{photo_parent.find("img")["src"]}'
            except (AttributeError, TypeError):
                product_photo = 'N/A'
            product_price = listing.find('span', class_='price').text.strip()

            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = '034-motorsport.png'
            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)