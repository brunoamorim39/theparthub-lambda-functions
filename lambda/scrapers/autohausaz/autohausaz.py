import json
import requests

###############################
#### AutohausAZ PN Scraper ####
###############################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.autohausaz.com'
    query_url = f'{base_URL}/catalog/ajax/findpartsbypartnumber'
    post_data = {'partnumber': part_number}
    resp = requests.post(query_url, data=post_data, proxies=proxies, headers=headers).json()
    results_array = []
    try:
        listings = resp['parts']
        for listing in listings:
            listing_obj = {}

            product_link = f"{base_URL}{listing['PartURL']}"
            product_name = f"{listing['Brand']} {listing['Name']}"
            product_photo = f"{base_URL}{listing['ImageSmallURL']}"
            product_price = f"${listing['CurrentPrice']}"

            listing_obj['link'] = product_link
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'autohausaz.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)