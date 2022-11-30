import json
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# EXAMPLE PART NUMBERS
# 64118391363 - E30 Heater Core
# SBC-K70037 - MKII Golf Clutch Kit
# 98350 - Audi A4 A/C Compressor
# 23430008 - Volvo Fuel Pump
# 63848-9Y000 - OEM Nissan Fender Liner Clip
# 6510906380 - Mercedes Sprinter Turbocharger
# 246126 - C6 Corvette Radiator
# 10005354 - LeSabre Air Tube
# 10000316 - Fleetwood Upper Control Arm
# 99110613702 - 991 911 Radiator

payload = {
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    },
    'proxies': {
        'http': 'http://45.72.59.14:3128'
    },
    'part_number': '10005'
}
t0 = time.time()
headers = payload['headers']
part_number  = payload['part_number']
proxies = payload['proxies']
# proxies = payload['proxies']['http'][7::]

# UTILIZING BEAUTIFULSOUP
# ------------------------------
base_URL = 'https://www.knfilters.com'
query_url = f'{base_URL}/cross-reference/walker/5205002-oil-filter'
# print(query_url)
resp = requests.get(query_url, proxies=proxies, headers=headers, timeout=5)
# print(resp)
soup = BeautifulSoup(resp.content, 'html.parser')
# print(soup)
results_array = []
try:
    container = soup.find('ul', class_='-buCiWq97Zwh8K3NM1Mdi')
    print(container)
    listings = container.find_all('ul', class_='_1IJ5Oc_4-Wf1N44zj4DLCP')
    # print(listings)
    for listing in listings:
        # print(listing)
        listing_obj = {}
        try:
            product_link = listing.find('a', class_='product-item-link')['href']
            product_name = listing.find('strong', class_='product-item-name').text.strip()
            product_photo = listing.find('img', class_='product-image-photo')['data-original']
            product_price = listing.find('span', class_='price').text.strip()
        except (AttributeError, TypeError, KeyError):
            continue

        listing_obj['link'] = product_link
        listing_obj['name'] = product_name
        listing_obj['image'] = product_photo
        listing_obj['price'] = product_price
        listing_obj['source'] = 'aemintakes.svg'

        results_array.append(listing_obj)
    print(results_array)
except AttributeError:
    print(results_array)

# brands = container.find_all('li', class_='UfDPijIpXyjDv4Su7qLm2')
# for brand in brands:
#     brand_link = brand.find('a')['href']
#     brand_url = f'https://www.knfilters.com{brand_link}'
#     brand_resp = requests.get(brand_url, proxies=proxies, headers=headers)
#     brand_soup = BeautifulSoup(brand_resp.content, 'html.parser')
#     ref_parts = brand_soup.find_all('li', class_='UfDPijIpXyjDv4Su7qLm2')
#     for part in ref_parts:
#         part_link = part.find('a')['href']
#         part_url = f'https://www.knfilters.com{part_link}'
#         part_resp = requests.get(part_url, proxies=proxies, headers=headers)
#         part_soup = BeautifulSoup(part_resp.content, 'html.parser')
#         part_xref = part_soup.find('h1', class_='_3Cir9wIlHLMIeTwLLMbCuo').text.strip()
#         part_name = part_soup.find('h1', class_='_1KvJhhAHFQQ2K5USKJ56dc').text.strip()
#         print(f'{part_url} | {part_xref} | {part_name}')



#     if soup.find('div', class_='searchResultContainer'):
#         container = soup.find('div', id='ctl00_Content_PageBody_SearchResultPanel')
#         listings = container.find_all('div', class_='panel-body')
#         for listing in listings:
#             listing_obj = {}
#             try:
#                 product_link = listing.find('a', class_='productSearchProductTitle')
#                 product_link_full = f"{base_URL}{product_link['href']}"
#                 product_name = product_link.text.strip()
#                 product_photo = listing.find('img')['src']
#                 product_price = f"${listing.find('span', class_='money').text.strip().split(' ')[-1]}"
#             except (AttributeError, TypeError, KeyError):
#                 continue

#             listing_obj['link'] = product_link_full
#             listing_obj['name'] = product_name
#             listing_obj['image'] = product_photo
#             listing_obj['price'] = product_price
#             listing_obj['source'] = 'XXXXXXXXXXXXXXXXXXXXXX.png'

#             results_array.append(listing_obj)
#     else:
#         listing_obj = {}
#         container = soup.find('div', id='contentDiv')

#         product_name = container.find('h2', class_='panel-title').text.strip()
#         product_photo = container.find('img', id='imgthumbnail')['src']
#         if container.find('div', class_='discontinued-part'):
#             product_price = 'N/A'
#         else:
#             product_price = f"${container.find('span', class_='productPriceSpan').text.strip().split(' ')[-1]}"

#         listing_obj['link'] = resp.url
#         listing_obj['name'] = product_name
#         listing_obj['image'] = product_photo
#         listing_obj['price'] = product_price
#         listing_obj['source'] = 'XXXXXXXXXXXXXXXXXXXXXX.png'

#         results_array.append(listing_obj)
#     print(results_array)
# except AttributeError:
#     print(results_array)


    # FOR LISTINGS RESULTS PAGE
#     if soup.find('ul', class_='products'):
#         container = soup.find('ul', class_='products')
#         # print(container)
#         listings = container.find_all('li', class_='product')
#         # print(listings)
#         for listing in listings:
#             # print(listing)
#             listing_obj = {}
#             try:
#                 product_link = listing.find('a', class_='o-product-card__card-title')
#                 product_link_full = product_link['href']
#                 product_name = product_link.text.strip()
#                 product_photo_container = listing.find('div', class_='o-product-card__thumbnail')
#                 product_photo = product_photo_container.find('img')['src']
#                 product_price = listing.find('div', class_='o-product-card__price').text.strip()
#             except (AttributeError, TypeError, KeyError):
#                 continue

#             listing_obj['link'] = product_link_full
#             listing_obj['name'] = product_name
#             listing_obj['image'] = product_photo
#             listing_obj['price'] = product_price
#             listing_obj['source'] = 'eeuroparts.png'

#             results_array.append(listing_obj)
    
#     # FOR REDIRECT TO LISTING PAGE
#     else:
#         listing_obj = {}
#         container = soup.find('div', class_='o-product')
#         # print(container)

#         product_name = container.find('h1', class_='product_title').text.strip()
#         product_photo = container.find('img', class_='u-img--base')['src']
#         if container.find('div', class_='discontinued-part'):
#             product_price = 'N/A'
#         else:
#             product_price = container.find('span', class_='woocommerce-Price-amount').text.strip()

#         listing_obj['link'] = resp.url
#         listing_obj['name'] = product_name
#         listing_obj['image'] = product_photo
#         listing_obj['price'] = product_price
#         listing_obj['source'] = 'eeuroparts.png'

#         results_array.append(listing_obj)

#     print(results_array)
# except AttributeError:
#     print(results_array)
    

# UTILIZING POST REQUEST
# -----------------------
# base_URL = 'https://www.autohausaz.com'
# query_url = f'{base_URL}/catalog/ajax/findpartsbypartnumber'
# post_data = {'query': part_number}
# resp = requests.post(query_url, data=post_data, proxies=proxies, headers=headers).json()
# results_array = []
# try:
#     listings = resp['parts']
#     for listing in listings:
#         listing_obj = {}

#         product_link = f"{base_URL}{listing['PartURL']}"
#         product_name = f"{listing['Brand']}{listing['Name']}"
#         product_photo = f"{base_URL}{listing['ImageSmallURL']}"
#         product_price = f"${listing['CurrentPrice']}"

#         listing_obj['link'] = product_link
#         listing_obj['name'] = product_name
#         listing_obj['image'] = product_photo
#         listing_obj['price'] = product_price
#         listing_obj['source'] = 'autohausaz.png'

#         results_array.append(listing_obj)
#     print(results_array)
# except AttributeError:
#     print(results_array)


# UTILIZING API CALLS
# ------------------------
# query_url = f'https://eucs27.ksearchnet.com/cloud-search/n-search/search?ticket=klevu-162757615056813994&term={part_number}&paginationStartsFrom=0&sortPrice=false&ipAddress=undefined&analyticsApiKey=klevu-162757615056813994&showOutOfStockProducts=true&klevuFetchPopularTerms=false&klevu_priceInterval=500&fetchMinMaxPrice=true&noOfResults=9&klevuSort=rel&enableFilters=true&filterResults=&visibility=search&category=KLEVU_PRODUCT&klevu_filterLimit=50&sv=1219&lsqt=&responseType=json&resultForZero=1&klevu_loginCustomerGroup='
# resp = requests.get(query_url, proxies=proxies, headers=headers).json()
# results_array = []
# try:
#     listings = resp['result']
#     for listing in listings:
#         listing_obj = {}

#         product_link = listing['url']
#         product_name = listing['name']
#         product_photo = listing['imageUrl']
#         product_photo = product_photo.replace('&amp;', '&')
#         product_price = f"${float(listing['price']):.2f}"

#         listing_obj['link'] = product_link
#         listing_obj['name'] = product_name
#         listing_obj['image'] = product_photo
#         listing_obj['price'] = product_price
#         listing_obj['source'] = 'lethal_performance.webp'

#         results_array.append(listing_obj)
#     print(results_array)
# except AttributeError:
#     print(results_array)


# REVOLUTION PARTS SCRAPERS
# ----------------------------------
# base_URL = 'https://www.chevroletonlineparts.com'
# query_url = f'{base_URL}/search?search_str={part_number}'
# resp = requests.get(query_url, proxies=proxies, headers=headers)
# soup = BeautifulSoup(resp.content, 'html.parser')
# results_array = []
# try:
#     # Check if search results page or listing page
#     container = soup.find('div', class_='catalog-products')
#     print(container)
#     print(results_array)
# except AttributeError:
#     print(results_array)


# UTILIZING SELENIUM
# ----------------------------------
# options = Options()
# proxy = Proxy({
#     'httpProxy': proxies[7::],
#     'ftpProxy': proxies[7::],
#     'sslProxy': proxies[7::],
#     'proxyType': 'MANUAL'
#     })
# options.headless = True
# driver = webdriver.Firefox(options=options, proxy=proxy)

# driver.get(query_url)
# WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'klevuProduct')))

# results_array = []
# try:
#     container = driver.find_element(By.CLASS_NAME, 'kuResults')
#     listings = container.find_elements(By.CLASS_NAME, 'klevuProduct')
#     for listing in listings:
#         listing_obj = {}

#         product_link = listing.find_element(By.CLASS_NAME, 'kuName').find_element(By.TAG_NAME, 'a')
#         product_link_full = product_link.get_attribute('href')
#         product_name = product_link.get_attribute('innerText')
#         try:
#             product_photo = listing.find_element(By.CLASS_NAME, 'kuProdImg').get_attribute('src')
#         except (AttributeError, TypeError):
#             pass
#         product_price = listing.find_element(By.CLASS_NAME, 'kuPrice').get_attribute('innerText')

#         listing_obj['link'] = product_link_full
#         listing_obj['name'] = product_name
#         listing_obj['image'] = product_photo
#         listing_obj['price'] = product_price
#         listing_obj['source'] = 'pelican-parts.png'

#         results_array.append(listing_obj)
#     print(results_array)
# except AttributeError:
#     print(results_array)

# EBAY API Call
# api_url = 'https://api.ebay.com'
# query_url = f'{api_url}/buy/browse/v1/item_summary/search?q={part_number}'
# headers['Authorization'] = 'Bearer v^1.1#i^1#r^0#p^3#I^3#f^0#t^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'
# headers['Content-Type'] = 'application/json'
# headers['X-EBAY-C-MARKETPLACE-ID'] = 'EBAY_US'
# resp = requests.get(query_url, proxies=proxies, headers=headers).json()
# results_array = []
# try:
#     listings = resp['itemSummaries']
#     for listing in listings:
#         listing_obj = {}

#         product_link = listing['itemWebUrl']
#         product_name = listing['title']
#         product_photo = listing['image']['imageUrl']
#         product_price = listing['price']['value']

#         listing_obj['link'] = product_link
#         listing_obj['name'] = product_name
#         listing_obj['image'] = product_photo
#         listing_obj['price'] = product_price
#         listing_obj['source'] = 'ebay.png'

#         results_array.append(listing_obj)
#     print(results_array)
# except AttributeError:
#     print(results_array)

print(f'Execution Time: {time.time() - t0}')