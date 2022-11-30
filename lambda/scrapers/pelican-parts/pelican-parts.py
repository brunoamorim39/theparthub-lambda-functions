import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

##################################
#### Pelican Parts PN Scraper ####
##################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    base_URL = 'http://www.pelicanparts.com'
    query_url = f'{base_URL}/search/?q={part_number}'

    options = Options()
    options.headless = True
    proxy = Proxy({
    'httpProxy': proxies['http'][7::],
    'ftpProxy': proxies['http'][7::],
    'sslProxy': proxies['http'][7::],
    'proxyType': 'MANUAL'
    })
    driver = webdriver.Firefox(options=options, proxy=proxy)

    driver.get(query_url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'klevuProduct')))

    results_array = []
    try:
        container = driver.find_element(By.CLASS_NAME, 'kuResults')
        listings = container.find_elements(By.CLASS_NAME, 'klevuProduct')
        for listing in listings:
            listing_obj = {}

            product_link = listing.find_element(By.CLASS_NAME, 'kuName').find_element(By.TAG_NAME, 'a')
            product_link_full = product_link.get_attribute('href')
            product_name = product_link.get_attribute('innerText')
            try:
                product_photo = listing.find_element(By.CLASS_NAME, 'kuProdImg').get_attribute('src')
            except (AttributeError, TypeError):
                pass
            product_price = listing.find_element(By.CLASS_NAME, 'kuPrice').get_attribute('innerText')

            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'pelican-parts.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)