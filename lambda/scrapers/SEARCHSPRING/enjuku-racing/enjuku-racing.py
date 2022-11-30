import json
import requests

##################################
#### Enjuku Racing PN Scraper ####
##################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    query_url = f'https://063mso.a.searchspring.io/api/search/search.json?ajaxCatalog=v3&resultsFormat=native&siteId=063mso&domain=https%3A%2F%2Fwww.enjukuracing.com%2Fsearch%2F%3Fsearch_query%3D{part_number}&q={part_number}&userId=V3-67ECBD23-83A6-49FA-BA79-C160EC7BF6F2&sessionId=1a14eee1-1f4b-4e30-a7fe-d9e3fc71d84c&pageLoadId=717d60ec-1c9e-4e5b-9ac5-4f59c65bdaa6'
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
            listing_obj['source'] = 'enjuku-racing.webp'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)