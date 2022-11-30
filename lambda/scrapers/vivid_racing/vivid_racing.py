import json
import requests
from bs4 import BeautifulSoup

#################################
#### Vivid Racing PN Scraper ####
#################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.vividracing.com'
    query_url = f'{base_URL}/index.php?keywords={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('div', class_='col-xl-10')
        listings = container.find_all('div', class_='product-listing')
        for listing in listings:
            listing_obj = {}
            try:
                product_link = listing.find('a')
                product_link_full = f"https:{product_link['href']}"
                product_name = listing.find('p').text.strip() + ' ' + listing.find('p', class_='text-primary').text.strip()
                product_photo = listing.find('img', class_='img-responsive')['src']
                try:
                    product_price = listing.find('span', class_='productSpecialPrice').text.strip()
                except (AttributeError, TypeError):
                    product_price = listing.find('div', class_='col-xl-6').text.strip()
            except (AttributeError, TypeError, KeyError):
                continue

            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'vivid_racing.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)