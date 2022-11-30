import json
import requests
from bs4 import BeautifulSoup

#############################
#### Autozone PN Scraper ####
#############################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.autozone.com'
    query_url = f'{base_URL}/searchresult?searchText={part_number}&recsPerPage=12'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        cat_container = soup.find('div', id='search-result-list')
        cat_listings = cat_container.find_all('article', class_='az_Co')
        for cat in cat_listings:
            cat_link = cat.find('a', href=True)['href']
            cat_url = f'{base_URL}{cat_link}'
            cat_resp = requests.get(cat_url, proxies=proxies, headers=headers)
            cat_soup = BeautifulSoup(cat_resp.content, 'html.parser')
            container = cat_soup.find('div', id='shelf-result-list')
            listings = container.find_all('article', class_='az_M3')
            for listing in listings:
                listing_obj = {}

                product_link = listing.find('a', class_='az_dd')
                product_link_full = f'{base_URL}{product_link["href"]}'
                product_name = product_link.text.strip()
                try:
                    photo_parent = listing.find('a', class_='az_c3')
                    product_photo = listing.find_all('img')[2]['src']
                except (AttributeError, TypeError):
                    product_photo = 'N/A'
                product_price = listing.find('div', class_='az_Z az_MTb').text.strip()

                listing_obj['link'] = product_link_full
                listing_obj['name'] = product_name
                listing_obj['image'] = product_photo
                listing_obj['price'] = product_price
                listing_obj['source'] = 'autozone.png'

                results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)