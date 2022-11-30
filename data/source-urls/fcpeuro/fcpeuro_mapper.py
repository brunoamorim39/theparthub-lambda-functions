import requests
import pandas as pd
from bs4 import BeautifulSoup
import csv


base_url = "https://www.fcpeuro.com"


headers = {
    "authority": "www.fcpeuro.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.fcpeuro.com/Volkswagen-parts/Beetle/?year=2019&m=5147&e=975&t=5&b=10&d=15792&v=",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
}


# Setting iter to 0, to get the headers in the 1st row
iter = 0
iter2 = 0


def saveInFile(data, filename):
    global iter
    df = pd.DataFrame(data, index=[0])
    if iter == 0:
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        iter = 1
    else:
        df.to_csv(filename, index=False, header=False, mode="a", encoding="utf-8-sig")


def saveInFile2(data, filename):
    global iter2
    df = pd.DataFrame(data, index=[0])
    if iter2 == 0:
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        iter2 = 1
    else:
        df.to_csv(filename, index=False, header=False, mode="a", encoding="utf-8-sig")


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


# Get response from url
def getResponse(url, request_type, headers, payload={}):
    reqCount = 0
    while True:
        if reqCount > 3:
            return
        try:
            reqCount += 1
            resp = requests.request(
                request_type.upper(), url, headers=headers, data=payload
            )
            if resp.status_code == 200:
                return resp
            else:
                continue
        except:
            # traceback.print_exc()
            # headerCookie = getCookie()
            pass


def getResultList(url):
    result_list = getResponse(url, "GET", headers).json()
    return result_list

def linkShaver(link):
    return link.split('?')[0]

# Collects vehicle URL's
inner_categories_list = set()
for year in reversed(range(1960, 2022)):
    # print(">", year)
    url = f"https://www.fcpeuro.com/frontend_api/makes.json?year={year}"
    for result1 in getResultList(url):
        # print(">>", result1)
        url = f"https://www.fcpeuro.com/frontend_api/base_vehicles.json?year={year}&make={result1['id']}"
        for result2 in getResultList(url):
            # print(">>>", result2)
            url = f"https://www.fcpeuro.com/frontend_api/vehicles.json?base_vehicle_id={result2['id']}"
            for result3 in getResultList(url):
                # print(">>>>", result3)
                url = f"https://www.fcpeuro.com/frontend_api/body_style_configs.json?vehicle_id={result3['id']}"
                for result4 in getResultList(url):
                    # print(">>>>>", result4)
                    url = f"https://www.fcpeuro.com/frontend_api/engine_configs.json?vehicle_id={result3['id']}&body_id={result4['id']}"
                    for result5 in getResultList(url):
                        # print(">>>>>>", result5)
                        url = f"https://www.fcpeuro.com/frontend_api/transmissions.json?vehicle_id={result3['id']}&body_id={result4['id']}&engine_ids={result5['id']}"
                        for result6 in getResultList(url):
                            # print(">>>>>>>", result6)

                            url = "https://www.fcpeuro.com/frontend_api/user/create_car_link.json"

                            payload = f"base_vehicle_id={result2['id']}&vehicle_id={result3['id']}&body_style_config_id={result4['id']}&engine_config_ids={result5['id']}&transmission_ids={result6['id']}"
                            post_resp = getResponse(url, "POST", headers, payload)
                            link_to_page = base_url + post_resp.json()["redirect"]

                            data = {
                                "year": year,
                                "make": result1["name"],
                                "model": result2["name"],
                                "sub_model": result3["name"],
                                "body": result4["name"],
                                "engine": result5["name"],
                                "transmission": result6["name"],
                                "link": link_to_page,
                            }
                            saveInFile(data, "results.csv")
                            print(link_to_page)

# Collects the category URL's from the vehicle URL's
print("---------- GETTING INNER CATEGORIES -----------")
urlList = []
with open('results.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        urlList.append(row['link'])

for link in urlList:
    link = linkShaver(link)
    print(link)
    soup = getSoup(link, headers)
    catList = soup.find('ul', class_='taxonList taxonList--hidden taxonList--browse')
    categories = catList.find_all('li')
    for each in categories:
        a = each.find('a', class_='taxonList__link')['href']
        cat_link = base_url + a
        print(">", cat_link)
        soup = getSoup(cat_link, headers)
        for a in soup.find_all("a", class_='taxonList__link'):
            cat_link = base_url + a["href"]
            print(">>", cat_link)
            soup = getSoup(cat_link, headers)
            for a in soup.find_all("a", class_='taxonList__link'):
                cat_link = base_url + a["href"]
                print(">>>", cat_link)
                inner_categories_list.add(cat_link)

    for link in inner_categories_list:
        data2 = {"Category_link": link}
        saveInFile2(data2, "inner_categories.csv")

# Trims vehicle CSV file to contain relevant URL tags
i = 0
trimmed_urls = []
urlList = pd.read_csv('collected_vehicles.csv', skiprows=1).values.tolist()
for row in urlList:
    trimmed_link = '/' + row[-1].split('/')[-3] + '/' + row[-1].split('/')[-2]
    if trimmed_link not in trimmed_urls:
        trimmed_urls.append(trimmed_link)
        print(f'({i}) {row[-1]}')
        print(f'    => {trimmed_link}')
        i += 1
    else:
        continue

for each_link in sorted(trimmed_urls, key=str.lower):
    csvdata = {'Vehicle_link' : each_link}
    saveInFile2(csvdata, 'vehicles.csv')

# Trims category CSV file to contain relevant URL tags
trimmed_urls = []
i = 1
urlList = pd.read_csv('inner_categories.csv', skiprows=1).values.tolist()

for link in urlList:
    trimmed_link = '/' + link[0].split('/')[-2]
    if trimmed_link not in trimmed_urls:
        trimmed_urls.append(trimmed_link)
        print(f'({i}) {link[0]}')
        print(f'    => {trimmed_link}')
        i += 1
    else:
        print('Category already exists. Moving on...')
        continue

for each_link in trimmed_urls:
    csvdata = {'Category_link': each_link}
    saveInFile2(csvdata, 'refined_categories.csv')