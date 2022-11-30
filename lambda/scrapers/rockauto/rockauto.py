import json
import requests
from bs4 import BeautifulSoup

#############################
#### RockAuto PN Scraper ####
#############################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.rockauto.com'
    query_url = f'{base_URL}/en/partsearch/?partnum={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('div', class_='listing-container-border')
        listings = container.find_all('tbody', class_='listing-inner')
        for listing in listings:
            listing_obj = {}
            try:
                product_link = listing.find('a', class_='ra-btn-moreinfo')
                product_link_full = f'{product_link["href"]}'
                product_name = listing.find('div', class_='listing-text-row-moreinfo-truck').text.strip().replace(' Info', '')
                product_photo = f"{base_URL}{listing.find('img', class_='listing-inline-image-thumb')['src']}"
                product_price = listing.find('span', class_='listing-total').text.strip()
                if not product_price:
                    product_price = listing.find('span', class_='oos-price-text').text.strip()
            except (AttributeError, TypeError):
                continue
            
            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'rockauto.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)