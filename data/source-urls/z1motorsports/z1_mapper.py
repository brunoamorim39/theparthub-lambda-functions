import requests
from bs4 import BeautifulSoup
import csv

user_agent_desktop = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
headers = {'User-Agent': user_agent_desktop}

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
            # traceback.print_exc()
            # headerCookie = getCookie()
            pass

def save_to_file_categories_oem(links):
    with open('categories_oem.csv', 'w', newline='') as csvfile:
        fieldnames = ['category_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'category_url': link})

def save_to_file_categories_performance(links):
    with open('categories_performance.csv', 'w', newline='') as csvfile:
        fieldnames = ['category_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'category_url': link})

def category_link_trimmer(link):
    trimmed_category_link = f'/{link.split("/")[-2]}/{link.split("/")[-1]}'
    return trimmed_category_link
    
def find_oem_categories():
    url = 'https://www.z1motorsports.com/oem-parts-c-4.html'

    category_links = []
    ground_level_soup = getSoup(url, headers)
    ground_level_elements = ground_level_soup.find_all('div', class_='categoryCard')
    level_1_links = []
    for each in ground_level_elements:
        level_1_links.append(each.find('a')['href'])
        print(f"> {each.find('a')['href']}")

    for level_1_link in level_1_links:
        level_1_soup = getSoup(level_1_link, headers)
        if level_1_soup.find('div', id='listing-page-con'):
            trimmed_link = category_link_trimmer(level_1_link)
            category_links.append(trimmed_link)
            print(f'=> {trimmed_link}')

        level_1_elements = level_1_soup.find_all('div', class_='categoryCard')
        level_2_links = []
        for each in level_1_elements:
            level_2_links.append(each.find('a')['href'])
            print(f">> {each.find('a')['href']}")

        for level_2_link in level_2_links:
            trimmed_link = category_link_trimmer(level_2_link)
            category_links.append(trimmed_link)
            print(f'==> {trimmed_link}')
    save_to_file_categories_oem(category_links)


def find_performance_categories():
    url = 'https://www.z1motorsports.com/performance-parts-c-6.html'
    
    category_links = []
    ground_level_soup = getSoup(url, headers)
    ground_level_elements = ground_level_soup.find_all('div', class_='categoryCard')
    level_1_links = []
    for each in ground_level_elements:
        level_1_links.append(each.find('a')['href'])
        print(f"> {each.find('a')['href']}")

    for level_1_link in level_1_links:
        level_1_soup = getSoup(level_1_link, headers)
        if level_1_soup.find('div', id='listing-page-con'):
            trimmed_link = category_link_trimmer(level_1_link)
            category_links.append(trimmed_link)
            print(f'=> {trimmed_link}')

        level_1_elements = level_1_soup.find_all('div', class_='categoryCard')
        level_2_links = []
        for each in level_1_elements:
            level_2_links.append(each.find('a')['href'])
            print(f">> {each.find('a')['href']}")

        for level_2_link in level_2_links:
            trimmed_link = category_link_trimmer(level_2_link)
            category_links.append(trimmed_link)
            print(f'==> {trimmed_link}')
    save_to_file_categories_performance(category_links)

find_oem_categories()
find_performance_categories()