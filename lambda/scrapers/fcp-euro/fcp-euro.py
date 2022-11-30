import json
import requests
from bs4 import BeautifulSoup

#############################
#### FCP Euro PN Scraper ####
#############################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']
    
    base_URL = 'https://www.fcpeuro.com'
    query_url = f'{base_URL}/Parts/?keywords={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('div', class_='group')
        listings = container.find_all('div', class_='grid-x hit')
        for listing in listings:
            listing_obj = {}

            product_link = listing.find('a', class_='hit__name', href=True)
            product_link_full = f'{base_URL}{product_link["href"]}'
            product_name = product_link.text.strip()
            try:
                photo_parent = listing.find('div', class_='hit__img')
                product_photo = photo_parent.find('img')['src']
            except (AttributeError, TypeError):
                pass
            product_price = listing.find('span', class_='hit__money').text.strip()

            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'fcp-euro.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)