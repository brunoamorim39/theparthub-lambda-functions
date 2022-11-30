import json
import requests

#######################################
#### Lethal Performance PN Scraper ####
#######################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    query_url = f'https://eucs27.ksearchnet.com/cloud-search/n-search/search?ticket=klevu-162757615056813994&term={part_number}&paginationStartsFrom=0&sortPrice=false&ipAddress=undefined&analyticsApiKey=klevu-162757615056813994&showOutOfStockProducts=true&klevuFetchPopularTerms=false&klevu_priceInterval=500&fetchMinMaxPrice=true&noOfResults=9&klevuSort=rel&enableFilters=true&filterResults=&visibility=search&category=KLEVU_PRODUCT&klevu_filterLimit=50&sv=1219&lsqt=&responseType=json&resultForZero=1&klevu_loginCustomerGroup='
    resp = requests.get(query_url, proxies=proxies, headers=headers).json()
    results_array = []
    try:
        listings = resp['result']
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
            listing_obj['source'] = 'lethal_performance.webp'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)