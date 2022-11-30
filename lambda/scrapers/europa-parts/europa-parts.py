import json
import requests
from bs4 import BeautifulSoup

#################################
#### Europa Parts PN Scraper ####
#################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.europaparts.com'
    query_url = f'{base_URL}/catalogsearch/result/?q={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        if '?q=' in resp.url:
            container = soup.find('ol', class_='product-items')
            listings = container.find_all('li', class_='product-item')
            for listing in listings:
                listing_obj = {}

                product_link = listing.find('a', class_='product-item-text-link', href=True)
                product_link_full = f'{product_link["href"]}'
                product_name = product_link.text.strip()
                try:
                    product_photo = listing.find('img', class_='lazyload')['data-src']
                except (AttributeError, TypeError):
                    product_photo = 'N/A'
                product_price = listing.find('span', class_='price').text.strip()

                listing_obj['link'] = product_link_full
                listing_obj['name'] = product_name
                listing_obj['image'] = product_photo
                listing_obj['price'] = product_price
                listing_obj['source'] = 'europa-parts.svg'

                results_array.append(listing_obj)
        else:
            listing_obj = {}
            container = soup.find('div', class_='product-info-wrapper')

            product_name = container.find('h1', class_='page-title').text.strip()
            product_photo = container.find('img', class_='no-sirv-lazy-load')['src']
            product_price = container.find('span', class_='price').text.strip()

            listing_obj['link'] = resp.url
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'europa-parts.svg'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)