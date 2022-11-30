import json
import requests
from bs4 import BeautifulSoup

##################################
#### Get BMW Parts PN Scraper ####
##################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.getbmwparts.com'
    query_url = f'{base_URL}/search?search_str={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        # FOR LISTINGS RESULTS PAGE
        if soup.find('div', class_='catalog-products'):
            container = soup.find('div', class_='catalog-products')
            listings = container.find_all('div', class_='catalog-product')
            for listing in listings:
                listing_obj = {}

                product_link = listing.find('a', class_='product-image-link', href=True)
                product_link_full = f'{base_URL}{product_link["href"]}'
                product_name = listing.find('strong', class_='product-title').text.strip()
                try:
                    product_photo = f"https:{product_link.find('img')['lazysrc']}"
                except (AttributeError, TypeError, KeyError):
                    continue
                price_parent = listing.find('div', class_='add-to-cart-col')
                if price_parent.find('strong', class_='cannot-purchase'):
                    product_price = 'N/A'
                elif price_parent.find('div', class_='sale-price'):
                    product_price = price_parent.find('div', class_='sale-price').text.strip()
                else:
                    product_price.price_parent.find('div', class_='list-price').text.strip()

                listing_obj['link'] = product_link_full
                listing_obj['name'] = product_name
                listing_obj['image'] = product_photo
                listing_obj['price'] = product_price
                listing_obj['source'] = 'getbmwparts.png'

                results_array.append(listing_obj)
        
        # FOR REDIRECT TO LISTING PAGE
        else:
            listing_obj = {}
            container = soup.find('div', class_='product-page-layout')

            product_name = container.find('h1', class_='product-title').text.strip()
            if container.find('img', class_='product-main-image'):
                product_photo = f"https:{container.find('img', class_='product-main-image')['src']}"
            else:
                product_photo = f"https:{container.find('img')['src']}"
            if container.find('div', class_='discontinued-part'):
                product_price = 'N/A'
            else:
                product_price = container.find('span', id='product_price').text.strip()

            listing_obj['link'] = resp.url
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'getbmwparts.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)