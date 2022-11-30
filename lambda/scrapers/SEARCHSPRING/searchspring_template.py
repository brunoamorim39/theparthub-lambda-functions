import json
import requests

##################################
#### XXXXXXXXXXXXX PN Scraper ####
##################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    query_url = f'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    resp = requests.get(query_url, proxies=proxies, headers=headers).json()
    results_array = []
    try:
        listings = resp['results']
        for listing in listings:
            listing_obj = {}

            product_link = listing['url']
            product_name = listing['name']
            product_photo = listing['imageUrl']
            product_photo = product_photo.replace('&amp;', '&')
            product_price = f"${float(listing['price']):.2f}"

            listing_obj['link'] = product_link
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'XXXXXXXXXXXXXXXXXXXXXXXXX'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)