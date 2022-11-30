import json
import requests
from bs4 import BeautifulSoup

##########################################################
#### VW Parts and Accessories Online Store PN Scraper ####
##########################################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://parts.vw.com'
    query_url = f'{base_URL}/productSearch.aspx?searchTerm={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        if soup.find('div', class_='searchResultContainer'):
            container = soup.find('div', id='ctl00_Content_PageBody_SearchResultPanel')
            listings = container.find_all('div', class_='panel-body')
            for listing in listings:
                listing_obj = {}
                try:
                    product_link = listing.find('a', class_='productSearchProductTitle')
                    product_link_full = f"{base_URL}{product_link['href']}"
                    product_name = product_link.text.strip()
                    product_photo = listing.find('img')['src']
                    product_price = f"${listing.find('span', class_='money').text.strip().split(' ')[-1]}"
                except (AttributeError, TypeError, KeyError):
                    continue

                listing_obj['link'] = product_link_full
                listing_obj['name'] = product_name
                listing_obj['image'] = product_photo
                listing_obj['price'] = product_price
                listing_obj['source'] = 'vw_parts_and_accessories_online_store.png'

                results_array.append(listing_obj)
        else:
            listing_obj = {}
            container = soup.find('div', id='contentDiv')

            product_name = container.find('h2', class_='panel-title').text.strip()
            product_photo = container.find('img', id='imgthumbnail')['src']
            if container.find('div', class_='discontinued-part'):
                product_price = 'N/A'
            else:
                product_price = f"${container.find('span', class_='productPriceSpan').text.strip().split(' ')[-1]}"

            listing_obj['link'] = resp.url
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'vw_parts_and_accessories_online_store.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)