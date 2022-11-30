import json
import requests

#######################
#### Shopify Scout ####
#######################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']
    vendor_url = json.loads(event)['vendor_url']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']
    # vendor_url = event['vendor_url']

    query_url = f'{vendor_url}/search?view=json&q={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    shopify_ids = resp.content
    return shopify_ids