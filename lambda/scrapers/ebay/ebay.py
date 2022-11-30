import json
import requests

#########################
#### eBay PN Scraper ####
#########################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    headers['Authorization'] = json.loads(event)['ebay_api_key']
    headers['Content-Type'] = 'application/json'
    headers['X-EBAY-C-MARKETPLACE-ID'] = 'EBAY_US'

    api_url = 'https://api.ebay.com'
    query_url = f'{api_url}/buy/browse/v1/item_summary/search?q={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers).json()
    results_array = []
    try:
        listings = resp['itemSummaries']
        for listing in listings:
            listing_obj = {}

            product_link = listing['itemWebUrl']
            product_name = listing['title']
            product_photo = listing['image']['imageUrl']
            product_price = listing['price']['value']

            listing_obj['link'] = product_link
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'ebay.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)