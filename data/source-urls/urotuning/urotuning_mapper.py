from json.decoder import JSONDecodeError
import requests
from bs4 import BeautifulSoup
import csv
import json
import random
import time
from selenium import webdriver

user_agent_desktop = 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36'
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp, image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Accept-Encoding': 'gzip',
'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

def sleep():
    time.sleep(random.uniform(30, 60))
    return

def request_json(url):
    try:
        json_file = requests.get(url, timeout=10, headers=headers).json()
        return json_file
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, TypeError) as e:
        print(e)
        sleep()
        sleep()
        sleep()
        sleep()
        sleep()
        request_json(url)
    except (JSONDecodeError, ValueError, TypeError):
        return

def save_to_file(data):
    with open('map.csv', 'w', newline='') as csvfile:
        fieldnames = ['vehicle_tag', 'link', 'title', 'category', 'image', 'price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for element in data:
            writer.writerow({'vehicle_tag': element[0], 'link': element[1], 'title': element[2], 'category': element[3], 'image': element[4], 'price': element[5]})

def map_site(vehicle_tag):
    base_url = 'https://www.urotuning.com'
    url = f'https://www.urotuning.com{vehicle_tag}/products.json?limit=250'
    page = 1

    while True:
        new_url = f'{url}&page={page}'
        print(new_url)
        page += 1

        sleep()
        try:
            json_file = request_json(new_url)
        except (JSONDecodeError, ValueError, TypeError):
            break
        if len(json_file['products']) == 0:
            break

        for product in json_file['products']:
            title = product['title']
            handle = product['handle']
            category = product['product_type']
            try:
                image = product['images'][0]['src']
            except IndexError as e:
                print(e)
                image = 'Missing Image'

            for variant in product['variants']:
                variant_ID = variant['id']
                link = f'{base_url}/products/{handle}?variant={variant_ID}'
                variant_price = variant['price']
                price = f'${variant_price}'
            
                print(vehicle_tag)
                print(link)
                print(title)
                print(category)
                print(image)
                print(price)
                print()

                product_data.append((vehicle_tag, link, title, category, image, price))
        
        save_to_file(product_data)

def test_results():
    with open('map.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each_line in csvreader:
            listing_link = each_line[0]
            listing_name = each_line[1]
            listing_category = each_line[2]
            listing_image = each_line[3]
            listing_price = each_line[4]

            categories = listing_category.split(' ### ')
            # if category_tag in categories:
            print(listing_link)
            print(listing_name)
            # print(category_tag)
            print(listing_image)
            print(listing_price)
            print()

product_data = []
vehicle_tags = []

try:
    with open('map.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each_line in csvreader:
            vehicle_tag = each_line[0]
            listing_link = each_line[1]
            listing_name = each_line[2]
            listing_category = each_line[3]
            listing_image = each_line[4]
            listing_price = each_line[5]

            product_data.append((vehicle_tag, listing_link, listing_name, listing_category, listing_image, listing_price))
            vehicle_tags.append(vehicle_tag)

            # print(listing_link)
            # print(listing_name)
            # print(listing_category)
            # print(listing_image)
            # print(listing_price)
            # print()
except FileNotFoundError:
    print('Starting fresh...')

urotuning_URLs = json.loads(open('urotuning-urls.json').read())
for make in urotuning_URLs:
    for models in urotuning_URLs[make]:
        for model in models:
            for generations in models[model]:
                for generation in generations:
                    for vehicle_tag in generations[generation]:
                        try:
                            if vehicle_tag in vehicle_tags:
                                print(f'{vehicle_tag}: Match Found')
                                # map_site(vehicle_tag)
                            else:
                                print(f'{vehicle_tag}: Match Not Found')
                                map_site(vehicle_tag)
                        except (IndexError):
                            map_site(vehicle_tag)
                        except (JSONDecodeError, ValueError, TypeError):
                            pass
# test_results()