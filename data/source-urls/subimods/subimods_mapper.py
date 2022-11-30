import requests
from bs4 import BeautifulSoup
import csv

user_agent_desktop = 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36'
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp, image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Accept-Encoding': 'gzip',
'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

def getSoup(url, header):
    reqCount = 0
    while True:
        if reqCount > 4:
            return
        try:
            resp = requests.get(url, timeout=10, headers=header)
            soup = BeautifulSoup(resp.content, "html.parser")
            return soup
        except:
            reqCount += 1
            print('Trying again...')
            # traceback.print_exc()
            # headerCookie = getCookie()
            pass

def save_to_file_vehicles(links):
    with open('vehicles.csv', 'w', newline='') as csvfile:
        fieldnames = ['vehicle_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'vehicle_url': link})

def save_to_file_categories(links, names):
    with open('categories.csv', 'w', newline='') as csvfile:
        fieldnames = ['category_url', 'category_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        i = 0
        for link in links:
            writer.writerow({'category_url': link, 'category_name': names[i]})
            i += 1

def find_vehicles():
    url = 'https://subimods.com/?SID=8msotesp6kibgj8cvb4rog29k6'
    vehicle_links = []
    main_soup = getSoup(url, headers)
    vehicle_containers = main_soup.find_all('li', class_='level1')
    vehicles = []
    for each in vehicle_containers:
        vehicles.append(each.find('a', href=True))
    for vehicle in vehicles:
        model_link = vehicle['href']
        trimmed_link = f'/{model_link.split("/")[-2]}/{model_link.split("/")[-1]}'
        vehicle_links.append(trimmed_link)
        print(f'> {trimmed_link}')
    save_to_file_vehicles(vehicle_links[4:-19])

def find_categories():
    links_to_check = []
    with open('vehicles.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each in csvreader:
            each_trimmed = each[0].replace('[', '')
            each_trimmed = each_trimmed.replace(']', '')
            each_trimmed = each_trimmed.replace("'", '')
            link = f'https://subimods.com{each_trimmed}'
            links_to_check.append(link)
            print(link)

    category_links = []
    category_texts = []
    for link in links_to_check:
        vehicle_soup = getSoup(link, headers)
        cat_container = vehicle_soup.find('div', class_='category')
        try:
            category_units = cat_container.find_all('li', class_='item')
            categories = []
            for each in category_units:
                categories.append(each.find('a', href=True))
            for category in categories:
                cat_url = category['href']
                cat_text = category.contents[0].strip()
                trimmed_url = f'?{cat_url.split("?")[-1]}'
                if trimmed_url not in category_links:
                    print(f'=> {cat_text} = {trimmed_url}')
                    category_links.append(trimmed_url)
                    category_texts.append(cat_text)
                category_soup = getSoup(cat_url, headers)
                subcat_container = category_soup.find('div', class_='category')
                try:
                    subcategory_units = subcat_container.find_all('li', class_='item')
                    subcategories = []
                    for each in subcategory_units:
                        subcategories.append(each.find('a', href=True))
                    for subcategory in subcategories:
                        subcat_url = subcategory['href']
                        subcat_text = subcategory.contents[0].strip()
                        trimmed_suburl = f'?{subcat_url.split("?")[-1]}'
                        if trimmed_suburl not in category_links:
                            print(f'==> {subcat_text} = {trimmed_suburl}')
                            category_links.append(trimmed_suburl)
                            category_texts.append(subcat_text)
                except AttributeError as e:
                    print(f'No subcategories for {cat_text}')
        except AttributeError as e:
            print(e)

    save_to_file_categories(category_links, category_texts)

find_vehicles()
find_categories()