import json
import requests
from bs4 import BeautifulSoup

################################
#### K&N Filters PN Scraper ####
################################
def lambda_handler(event, context):
    headers = event['headers']
    proxies = event['proxies']
    url = event['xref_url']

    resp = requests.get(url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    try:
        listing_obj = {}
        listing_obj['link'] = url
        listing_obj['name'] = f"{soup.find('h1', class_='_3Cir9wIlHLMIeTwLLMbCuo').text.strip()} | {soup.find('h1', class_='_1KvJhhAHFQQ2K5USKJ56dc').text.strip()}"
        listing_obj['image'] = soup.find('img', class_='_1vxRiFtyh8Xkwb5xlL7K9N')['src']
        try:
            listing_obj['price'] = soup.find('div', class_='_10coDizHEkaNv_SoMFQzpz').text.strip()
        except (AttributeError, TypeError):
            listing_obj['price'] = soup.find('div', class_='_2pX4kpF6OVSpON2oHQsG3w').text.strip()
        listing_obj['source'] = 'knfilters.svg'
    except AttributeError:
        pass
    return json.dumps([listing_obj])