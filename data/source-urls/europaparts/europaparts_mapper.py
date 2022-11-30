import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path

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

def save_to_file_categories(links):
    with open('categories.csv', 'w', newline='') as csvfile:
        fieldnames = ['category_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'category_url': link})

def find_vehicles():
    vehicle_links = []
    main_soup = getSoup(main_url, headers)
    makes = main_soup.find_all('a', class_='featured-make-link-image', href=True)
    for make in makes:
        make_link = make['href']
        make_soup = getSoup(make_link, headers)
        models = make_soup.find_all('a', class_='boxed-item-link small', href=True)
        for model in models:
            model_link = model['href']
            model_soup = getSoup(model_link, headers)
            years = model_soup.find_all('a', class_='boxed-item-link small', href=True)
            for year in years:
                year_link = year['href']
                year_soup = getSoup(year_link, headers)
                trims = year_soup.find_all('a', class_='boxed-item-link small', href=True)
                for trim in trims:
                    trim_link = trim['href']
                    trim_soup = getSoup(trim_link, headers)
                    bodies = trim_soup.find_all('a', class_='boxed-item-link small', href=True)
                    for body in bodies:
                        body_link = body['href']
                        body_soup = getSoup(body_link, headers)
                        engines = body_soup.find_all('a', class_='boxed-item-link small', href=True)
                        for engine in engines:
                            engine_link = engine['href']
                            engine_soup = getSoup(engine_link, headers)
                            transmissions = engine_soup.find_all('a', class_='boxed-item-link small', href=True)
                            for transmission in transmissions:
                                trans_link = transmission['href']
                                trimmed_link = f'/{trans_link.split("/")[-7]}/{trans_link.split("/")[-6]}/{trans_link.split("/")[-5]}/{trans_link.split("/")[-4]}/{trans_link.split("/")[-3]}/{trans_link.split("/")[-2]}/{trans_link.split("/")[-1][0:-5]}'
                                print(f'> {trimmed_link}')
                                vehicle_links.append(trimmed_link)
    save_to_file_vehicles(vehicle_links)

def find_categories():
    links_to_check = []
    with open('vehicles.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each in csvreader:
            each_trimmed = each[0].replace('[', '')
            each_trimmed = each_trimmed.replace(']', '')
            each_trimmed = each_trimmed.replace("'", '')
            link = f'{main_url}/{each_trimmed}'
            links_to_check.append(link)
            print(link)
    
    category_links = []
    for link in links_to_check:
        vehicle_soup = getSoup(link, headers)
        container = vehicle_soup.find_all('form', class_='am-ranges')[1]
        subcats = container.find_all('a', href=True)
        for subcat in subcats:
            subcat_link = subcat['href']
            trimmed_link = f'/{subcat_link.split("/")[-1]}'
            if trimmed_link not in category_links:
                print(f'=> {trimmed_link}')
                category_links.append(trimmed_link)
    save_to_file_categories(category_links)

main_url = 'https://www.europaparts.com'

url_file = Path('europaparts-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path('europaparts-cats.json')
cat_file.touch(exist_ok=True)

# find_vehicles()
find_categories()