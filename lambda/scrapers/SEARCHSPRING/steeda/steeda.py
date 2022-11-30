import json
import requests

###########################
#### Steeda PN Scraper ####
###########################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    query_url = f'https://5qthyx.a.searchspring.io/api/search/search.json?ajaxCatalog=v3&resultsFormat=native&siteId=5qthyx&domain=https%3A%2F%2Fwww.steeda.com%2Fshop%3Fkeyword%3D{part_number}&q={part_number}&userId=V3-9CF1BDE5-5F23-4507-8068-43912F621E9A&sessionId=aae5880b-b2b9-49f6-9536-e310d32d70a7&pageLoadId=51f14bd5-2b5d-424d-a459-ce106d8a1cb7'
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
            listing_obj['source'] = 'steeda.webp'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)