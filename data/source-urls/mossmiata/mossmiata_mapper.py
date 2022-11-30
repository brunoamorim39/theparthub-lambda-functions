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

def save_to_file_categories(links):
    with open('categories.csv', 'w', newline='') as csvfile:
        fieldnames = ['category_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'category_url': link})

def find_categories():
    links_to_check = [
        'https://mossmiata.com/1990-1997-miata',
        'https://mossmiata.com/1999-2005-miata',
        'https://mossmiata.com/2006-2015-mx-5-miata',
        'https://mossmiata.com/2016-2017-mx-5-miata'
    ]
    category_links = []
    for link in links_to_check:
        vehicle_soup = getSoup(link, headers)
        categories = vehicle_soup.find_all('div', class_='m-tree-item')
        for category in categories:
            cat_url = category.find('a', href=True)['href']
            split_link = cat_url.split('/')
            if len(split_link) == 5:
                trimmed_link = f"/{split_link[-1]}"
            elif len(split_link) == 6:
                trimmed_link = f"/{split_link[-2]}/{split_link[-1]}"
            
            if trimmed_link not in category_links:
                category_links.append(trimmed_link)
                print(f'=> {trimmed_link}')
    save_to_file_categories(category_links)

find_categories()