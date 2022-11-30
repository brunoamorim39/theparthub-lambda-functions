import json
import requests

################################
#### Bimmerworld PN Scraper ####
################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    query_url = f'https://fnpgvs.a.searchspring.io/api/search/search.json?ajaxCatalog=v3&resultsFormat=native&siteId=fnpgvs&domain=https%3A%2F%2Fwww.bimmerworld.com%2Fssearch.html%3Fquery%3D{part_number}&q={part_number}&userId=V3-BC85E163-E63F-4CF2-AC5A-8C0A09C83F6A&sessionId=30344e6c-1f22-401c-b490-510dd1c5159c&pageLoadId=cbffbf30-82bf-4d4e-b70b-4a4baab1edcd'
    resp = requests.get(query_url, proxies=proxies, headers=headers).json()
    results_array = []
    try:
        listings = resp['results']
        for listing in listings:
            try:
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
                listing_obj['source'] = 'bimmerworld.png'

                results_array.append(listing_obj)
            except KeyError:
                continue
    except AttributeError:
        pass
    return json.dumps(results_array)