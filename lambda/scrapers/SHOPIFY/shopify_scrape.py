import json
import requests

############################
#### Shopify PN Scraper ####
############################
def lambda_handler(event, context):
    headers = event['headers']
    proxies = event['proxies']
    handle = event['handle']
    vendor_url = event['vendor_url']

    query_url = f'{vendor_url}/products/{handle}.json'
    resp = requests.get(query_url, proxies=proxies, headers=headers).json()
    try:
        listing_obj = {}
        listing_obj['link'] = f'{vendor_url}/products/{handle}'
        listing_obj['name'] = resp['product']['title']
        listing_obj['image'] =  resp['product']['image']['src']
        listing_obj['price'] = resp['product']['variants'][0]['price']
        listing_obj['source'] = f'{vendor_url.split(".")[1]}.png'
    except AttributeError:
        pass
    return json.dumps([listing_obj])