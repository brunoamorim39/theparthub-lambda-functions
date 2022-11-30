import json
import requests
from bs4 import BeautifulSoup

###############################
#### ECS Tuning PN Scraper ####
###############################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']
    
    base_URL = 'https://www.ecstuning.com'
    query_url = f'{base_URL}/Search/SiteSearch/{part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('div', class_='groupContainer')
        listings = container.find_all('div', class_='productListBox')
        for listing in listings:
            listing_obj = {}

            product_link = listing.find('a', href=True)['href']
            product_link_full = f'{base_URL}{product_link}'
            product_name = listing.find('span', class_='cleanDesc productTitle').text.strip()
            try:
                product_photo = listing.find('img', class_='productThumb')['src']
            except (AttributeError, TypeError):
                product_photo = 'https://c1521972.ssl.cf0.rackcdn.com/img/ecs_box_no_image.jpg'
            product_price = listing.find('span', class_='price').text.strip()

            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'ecs-tuning.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)