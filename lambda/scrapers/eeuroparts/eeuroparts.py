import json
import requests
from bs4 import BeautifulSoup

################################
#### eEuroparts! PN Scraper ####
################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.eeuroparts.com'
    query_url = f'{base_URL}/?s={part_number}&post_type=product'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    # print(soup)
    results_array = []
    try:
        # FOR LISTINGS RESULTS PAGE
        if soup.find('ul', class_='products'):
            container = soup.find('ul', class_='products')
            listings = container.find_all('li', class_='product')
            for listing in listings:
                listing_obj = {}
                try:
                    product_link = listing.find('a', class_='o-product-card__card-title')
                    product_link_full = product_link['href']
                    product_name = product_link.text.strip()
                    product_photo_container = listing.find('div', class_='o-product-card__thumbnail')
                    product_photo = product_photo_container.find('img')['src']
                    product_price = listing.find('div', class_='o-product-card__price').text.strip()
                except (AttributeError, TypeError, KeyError):
                    continue

                listing_obj['link'] = product_link_full
                listing_obj['name'] = product_name
                listing_obj['image'] = product_photo
                listing_obj['price'] = product_price
                listing_obj['source'] = 'eeuroparts.svg'

                results_array.append(listing_obj)
        
        # FOR REDIRECT TO LISTING PAGE
        else:
            listing_obj = {}
            container = soup.find('div', class_='o-product')

            product_name = container.find('h1', class_='product_title').text.strip()
            product_photo = container.find('img', class_='u-img--base')['src']
            if container.find('div', class_='discontinued-part'):
                product_price = 'N/A'
            else:
                product_price = container.find('span', class_='woocommerce-Price-amount').text.strip()

            listing_obj['link'] = resp.url
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'eeuroparts.svg'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)