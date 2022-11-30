import json
import requests
from bs4 import BeautifulSoup

###################################
#### AmericanMuscle PN Scraper ####
###################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.americanmuscle.com'
    query_url = f'{base_URL}/search?keywords={part_number}&generationId=0&vehicleType=All'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('div', class_='products_container')
        listings = container.find_all('div', attrs={'data-component': True})
        for listing in listings:
            listing_obj = {}

            listing_data = json.loads(listing['data-prop-product'])

            product_link = listing_data['PdpUrl']
            product_name = listing_data['DisplayName']
            product_photo = listing_data['Image']['NonRenderUrl']
            product_price = f"${round(listing_data['CurrentPrice'], 2)}"

            listing_obj['link'] = product_link
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'americanmuscle.svg'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)