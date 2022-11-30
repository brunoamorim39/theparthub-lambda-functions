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

def save_to_file_categories(links):
    with open('categories.csv', 'w', newline='') as csvfile:
        fieldnames = ['category_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'category_url': link})

def find_vehicles():
    url = 'https://www.autohausaz.com/catalog/c'
    vehicle_links = []
    main_soup = getSoup(url, headers)
    vehicle_make_container = main_soup.find('div', class_='div-makes')
    vehicle_makes = vehicle_make_container.find_all('a', href=True)
    for each_make in vehicle_makes:
        vehicle_make_url = f'https://www.autohausaz.com{each_make["href"]}'
        print(f'> {vehicle_make_url}')

        vehicle_make_soup = getSoup(vehicle_make_url, headers)
        year_container = vehicle_make_soup.find('div', class_='div-years')
        years = year_container.find_all('a', href=True)
        for each_year in years:
            vehicle_year_url = f'https://www.autohausaz.com{each_year["href"]}'
            print(f'>> {vehicle_year_url}')

            year_soup = getSoup(vehicle_year_url, headers)
            models = year_soup.find_all('a', class_='div-model-row')
            for each in models:
                model_url = f'https://www.autohausaz.com{each["href"]}'
                trimmed_link = each["href"]
                print(f'===> {trimmed_link}')
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
            link = f'https://www.autohausaz.com{each_trimmed}'
            links_to_check.append(link)
            print(link)
    
    category_links = []
    for link in links_to_check:
        vehicle_soup = getSoup(link, headers)
        cat_container = vehicle_soup.find('div', class_='div-categories')
        categories = cat_container.find_all('a', href=True)
        for category in categories:
            cat_url = f'https://www.autohausaz.com{category["href"]}'
            trimmed_link = f"/{category['href'].split('/')[-1]}"

            if trimmed_link not in category_links:
                category_links.append(trimmed_link)
                print(f'=> {trimmed_link}')

            cat_soup = getSoup(cat_url, headers)
            subcats = cat_soup.find_all('a', class_='subcategory')
            for subcat in subcats:
                trimmed_link = f"/{subcat['href'].split('/')[-2]}/{subcat['href'].split('/')[-1]}"

                if trimmed_link not in category_links:
                    category_links.append(trimmed_link)
                    print(f'==> {trimmed_link}')
        save_to_file_categories(category_links)

# find_vehicles()
find_categories()