from bs4 import BeautifulSoup
import csv
import json
import os
import paramiko
import pickle
import random
import re
import requests
from requests import HTTPAdapter, Retry
import time
import yagmail

from application.models import Make, Model, Category, Subcategory, Part, Classification
from application.__init__ import db

def sleep_scraper():
    time.sleep(random.uniform(3, 8))
    return

def get_image(directory, listing_image, image_filename):
    try:
        image_response = requests.get(listing_image, timeout=10, headers=headers)
        if image_response.status_code == 200:
            image_file = open(image_filename, 'wb')
            image_file.write(image_response.content)
            image_file.close()
            sftp = ssh.open_sftp()
            sftp.get_channel().settimeout(None)
            sftp.put(image_filename, f'theparthub/application/static/images/thumbnails/{directory}/{image_filename}')
            sftp.close()
            print('Copied image successfully')
            return image_filename
        else:
            image_filename = 'missing_image.jpg'
            return image_filename
    except ConnectionError:
        print('Connection error - retrying connection in 10-15 seconds')
        time.sleep(random.uniform(10, 15))
        return get_image(directory, listing_image, image_filename)

# iterateCycle is responsible for properly iterating through the data sources and saving the positions so that they may be accessed again
def iterateCycle(load_location, save_index, url_json, cat_json, website, designation):
    # Initializes variables for determining subsequent passthroughs of the loop
    newMake = 0
    newModel = 0
    newVehicle = 0
    newCategory = 0
    newSubCategory = 0

    # Iterates over the makes in the url json and only allows passing if the position is at or greater than the loaded position
    for make in url_json:
        if list(url_json).index(make) >= list(url_json).index(load_location[0]):
            load_location[0] = list(url_json)[0]

            # Iterates over the models for each make and only allows passing if the position is at or greater than the loaded position
            for models in url_json[make]:
                for model in models:
                    if newMake == 1 or list(models).index(model) >= list(models).index(load_location[1]):
                        load_location[1] = list(models)[0]

                        # Iterates over the generations for each model and only allows passing if the position is at or greater than the loaded position
                        for generations in models[model]:
                            for generation in generations:
                                if newModel == 1 or list(generations).index(generation) >= list(generations).index(load_location[2]):
                                    load_location[2] = list(generations)[0]

                                    # Iterates over the vehicle tags for each generation and only allows passing if the position is at or greater than the loaded position
                                    for vehicle_tag in generations[generation]:
                                        if newVehicle == 1 or vehicle_tag >= load_location[3]:
                                            load_location[3] = list(generations[generation])[0]

                                            # Iterates over the categories in the category json and only allows passing if the position is at or greater than the loaded position
                                            for category in cat_json:
                                                if list(cat_json).index(category) >= list(cat_json).index(load_location[4]):
                                                    load_location[4] = list(cat_json)[0]

                                                    # Iterates over the subcategories for each category and only allows passing if the position is at or greater than the loaded position
                                                    for subcategories in cat_json[category]:
                                                        for subcategory in subcategories:
                                                            if newCategory == 1 or subcategory >= load_location[5]:
                                                                load_location[5] = list(subcategories)[0]

                                                                # Iterates over the category tags for each subcategory and only allows passing if the position is at or greater than the loaded position
                                                                for category_tag in subcategories[subcategory]:
                                                                    if newSubCategory == 1 or category_tag >= load_location[6]:
                                                                        load_location[6] = list(subcategories[subcategory])[0]

                                                                        # Prints current destination and calls scraping function
                                                                        print('Now scraping for: ' + generation + ' ' + make + ' ' + model + ': ' + subcategory + ' in ' + category)
                                                                        print()
                                                                        scraper = f'scrape_{designation}'
                                                                        eval(scraper + '(make, model, generation, vehicle_tag, category, subcategory, category_tag)')

                                                                        # Creates the save state and writes it to the pickled file in case of early termination
                                                                        save_location = [make, model, generation, vehicle_tag, category, subcategory, category_tag]
                                                                        save_file = open(f'saves/{website}_{save_index}', 'wb')
                                                                        pickle.dump(save_location, save_file)
                                                                        save_file.close()
                                                                newSubCategory = 1
                                                    newCategory = 1
                                    newVehicle = 1
                        newModel = 1
            newMake = 1

                                            #################################
                                            ### Source Scraping Functions ###
                                            #################################

# ECS_Scrape serves to scrape the appropriate data from ECSTuning.com, utilizing links from ecstuning-urls.json and ecstuning-cats.json
def scrape_ecs(make, model, generation, vehicle_tag, category, subcategory, category_tag):
    '''
    Scrapes listing information from ECStuning.com regarding a link to the product, the product thumbnail, title, details, and price
    '''
    baseURL = 'https://www.ecstuning.com'    
    
    URL = baseURL + vehicle_tag + category_tag
    print(URL)
    
    page = requests.get(URL, timeout=None, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    redirectCheck = soup.find('link', href=URL+'/')
    if redirectCheck is None:
        return

    listings = soup.find_all('div', class_='productListBox')

    # Iterates through all of the listings displayed on the page
    for listing in listings:
        os.chdir(baseDir + '/application/static/images/thumbnails/ecstuning')

        # Parses through each listing to find the relevant classes
        link = listing.find('a', href=True)
        thumbnail = listing.find('img', {'src':re.compile('.jpg')})
        title = listing.find('span', class_='cleanDesc productTitle')
        price = listing.find('span', class_='price')

        # Set text in variables to add to the database
        partLink = baseURL + link['href']
        partName = title.text.strip()

        if price is not None:
            partPrice = price.text.strip()
            priceTrim = partPrice.split('at')
            priceTrim = priceTrim[-1].split(' ')
            partPrice = priceTrim[-1]
        else:
            os.chdir(baseDir)
            continue

        # Prints the relevant information for each listing
        print(partLink)

        if thumbnail is not None:
            partPicLink = thumbnail['src']
            print(partPicLink)

            TrimmedImageURL = partPicLink.split('/')
            TrimmedImageURL = TrimmedImageURL[-1]
            partPic = TrimmedImageURL.split('.')
            partPic = partName + partPic[0] + '.jpg'
            partPic = partPic.replace(' ', '')
            partPic = partPic.replace('/', '')
            partPic = partPic.replace("'", '')
            partPic = partPic.replace('"', '')

            # Exception handler for missing thumbnails
            try:
                partResponse = requests.get(partPicLink, timeout=None, headers=headers)
                picFile = open(partPic, 'wb')
                picFile.write(partResponse.content)
                picFile.close()

                sftp = ssh.open_sftp()
                sftp.get_channel().settimeout(None)
                sftp.put(partPic, f'theparthub/application/static/images/thumbnails/ecstuning/{partPic}')
                sftp.close()
                print('Image copied successfully')

                print(picFile)
            except OSError as e:
                print(e.errno)
        else:
            partPic = 'missing_image.jpg'
            print(partPic)
        
        print(partName)
        print(partPrice)
        print()
        writeToDatabase(partLink, partName, partPrice, partPic, 'ecs-tuning.png', make, model, generation, category, subcategory)
    return
  
# FCP_Scrape serves to scrape the appropriate data from FCPEuro.com, utilizing links from fcpeuro-urls.json and fcpeuro-cats.json
def scrape_fcp(make, model, generation, vehicle_tag, category, subcategory, category_tag):
    '''
    Scrapes listing information from ECStuning.com regarding a link to the product, the product thumbnail, title, details, and price
    '''
    baseURL = 'https://www.fcpeuro.com'
    imageDir = baseDir + '/application/static/images/thumbnails/fcpeuro'

    newURL = baseURL + vehicle_tag + category_tag
    print(newURL)
    response = requests.get(newURL, timeout=None, headers=headers)

    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    if soup.find('h1', class_='browse__heading browse__heading--failed') is not None:
        print('Nothing found. Moving on to the next search...')
        print()
        os.chdir(baseDir)
        return
    listings = soup.find_all('div', class_='grid-x hit')

    # Iterates through the page listings and gathers data from each one
    print('Found Listings! Scraping data for ' + str(len(listings)) + ' elements')
    for listing in listings:
        os.chdir(imageDir)

        link = listing.find('a', class_='hit__name')
        partLink = baseURL + link['href']

        partTitle = link.text.strip()

        price = listing.find('span', class_='hit__money')
        if price is not None:
            partPrice = price.text.strip()
        else:
            os.chdir(baseDir)
            continue
        
        listingContent = BeautifulSoup(requests.get(partLink, timeout=None, headers=headers).content, 'html.parser')
        if listingContent.find('img', class_='listing__mainImage') is not None:
            imageURL = listingContent.find('img', class_='listing__mainImage')['src']
            imagePath = imageURL.replace(' ', '')
            imagePath = imagePath.split('/')
            imagePath = imagePath[-1]
            imagePath = imagePath.split('?')
            imagePath = imagePath[0]
            if imagePath[-1] == '.':
                imagePath = imagePath + 'webp'
        elif listingContent.find('div', class_='error__404') is not None:
            print('Part seems to not exist. Continuing on...')
            continue
        else:
            imageContainer = listingContent.find('div', class_='listing__gallery')
            imageURL = imageContainer.find('img')['src']
            imagePath = imageURL.replace(' ', '')
            imagePath = imagePath.split('/')
            imagePath = imagePath[-1]
        
        # Exception handler for missing thumbnails
        missingImage = 'missing_image.jpg'
        try:
            partResponse = requests.get(imageURL, timeout=None, headers=headers)
            picFile = open(imagePath, 'wb')
            picFile.write(partResponse.content)

            sftp = ssh.open_sftp()
            sftp.get_channel().settimeout(None)
            sftp.put(imagePath, f'theparthub/application/static/images/thumbnails/fcpeuro/{imagePath}')
            sftp.close()
            print('Image copied successfully')

            picFile.close()
        except OSError as e:
            print(e.errno)

        # Prints to console the link, title, price, and path of the saved thumbnail for each listing
        print(partLink)
        print(partTitle)
        print(partPrice)
        if partResponse.status_code != 200:
            imagePath = missingImage
            print(imagePath)
        else:
            print(imagePath)
        print()

        # Uses BeautifulSoup to analyze the page and find the fitment elements
        fitmentPage = requests.get(partLink + '/extended.html', timeout=None, headers=headers)
        soup = BeautifulSoup(fitmentPage.content, 'html.parser')

        fitmentList = soup.find_all(class_='fitmentGuide__application')

        # If there are 0 applications, write to database anyways due to the likelihood that the item is universal
        written = 0
        if len(fitmentList) == 0:
            writeToDatabase(partLink, partTitle, partPrice, imagePath, 'fcp-euro.jpg', make, model, generation, category, subcategory)
            written = 1

        # Pulls information from the database to check whether the listed year falls within the generation or not
        makeData = Make.query.filter_by(name=make).first()
        modelData = Model.query.filter_by(make_id=makeData.id, name=model, generation=generation).first()

        print('Checking for: ' + modelData.first + ' - ' + modelData.last + ' ' + make + ' ' + model)
        print()

        # Iterates through each of the vehicle applications in the fitment list to verify that at least one matches the criteria that we're looking for
        checkCount = 0
        for vehicle in fitmentList:
            application = vehicle.text.strip()
            splitApplication = application.split(' ')
            checkYear = splitApplication[0]
            checkMake = splitApplication[1]
            checkModel = splitApplication[2]

            if splitApplication[3] == 'allroad':
                checkModel = splitApplication[2] + ' Allroad'

            print(checkYear + ' ' + checkMake + ' ' + checkModel)

            # Verifies whether or not the listed year is within first and last years of the generation and whether the names of the models match
            if int(checkYear) >= int(modelData.first) and int(checkYear) <= int(modelData.last) and checkModel == modelData.name:
                print('Year falls within model generation criteria')
                checkCount += 1
            # elif int(checkYear) >= int(modelData.first) and int(checkYear) <= int(modelData.last) and makeData.name == 'BMW' and checkModel[0] == modelData.name[0]:
            #     print('Year falls within model generation criteria')
            #     checkCount += 1

        # Checks to verify that at least one application matches the model we're collecting data for and then if so, writes the listing data to the database        
        if checkCount > 0:
            print('Writing to database...')
            print()
            writeToDatabase(partLink, partTitle, partPrice, imagePath, 'fcp-euro.jpg', make, model, generation, category, subcategory)
        elif written == 1:
            print('Has been written to database')
            print()
        else:
            print('Will not be written to database')
            print()
            os.chdir(baseDir)
    return

# BW_Scrape serves to scrape the appropriate data from BimmerWorld.com, utilizing links from bimmerworld-urls.json and bimmerworld-cats.json
def scrape_bw(make, model, generation, vehicle_tag, category, subcategory, category_tag):
    '''
    Scrapes listing information from bimmerworld.com regarding a link to the product, the product thumbnail, title, details, and price
    '''
    baseURL = 'https://www.bimmerworld.com'
    imageDir = baseDir + '/application/static/images/thumbnails/bimmerworld'

    newURL = baseURL + category_tag + vehicle_tag 
    print(newURL)
    response = requests.get(newURL, timeout=None, headers=headers)

    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    if soup.find('div', class_='performance-part'):
        return
    
    listings = soup.find_all('div', class_='product-info')

    # Iterates through the page listings and gathers data from each one
    print('Found Listings! Scraping data for ' + str(len(listings)) + ' elements')
    for listing in listings:
        os.chdir(imageDir)

        link = listing.find('a', href=True)
        title = listing.find('div', class_='product-title')
        price = listing.find('span', class_='current')

        partLink = baseURL + link['href']
        partName = title.text.strip()

        if price is not None:
            partPrice_preTrim = price.text.strip()
            partPrice_preTrim = partPrice_preTrim.split(' ')
            partPrice = partPrice_preTrim[-1]
        else:
            os.chdir(baseDir)
            continue

        print(partLink)

        # BeautifulSoup downloads the html for each individual listing in order to grab the images of the items
        listingPage = requests.get(partLink, timeout=None, headers=headers)
        soup = BeautifulSoup(listingPage.content, 'html.parser')

        if soup.find('img', class_='zoom') is not None:
            thumbnail = soup.find('img', class_='zoom')['src']
            partPicLink = baseURL + thumbnail
            print(partPicLink)

            TrimmedImageURL = partPicLink.split('/')
            TrimmedImageURL = TrimmedImageURL[-1]
            partPic = TrimmedImageURL.split('.')
            partPic = partPic[0] + '.jpg'
            partPic = partPic.replace('/', '')

            # Exception handler for missing thumbnails
            try:
                if partPic == 'www.jpg':
                    partPic = 'missing_image.jpg'
                    print(partPic)
                else:
                    partResponse = requests.get(partPicLink, timeout=None, headers=headers)
                    if partResponse.status_code == 404:
                        partPic = 'missing_image.jpg'
                        print(partPic)
                    else:
                        picFile = open(partPic, 'wb')
                        picFile.write(partResponse.content)
                        picFile.close()

                        sftp = ssh.open_sftp()
                        sftp.get_channel().settimeout(None)
                        sftp.put(partPic, f'theparthub/application/static/images/thumbnails/bimmerworld/{partPic}')
                        sftp.close()
                        print('Image copied successfully')

                        print(picFile)
            except OSError as e:
                print(e.errno)
        else:
            partPic = 'missing_image.jpg'
            print(partPic)

        print(partName)
        print(partPrice)
        print()
        writeToDatabase(partLink, partName, partPrice, partPic, 'bimmerworld.jpg', make, model, generation, category, subcategory)
    return

# TM_Scrape serves to scrape the appropriate data from TurnerMotorsport.com, utilizing links from turnermotorsport-urls.json and turnermotorsport-cats.json
def scrape_tm(make, model, generation, vehicle_tag, category, subcategory, category_tag):
    '''
    Scrapes listing information from turnermotorsport.com regarding a link to the product, the product thumbnail, title, details, and price
    '''
    baseURL = 'https://www.turnermotorsport.com'
    imageDir = baseDir + '/application/static/images/thumbnails/turnermotorsport'

    newURL = baseURL + vehicle_tag + category_tag
    print(newURL)
    response = requests.get(newURL, timeout=None, headers=headers)

    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    listings = soup.find_all('div', class_='product-item')

    # Iterates through the page listings and gathers data from each one
    print('Found Listings! Scraping data for ' + str(len(listings)) + ' elements')
    for listing in listings:
        os.chdir(imageDir)

        link = listing.find('a', class_='cleanDesc', href=True)
        price = listing.find('span', class_='price')
        partLink = baseURL + link['href']
        
        if price is not None:
            partPrice = price.text.strip()
            priceTrim = partPrice.split(' ')
            partPrice = priceTrim[-1]
        else:
            os.chdir(baseDir)
            continue

        print(partLink)

        # BeautifulSoup downloads the html for each individual listing in order to grab the images of the items
        listingPage = requests.get(partLink, timeout=None, headers=headers)
        if listingPage.url != partLink:
            os.chdir(baseDir)
            return
        soup = BeautifulSoup(listingPage.content, 'html.parser')

        pageNotExistMessage = 'Sorry, looks like we got distracted and forgot to build this page.'
        if soup.find('div', class_='title') is not None and soup.find('div', class_='title').text.strip() == pageNotExistMessage:
            os.chdir(baseDir)
            return

        title = soup.find('h1', class_='m-0 product-name cleanDesc js-title')
        partName = title.text.strip()

        thumbnailZone = soup.find('a', class_='product-main-image')
        if thumbnailZone is not None:
            thumbnail = thumbnailZone.find('img')['data-src']
            partPicLink = thumbnail
            print(partPicLink)

            TrimmedImageURL = partPicLink.split('/')
            TrimmedImageURL = TrimmedImageURL[-1]
            partPic = TrimmedImageURL.split('.')
            partPic = partPic[0] + '.jpg'
            partPic = partPic.replace('/', '')

            # Exception handler for missing thumbnails
            try:
                if partPic == 'www.jpg':
                    partPic = 'missing_image.jpg'
                    print(partPic)
                else:
                    partResponse = requests.get(partPicLink, timeout=None, headers=headers)
                    if partResponse.status_code == 404:
                        partPic = 'missing_image.jpg'
                        print(partPic)
                    else:
                        picFile = open(partPic, 'wb')
                        picFile.write(partResponse.content)
                        picFile.close()

                        sftp = ssh.open_sftp()
                        sftp.get_channel().settimeout(None)
                        sftp.put(partPic, f'theparthub/application/static/images/thumbnails/turnermotorsport/{partPic}')
                        sftp.close()
                        print('Image copied successfully')

                        print(picFile)
            except OSError as e:
                print(e.errno)
        else:
            partPic = 'missing_image.jpg'
            print(partPic)

        print(partName)
        print(partPrice)
        print()
        writeToDatabase(partLink, partName, partPrice, partPic, 'turner-motorsport.png', make, model, generation, category, subcategory)
    return

# OhThirtyFour_Scrape serves to scrape the appropriate data from 034motorsport.com, utilizing links from 034motorsport-urls.json and 034motorsport-cats.json
def scrape_034(make, model, generation, vehicle_tag, category, subcategory, category_tag):
    '''
    Scrapes listing information from 034motorsport.com regarding a link to the product, the product thumbnail, title, details, and price
    '''
    baseURL = 'https://store.034motorsport.com'
    imageDir = baseDir + '/application/static/images/thumbnails/034motorsport'
    
    newURL = baseURL + vehicle_tag + category_tag
    print(newURL)
    response = requests.get(newURL, timeout=None, headers=headers)

    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    listings = soup.find_all('li', class_='item last')

    # Iterates through the page listings and gathers data from each one
    print('Found Listings! Scraping data for ' + str(len(listings)) + ' elements')
    for listing in listings:
        os.chdir(imageDir)

        nameZone = listing.find('h2', class_='product-name')
        link = nameZone.find('a', href=True)
        partName = link.text.strip()

        priceZone = listing.find('div', class_='price-box')
        if priceZone.find('p', class_='special-price') is not None:
            priceTag = priceZone.find('p', class_='special-price')
            price = priceTag.find('span', class_='price')
        elif priceZone.find('p', class_='minimal-price') is not None:
            price = priceZone.find('span', class_='price')
        else:
            priceTag = priceZone.find('span', class_='regular-price')
            price = priceTag.find('span', class_='price')

        partLink = link['href']
        
        if price is not None:
            partPrice = price.text.strip()
        else:
            os.chdir(baseDir)
            continue

        print(partLink)

        thumbnailZone = listing.find('a', class_="product-image")
        if thumbnailZone is not None:
            thumbnail = thumbnailZone.find('img')['src']
            partPicLink = thumbnail
            print(partPicLink)

            TrimmedImageURL = partPicLink.split('/')
            TrimmedImageURL = TrimmedImageURL[-1]
            partPic = TrimmedImageURL.replace('.', '-')
            partPic = partPic + '.jpg'
            partPic = partPic.replace('/', '')

            # Exception handler for missing thumbnails
            try:
                if partPic == 'www.jpg':
                    partPic = 'missing_image.jpg'
                    print(partPic)
                else:
                    partResponse = requests.get(partPicLink, timeout=None, headers=headers)
                    if partResponse.status_code == 404:
                        partPic = 'missing_image.jpg'
                        print(partPic)
                    else:
                        picFile = open(partPic, 'wb')
                        picFile.write(partResponse.content)
                        picFile.close()

                        sftp = ssh.open_sftp()
                        sftp.get_channel().settimeout(None)
                        sftp.put(partPic, f'theparthub/application/static/images/thumbnails/034motorsport/{partPic}')
                        sftp.close()
                        print('Image copied successfully')

                        print(picFile)
            except OSError as e:
                print(e.errno)
        else:
            partPic = 'missing_image.jpg'
            print(partPic)

        print(partName)
        print(partPrice)
        print()
        writeToDatabase(partLink, partName, partPrice, partPic, '034-motorsport.png', make, model, generation, category, subcategory)
    return

# scrape_uro serves to scrape the appropriate data from urotuning.com, utilizing links from urotuning-urls.json and urotuning-cats.json
def scrape_uro(make, model, generation, vehicle_tag, category, subcategory, category_tag):
    '''
    Scrapes part information from urotuning.com and adds it to database. This website was built using shopify, and therefore requires consolidation of the product data into a CSV file beforehand.
    '''
    baseURL = 'https://www.urotuning.com'
    imageDir = baseDir + '/application/static/images/thumbnails/urotuning'

    with open('map.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each_line in csvreader:
            listing_tag = each_line[0]
            listing_link = each_line[1]
            listing_name = each_line[2]
            listing_category = each_line[3]
            listing_image = each_line[4]
            listing_price = each_line[5]

            categories = listing_category.split(' ### ')

            # Verifies that vehicle tag is equal to that of each listing item and verifies existence of interested category in the categories for each listing
            if vehicle_tag == listing_tag and category_tag in categories:
                print(listing_tag)
                print(listing_link)
                print(listing_name)
                print(category_tag)
                print(listing_image)
                print(listing_price)

                # Downloads listing image to the local directory for the vendor
                os.chdir(imageDir)
                image_filename = listing_image.split('/')[-1]
                image_filename = get_image('urotuning', listing_image, image_filename)

                # def get_image(directory, listing_image, image_filename):
                #     try:
                #         image_response = requests.get(listing_image, timeout=10, headers=headers)
                #         if image_response.status_code == 200:
                #             image_file = open(image_filename, 'wb')
                #             image_file.write(image_response.content)
                #             image_file.close()

                #             # Transfer protocol for moving image to server machine
                #             sftp = ssh.open_sftp()
                #             sftp.get_channel().settimeout(None)
                #             sftp.put(image_filename, f'theparthub/application/static/images/thumbnails/{directory}/{image_filename}')
                #             sftp.close()
                #             print('Copied image successfully')
                #             return image_filename
                #         else:
                #             image_filename = 'missing_image.jpg'
                #             return image_filename

                #     except ConnectionError:
                #         print('Connection error - retrying connection in 10-15 seconds')
                #         time.sleep(random.uniform(10, 15))
                #         return get_image(directory, listing_image, image_filename)
                
                print()
                writeToDatabase(listing_link, listing_name, listing_price, image_filename, 'urotuning.png', make, model, generation, category, subcategory)

    # # Initializes variables for determining subsequent passthroughs of the loop
    # newMake = 0
    # newModel = 0
    # newVehicle = 0
    # newCategory = 0
    # newSubCategory = 0

    # # Majority of this is the handling of loading save files for the scraper
    # for make in urls_json:
    #     if list(urls_json).index(make) >= list(urls_json).index(load_location[0]):
    #         load_location[0] = list(urls_json)[0]
    #         for models in urls_json[make]:
    #             for model in models:
    #                 if newMake == 1 or list(models).index(model) >= list(models).index(load_location[1]):
    #                     load_location[1] = list(models)[0]
    #                     for generations in models[model]:
    #                         for generation in generations:
    #                             if newModel == 1 or list(generations).index(generation) >= list(generations).index(load_location[2]):
    #                                 load_location[2] = list(generations)[0]
    #                                 for vehicle_tag in generations[generation]:
    #                                     if newVehicle == 1 or vehicle_tag >= load_location[3]:
    #                                         load_location[3] = list(generations[generation])[0]

    #                                         # Begin scraper
    #                                         newURL = baseURL + vehicle_tag + '/products.json?limit=250'
    #                                         page = 1
                                            
    #                                         while True:
    #                                             print(newURL + f'&page={page}')
    #                                             listings = requests.get(newURL + f'&page={page}', timeout=None, headers=headers).json()

    #                                             # Check to see if there are entries on the page of the JSON file being requested
    #                                             if len(listings['products']) == 0:
    #                                                 break
                                                
    #                                             for listing in listings['products']:
    #                                                 listing_categories = listing['product_type'].split(' ### ')
    #                                                 for each_category in listing_categories:
    #                                                     for category in cats_json:
    #                                                         if list(cats_json).index(category) >= list(cats_json).index(load_location[4]):
    #                                                             load_location[4] = list(cats_json)[0]
    #                                                             for subcategories in cats_json[category]:
    #                                                                 for subcategory in subcategories:
    #                                                                     if newCategory == 1 or subcategory >= load_location[5]:
    #                                                                         load_location[5] = list(subcategories)[0]
    #                                                                         for category_tag in subcategories[subcategory]:
    #                                                                             if newSubCategory == 1 or category_tag >= load_location[6]:
    #                                                                                 load_location[6] = list(subcategories[subcategory])[0]
    #                                                                                 if category_tag == each_category:
    #                                                                                     title = listing['title']
    #                                                                                     handle = listing['handle']
    #                                                                                     print(f'Matched {each_category} with {category_tag}')

    #                                                                                     if len(listing['images']) > 0:
    #                                                                                         os.chdir(imageDir)
    #                                                                                         imageURL = listing['images'][0]['src']
    #                                                                                         imagePath = imageURL.split('/')
    #                                                                                         imagePath = imagePath[-1]
    #                                                                                         imagePath = imagePath.split('?')
    #                                                                                         imagePath = imagePath[0]
    #                                                                                         if imagePath[-1] == '.':
    #                                                                                             imagePath = imagePath + 'webp'
    #                                                                                         splitImage = imagePath.split('.')
    #                                                                                         imagePath = splitImage[-2] + '.' + splitImage[-1]

    #                                                                                         imageResponse = requests.get(imageURL, timeout=None, headers=headers)
    #                                                                                         imageFile = open(imagePath, 'wb')
    #                                                                                         imageFile.write(imageResponse.content)
    #                                                                                         imageFile.close()

    #                                                                                         sftp = ssh.open_sftp()
    #                                                                                         sftp.get_channel().settimeout(None)
    #                                                                                         sftp.put(imagePath, f'theparthub/application/static/images/thumbnails/urotuning/{imagePath}')
    #                                                                                         sftp.close()
    #                                                                                         print('Image copied successfully')
    #                                                                                     else:
    #                                                                                         imagePath = 'missing_image.jpg'
    #                                                                                         print(imagePath)

    #                                                                                     print('==================================================')

    #                                                                                     for variant in listing['variants']:
    #                                                                                         variantID = variant['id']
    #                                                                                         link = f'{baseURL}/products/{handle}?variant={variantID}'
    #                                                                                         variantPrice = variant['price']
    #                                                                                         price = f'${variantPrice}'
                                                                                            
    #                                                                                         print(title)
    #                                                                                         print(link)
    #                                                                                         print(imagePath)
    #                                                                                         print(price)
    #                                                                                         print()
    #                                                                                         writeToDatabase(link, title, price, imagePath, 'urotuning.png', make, model, generation, category, subcategory)

    #                                                                             # Creates the save state and writes it to the pickled file in case of early termination
    #                                                                             save_location = [make, model, generation, vehicle_tag, category, subcategory, category_tag]
    #                                                                             save_file = open(f'saves/urotuning_{save_index}', 'wb')
    #                                                                             pickle.dump(save_location, save_file)
    #                                                                             save_file.close()
    #                                                                         newSubCategory = 1
    #                                                             newCategory = 1
    #                                             # Sleeps the scraper for 1.1 seconds and then moves to the next page
    #                                             time.sleep(1.1)
    #                                             page += 1
    #                                 newVehicle = 1
    #                     newModel = 1
    #         newMake = 1
    return

def scrape_ahaz(make, model, generation, vehicle_tag, category, subcategory, category_tag):
    '''
    Scrapes part information from autohausaz.com and adds it to database based on the URL morsels fed to it from the JSON files created for hosting the vehicle and category data.
    '''
    baseURL = 'https://www.autohausaz.com'
    imageDir = baseDir + '/application/static/images/thumbnails/autohausaz'

    newURL = baseURL + vehicle_tag + category_tag
    print(newURL)
    response = requests.get(newURL, timeout=None, headers=headers)

    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    listingContainer = soup.find('div', id='div-partlist-content')
    listings = listingContainer.find_all('div', class_='div-part')

    print('Found Listings! Scraping data for ' + str(len(listings)) + ' listings')
    print('==================================================')
    for listing in listings:
        os.chdir(imageDir)

        partInfo = listing.find('div', class_='div-part-info')
        link = baseURL + partInfo.find('a', href=True)['href']
        title = f"{partInfo.find('div', class_='name').text.strip()} ({partInfo.find('a', href=True).text.strip()})"

        partImage = listing.find('div', class_='div-part-image-container')
        imageURL = baseURL + partImage.find('a', href=True)['href']
        imagePath = imageURL.split('/')[-1]
        if requests.get(imageURL, timeout=None, headers=headers).status_code == 200:
            imageResponse = requests.get(imageURL, timeout=None, headers=headers)
            imageFile = open(imagePath, 'wb')
            imageFile.write(imageResponse.content)
            imageFile.close()

            sftp = ssh.open_sftp()
            sftp.get_channel().settimeout(None)
            sftp.put(imagePath, f'theparthub/application/static/images/thumbnails/autohausaz/{imagePath}')
            sftp.close()
            print('Image copied successfully')
        else:
            imagePath = 'missing_image.jpg'

        if listing.find('div', class_='div-part-price sale'):
            partPrice = listing.find('div', class_='div-part-price sale')
        else:
            partPrice = listing.find('div', class_='div-part-price regular')
        price = partPrice.find('div', class_='price').text.strip()
        
        print(link)
        print(title)
        print(imagePath)
        print(price)
        print()
        writeToDatabase(link, title, price, imagePath, 'autohausaz.png', make, model, generation, category, subcategory)

def scrape_autozone(make, model, generation, vehicle_tag, category, subcategory, category_tag):
    '''
    Scrapes part information from autozone.com and adds it to the database based on URL morsels fed to it from JSON files created for hosting the vehicle and category data.
    '''
    baseURL = 'https://www.autozone.com'
    imageDir = baseDir + '/application/static/images/thumbnails/autozone'

    newURL = baseURL + category_tag + vehicle_tag
    print(newURL)
    sleep_scraper()
    response = requests.get(newURL, timeout=None, headers=headers)

    if response.status_code != 200:
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    listings = soup.find_all('div', class_='c70ed0')

    print(f'Found Listings! Scraping data for {str(len(listings))} listings')
    print('==================================================')
    for listing in listings:
        os.chdir(imageDir)

        part_link_element = listing.find('a', class_='ec324a', href=True)

        part_link = part_link_element['href']
        part_title = part_link_element.find('h3', id='productTitle').text.strip()

        part_image = listing.find('img', id='productImage')
        image_filename = part_title.replace(' ', '') + part_image['href'].split('/')[-1]
        # image_filename = get_image('autozone', part_image, image_filename)

        # try:
        #     sleep_scraper()
        #     image_request = requests.get(part_image['href'], timeout=None, headers=headers).content
        #     image_file = open(image_filename, 'wb')
        #     image_file.write(image_request)
        #     image_file.close()

        #     sftp = ssh.open_sftp()
        #     sftp.get_channel().settimeout(None)
        #     sftp.put(image_filename, f'theparthub/application/static/images/thumbnails/autozone/{image_filename}')
        #     sftp.close()
        #     print('Image copied successfully')
        # except AttributeError as e:
        #     image_filename = 'missing_image.jpg'
        
        part_price = listing.find('div', id='priceContainer').text.strip()

        print(part_link)
        print(part_title)
        print(image_filename)
        print(part_price)
        print()
        # writeToDatabase(part_link, part_title, part_price, image_filename, 'autozone.png', make, model, generation, category, subcategory)

def scrape_moss(make, model, generation, vehicle_tag, category, subcategory, category_tag):
    '''
    Scrapes part information from mossmiata.com and adds it to the database based on URL tags that are fed to it from the JSON files created for hosting the vehicle and category data.
    '''
    base_url = 'https://www.mossmiata.com'
    image_dir = base_url + '/application/static/images/thumbnails/mossmiata'

    new_url = base_url + vehicle_tag + category_tag
    print(new_url)
    sleep_scraper()
    response = requests.get(new_url, timeout=None, headers=headers)

    if response.status_code != 200:
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    listings = soup.find_all('li', class_='item last')
    print(f'Found Listings! Scraping data for {str(len(listings))} listings')
    print('==================================================')
    for listing in listings:
        os.chdir(image_dir)
        link_element = listing.find('h2', class_='product-name').find('a', href=True)
        part_link = link_element['href']
        part_title = link_element.text.strip()

        part_pricebox = listing.find('div', class_='price-box')
        try:
            part_price = part_pricebox.find('span', class_='regular-price').text.strip()
        except AttributeError:
            part_price = part_pricebox.find('span', class_='special-price').text.strip()

        part_image = listing.find('a', class_='product-image', href=True).find('img')
        image_filename = part_image['src'].split('/')[-3] + part_image['src'].split('/')[-2] + part_image['src'].split('/')[-1]
        # image_filename = get_image('mossmiata', part_image, image_filename)

        print(part_link)
        print(part_title)
        print(image_filename)
        print(part_price)
        print()
        # writeToDatabase(part_link, part_title, part_price, image_filename, 'autozone.png', make, model, generation, category, subcategory)

# codeSelect is responsible for acting as a selection and initialization function for the respective sources that data will be retrieved from
def codeSelect():
    '''
    Processes the code selection that the user makes and handles the web scraping for each website accordingly
    '''
    import json

    dest = input("Where are we scraping from?\nType in the code, or type 'ESC' to exit: ")

    if dest == '':
        print('Please type in a code\n')
        codeSelect()
    elif dest == 'ESC':
        exit()
        
    elif dest == 'ecs':
        ecstuning_URLs = json.loads(open('data/source-urls/ecstuning/ecstuning-urls.json').read())
        ecstuning_cats = json.loads(open('data/source-urls/ecstuning/ecstuning-cats.json').read())

        save_index = input('Which save file would you like to save your position to? ')

        # Asks user if they would like to resume scraping where they last left off or start from the beginning
        resumeCheck = input('Resume from where you left off (y/n)? ')
        if resumeCheck == 'y':
            load_location = pickle.load(open(f'saves/ecstuning_{save_index}', 'rb'))
        elif resumeCheck == 'n':

            brandCheck = input('Which make would you like to start with? (Audi/BMW/Mercedes/MINI/Porsche/Volkswagen): ')
            if brandCheck == 'Audi':
                save_location = ['Audi', '80', 'B1', '/Audi-80-FWD-4cyl', 'Air Intake', 'Air Filter', '/Engine/Intake/Air_Filter']
                pickle.dump(save_location, open(f'saves/ecstuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/ecstuning_{save_index}', 'rb'))
            elif brandCheck == 'BMW':
                save_location = ['BMW', '128i', 'E8X', '/BMW-E82-128i-N52_3.0L', 'Air Intake', 'Air Filter', '/Engine/Intake/Air_Filter']
                pickle.dump(save_location, open(f'saves/ecstuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/ecstuning_{save_index}', 'rb'))
            elif brandCheck == 'Mercedes':
                save_location = ['Mercedes', '190D', 'W201', '/Mercedes_Benz-1988-190D-201.126-2.5-Sedan-L5_2.5L', 'Air Intake', 'Air Filter', '/Engine/Intake/Air_Filter']
                pickle.dump(save_location, open(f'saves/ecstuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/ecstuning_{save_index}', 'rb'))
            elif brandCheck == 'MINI':
                save_location = ['MINI',  'Clubman', 'R55', '/Mini-2010-Cooper-R55-Clubman-Coupe-L4_1.6L_N12B16A', 'Air Intake', 'Air Filter', '/Engine/Intake/Air_Filter']
                pickle.dump(save_location, open(f'saves/ecstuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/ecstuning_{save_index}', 'rb'))
            elif brandCheck == 'Porsche':
                save_location = ['Porsche', '356', 'Pre-A', '/Porsche-1955-356-Base-H4_1.3L', 'Air Intake', 'Air Filter', '/Engine/Intake/Air_Filter']
                pickle.dump(save_location, open(f'saves/ecstuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/ecstuning_{save_index}', 'rb'))
            elif brandCheck == 'Volkswagen':
                save_location = ['Volkswagen', 'Arteon', 'B8', '/Volkswagen-Arteon-4Motion-2.0T_Gen3', 'Air Intake', 'Air Filter', '/Engine/Intake/Air_Filter']
                pickle.dump(save_location, open(f'saves/ecstuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/ecstuning_{save_index}', 'rb'))
            elif brandCheck == 'custom':
                customMake = input('Make: ')
                customModel = input('Model: ')
                customGen = input('Generation: ')
                customVTag = input('Vehicle Tag: ')
                customCat = input('Category: ')
                customSubcat = input('Subcategory: ')
                customCTag = input('Category Tag: ')

                save_location = [customMake, customModel, customGen, customVTag, customCat, customSubcat, customCTag]
                pickle.dump(save_location, open(f'saves/ecstuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/ecstuning_{save_index}', 'rb'))
            else:
                print('You literally did not type a single valid brand in. Exiting.')
                exit()

        iterateCycle(load_location, save_index, ecstuning_URLs, ecstuning_cats, 'ecstuning', dest)        
        
    elif dest == 'fcp':
        fcpeuro_URLs = json.loads(open('data/source-urls/fcpeuro/fcpeuro-urls.json').read())
        fcpeuro_cats = json.loads(open('data/source-urls/fcpeuro/fcpeuro-cats.json').read())

        save_index = input('Which save file would you like to save your position to? ')

        # Asks user if they would like to resume scraping where they last left off or start from the beginning
        resumeCheck = input('Resume from where you left off (y/n)? ')
        if resumeCheck == 'y':
            load_location = pickle.load(open(f'saves/fcpeuro_{save_index}', 'rb'))
        elif resumeCheck == 'n':

            brandCheck = input('Which make would you like to start with? (Audi/BMW/Mercedes/Porsche/Volkswagen): ')
            if brandCheck == 'Audi':
                save_location = ['Audi', '80', 'B1', '/Audi-parts/80', 'Air Intake', 'Air Filter', '/Air-Filter']
                pickle.dump(save_location, open(f'saves/fcpeuro_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/fcpeuro_{save_index}', 'rb'))
            elif brandCheck == 'BMW':
                save_location = ['BMW', '128i', 'E8X', '/BMW-parts/128i', 'Air Intake', 'Air Filter', '/Air-Filter']
                pickle.dump(save_location, open(f'saves/fcpeuro_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/fcpeuro_{save_index}', 'rb'))
            elif brandCheck == 'Mercedes':
                save_location = ['Mercedes', '190', 'W201', '/Mercedes~Benz-parts/190', 'Air Intake', 'Air Filter', '/Air-Filter']
                pickle.dump(save_location, open(f'saves/fcpeuro_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/fcpeuro_{save_index}', 'rb'))
            elif brandCheck == 'Porsche':
                save_location = ['Porsche', '356B', 'B', '/Porsche-parts/356B', 'Air Intake', 'Air Filter', '/Air-Filter']
                pickle.dump(save_location, open(f'saves/fcpeuro_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/fcpeuro_{save_index}', 'rb'))
            elif brandCheck == 'Volkswagen':
                save_location = ['Volkswagen', 'Arteon', 'B8', '/Volkswagen-parts/Arteon', 'Air Intake', 'Air Filter', '/Air-Filter']
                pickle.dump(save_location, open(f'saves/fcpeuro_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/fcpeuro_{save_index}', 'rb'))
            elif brandCheck == 'custom':
                customMake = input('Make: ')
                customModel = input('Model: ')
                customGen = input('Generation: ')
                customVTag = input('Vehicle Tag: ')
                customCat = input('Category: ')
                customSubcat = input('Subcategory: ')
                customCTag = input('Category Tag: ')

                save_location = [customMake, customModel, customGen, customVTag, customCat, customSubcat, customCTag]
                pickle.dump(save_location, open(f'saves/fcpeuro_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/fcpeuro_{save_index}', 'rb'))
            else:
                print('You literally did not type a single valid brand in. Exiting.')
                exit()

        iterateCycle(load_location, save_index, fcpeuro_URLs, fcpeuro_cats, 'fcpeuro', dest)

    elif dest == 'bw':
        bimmerworld_URLs = json.loads(open('data/source-urls/bimmerworld/bimmerworld-urls.json').read())
        bimmerworld_cats = json.loads(open('data/source-urls/bimmerworld/bimmerworld-cats.json').read())

        save_index = input('Which save file would you like to save your position to? ')

        # Asks user if they would like to resume scraping where they last left off or start from the beginning
        resumeCheck = input('Resume from where you left off (y/n)? ')
        if resumeCheck == 'y':
            load_location = pickle.load(open(f'saves/bimmerworld_{save_index}', 'rb'))
        elif resumeCheck == 'n':
            save_location = ['BMW', '128i', 'E8X', '/#/filter:finder_hierarchy_2:3$2520Series~E36$2520(92-99)/q:', 'Air Intake', 'Air Filter', '/Intake-Fuel/Replacement-Filters']
            pickle.dump(save_location, open(f'saves/bimmerworld_{save_index}', 'wb'))
            load_location = pickle.load(open(f'saves/bimmerworld_{save_index}', 'rb'))
        
        iterateCycle(load_location, save_index, bimmerworld_URLs, bimmerworld_cats, 'bimmerworld', dest)

    elif dest == 'tm':
        turnermotorsport_URLs = json.loads(open('data/source-urls/turnermotorsport/turnermotorsport-urls.json').read())
        turnermotorsport_cats = json.loads(open('data/source-urls/turnermotorsport/turnermotorsport-cats.json').read())

        save_index = input('Which save file would you like to save your position to? ')

        # Asks user if they would like to resume scraping where they last left off or start from the beginning
        resumeCheck = input('Resume from where you left off (y/n)? ')
        if resumeCheck == 'y':
            load_location = pickle.load(open(f'saves/turnermotorsport_{save_index}', 'rb'))
        elif resumeCheck == 'n':

            brandCheck = input('Which make would you like to start with? (BMW/MINI): ')
            if brandCheck == 'BMW':
                save_location = ['BMW', '128i', 'E8X', '/BMW-E82', 'Air Intake', 'Air Filter', '/c-343-bmw-air-intake-filters']
                pickle.dump(save_location, open(f'saves/turnermotorsport_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/turnermotorsport_{save_index}', 'rb'))
            elif brandCheck == 'MINI':
                save_location = ['MINI', 'Clubman', 'R55', '/BMW-MINI', 'Air Intake', 'Air Filter', '/c-343-bmw-air-intake-filters']
                pickle.dump(save_location, open(f'saves/turnermotorsport_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/turnermotorsport_{save_index}', 'rb'))
            elif brandCheck == 'custom':
                customMake = input('Make: ')
                customModel = input('Model: ')
                customGen = input('Generation: ')
                customVTag = input('Vehicle Tag: ')
                customCat = input('Category: ')
                customSubcat = input('Subcategory: ')
                customCTag = input('Category Tag: ')

                save_location = [customMake, customModel, customGen, customVTag, customCat, customSubcat, customCTag]
                pickle.dump(save_location, open(f'saves/turnermotorsport_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/turnermotorsport_{save_index}', 'rb'))
            else:
                print('You literally did not type a single valid brand in. Exiting.')
                exit()

        iterateCycle(load_location, save_index, turnermotorsport_URLs, turnermotorsport_cats, 'turnermotorsport', dest)

    elif dest == '034':
        o34motorsport_URLs = json.loads(open('data/source-urls/034motorsport/034motorsport-urls.json').read())
        o34motorsport_cats = json.loads(open('data/source-urls/034motorsport/034motorsport-cats.json').read())

        save_index = input('Which save file would you like to save your position to? ')

        # Asks user if they would like to resume scraping where they last left off or start from the beginning
        resumeCheck = input('Resume from where you left off (y/n)? ')
        if resumeCheck == 'y':
            load_location = pickle.load(open(f'saves/034motorsport_{save_index}', 'rb'))
        elif resumeCheck == 'n':

            brandCheck = input('Which make would you like to start with? (Audi/Volkswagen): ')
            if brandCheck == 'Audi':
                save_location = ['Audi', '80', 'B3', '/audi/vintage/80-90/b3/i4-8v', 'Air Intake', 'Air Intake', '/air-intake.html']
                pickle.dump(save_location, open(f'saves/034motorsport_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/034motorsport_{save_index}', 'rb'))
            elif brandCheck == 'Volkswagen':
                save_location = ['Volkswagen', 'Beetle', 'Type 2', '/volkswagen/beetle/mkiv-new-beetle/1-8t', 'Air Intake', 'Air Intake', '/air-intake.html']
                pickle.dump(save_location, open(f'saves/034motorsport_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/034motorsport_{save_index}', 'rb'))
            elif brandCheck == 'custom':
                customMake = input('Make: ')
                customModel = input('Model: ')
                customGen = input('Generation: ')
                customVTag = input('Vehicle Tag: ')
                customCat = input('Category: ')
                customSubcat = input('Subcategory: ')
                customCTag = input('Category Tag: ')

                save_location = [customMake, customModel, customGen, customVTag, customCat, customSubcat, customCTag]
                pickle.dump(save_location, open(f'saves/034motorsport_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/034motorsport_{save_index}', 'rb'))
            else:
                print('You literally did not type a single valid brand in. Exiting.')
                exit()

        iterateCycle(load_location, save_index, o34motorsport_URLs, o34motorsport_cats, '034motorsport', dest)

    elif dest == 'uro':
        urotuning_URLs = json.loads(open('data/source-urls/urotuning/urotuning-urls.json').read())
        urotuning_cats = json.loads(open('data/source-urls/urotuning/urotuning-cats.json').read())

        save_index = input('Which save file would you like to save your position to? ')

        # Asks user if they would like to resume scraping where they last left off or start from the beginning
        resumeCheck = input('Resume from where you left off (y/n)? ')
        if resumeCheck == 'y':
            load_location = pickle.load(open(f'saves/urotuning_{save_index}', 'rb'))
        elif resumeCheck == 'n':

            brandCheck = input ('Which make would you like to start with? (Audi/BMW/Mercedes/MINI/Porsche/Volkswagen): ')
            if brandCheck == 'Audi':
                save_location = ['Audi', '80', 'B1', '', 'Air Intake', 'Air Filter', 'Engine > Intake > Air Filter']
                pickle.dump(save_location, open(f'saves/urotuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/urotuning_{save_index}', 'rb'))
            elif brandCheck == 'BMW':
                save_location = ['BMW', '128i', 'E8X', '/collections/bmw-e8x-128i-n52-3-0l', 'Air Intake', 'Air Filter', 'Engine > Intake > Air Filter']
                pickle.dump(save_location, open(f'saves/urotuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/urotuning_{save_index}', 'rb'))
            elif brandCheck == 'Mercedes':
                save_location = ['Mercedes', '190', 'W201', '', 'Air Intake', 'Air Filter', 'Engine > Intake > Air Filter']
                pickle.dump(save_location, open(f'saves/urotuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/urotuning_{save_index}', 'rb'))
            elif brandCheck == 'MINI':
                save_location = ['MINI',  'Clubman', 'R55', '/collections/mini-cooper-clubman-r55-base-1-6l', 'Air Intake', 'Air Filter', 'Engine > Intake > Air Filter']
                pickle.dump(save_location, open(f'saves/urotuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/urotuning_{save_index}', 'rb'))
            elif brandCheck == 'Porsche':
                save_location = ['Porsche', '356', 'Pre-A', '', 'Air Intake', 'Air Filter', 'Engine > Intake > Air Filter']
                pickle.dump(save_location, open(f'saves/urotuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/urotuning_{save_index}', 'rb'))
            elif brandCheck == 'Volkswagen':
                save_location = ['Volkswagen', 'Arteon', 'B8', '/collections/volkswagen-arteon-2-0t', 'Air Intake', 'Air Filter', 'Engine > Intake > Air Filter']
                pickle.dump(save_location, open(f'saves/urotuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/urotuning_{save_index}', 'rb'))
            elif brandCheck == 'custom':
                customMake = input('Make: ')
                customModel = input('Model: ')
                customGen = input('Generation: ')
                customVTag = input('Vehicle Tag: ')
                customCat = input('Category: ')
                customSubcat = input('Subcategory: ')
                customCTag = input('Category Tag: ')

                save_location = [customMake, customModel, customGen, customVTag, customCat, customSubcat, customCTag]
                pickle.dump(save_location, open(f'saves/urotuning_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/urotuning_{save_index}', 'rb'))
            else:
                print('You literally did not type a single valid brand in. Exiting.')
                exit()

        scrape_uro(urotuning_URLs, urotuning_cats, load_location, save_index)

    elif dest == 'ahaz':
        autohausaz_URLs = json.loads(open('data/source-urls/autohausaz/autohausaz-urls.json').read())
        autohausaz_cats = json.loads(open('data/source-urls/autohausaz/autohausaz-cats.json').read())

        save_index = input('Which save file would you like to save your position to? ')

        # Asks user if they would like to resume scraping where they last left off or start from the beginning
        resumeCheck = input('Resume from where you left off (y/n)? ')
        if resumeCheck == 'y':
            load_location = pickle.load(open(f'saves/autohausaz_{save_index}', 'rb'))
        elif resumeCheck == 'n':

            brandCheck = input('Which make would you like to start with? (Audi/BMW/Mercedes/MINI/Porsche/Volkswagen): ')
            if brandCheck == 'Audi':
                save_location = ['Audi', '80', 'B1', '', 'Air Intake', 'Air Filter', '/22-fuel_air_system/11162-air_filter_seal']
                pickle.dump(save_location, open(f'saves/autohausaz_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autohausaz_{save_index}', 'rb'))
            elif brandCheck == 'BMW':
                save_location = ['BMW', '128i', 'E8X', '/catalog/c/bmw/2008/1442302-128i', 'Air Intake', 'Air Filter', '/22-fuel_air_system/11162-air_filter_seal']
                pickle.dump(save_location, open(f'saves/autohausaz_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autohausaz_{save_index}', 'rb'))
            elif brandCheck == 'Mercedes':
                save_location = ['Mercedes', '190', 'W201', '', 'Air Intake', 'Air Filter', '/22-fuel_air_system/11162-air_filter_seal']
                pickle.dump(save_location, open(f'saves/autohausaz_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autohausaz_{save_index}', 'rb'))
            elif brandCheck == 'MINI':
                save_location = ['MINI',  'Clubman', 'R55', '/catalog/c/mini/2011/1501048-cooper_clubman', 'Air Intake', 'Air Filter', '/22-fuel_air_system/11162-air_filter_seal']
                pickle.dump(save_location, open(f'saves/autohausaz_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autohausaz_{save_index}', 'rb'))
            elif brandCheck == 'Porsche':
                save_location = ['Porsche', '356', 'Pre-A', '', 'Air Intake', 'Air Filter', '/22-fuel_air_system/11162-air_filter_seal']
                pickle.dump(save_location, open(f'saves/autohausaz_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autohausaz_{save_index}', 'rb'))
            elif brandCheck == 'Volkswagen':
                save_location = ['Volkswagen', 'Arteon', 'B8', '/catalog/c/vw/2019/146564~5129~975~15880~~6~6-arteon_sel_rline', 'Air Intake', 'Air Filter', '/22-fuel_air_system/11162-air_filter_seal']
                pickle.dump(save_location, open(f'saves/autohausaz_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autohausaz_{save_index}', 'rb'))
            elif brandCheck == 'custom':
                customMake = input('Make: ')
                customModel = input('Model: ')
                customGen = input('Generation: ')
                customVTag = input('Vehicle Tag: ')
                customCat = input('Category: ')
                customSubcat = input('Subcategory: ')
                customCTag = input('Category Tag: ')

                save_location = [customMake, customModel, customGen, customVTag, customCat, customSubcat, customCTag]
                pickle.dump(save_location, open(f'saves/autohausaz_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autohausaz_{save_index}', 'rb'))
            else:
                print('You literally did not type a single valid brand in. Exiting.')
                exit()

        iterateCycle(load_location, save_index, autohausaz_URLs, autohausaz_cats, 'autohausaz', dest)
    
    elif dest == 'autozone':
        autozone_URLs = json.loads(open('data/source-urls/autozone/autozone-urls.json').read())
        autozone_cats = json.loads(open('data/source-urls/autozone/autozone-cats.json').read())

        save_index = input('Which save file would you like to save your position to? ')
        resume_check = input('Resume from where you left off (y/n)? ')
        if resume_check == 'y':
            load_location = pickle.load(open(f'saves/autozone_{save_index}', 'rb'))
        elif resume_check == 'n':
            brand_check = input('Which make would you like to start with? (Audi/BMW/Mercedes/MINI/Porsche/Volkswagen): ')
            if brand_check == 'Audi':
                save_location = ['Audi', '80', 'B1', '', 'Air Intake', 'Air Filter', '']
                pickle.dump(save_location, open(f'saves/autohausaz_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autohausaz_{save_index}', 'rb'))
            elif brand_check == 'BMW':
                save_location = ['BMW', '128i', 'E8X', '', 'Air Intake', 'Air Filter', '']
                pickle.dump(save_location, open(f'saves/autozone_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autozone_{save_index}', 'rb'))
            elif brand_check == 'Mercedes':
                save_location = ['Mercedes', '190', 'W201', '', 'Air Intake', 'Air Filter', '']
                pickle.dump(save_location, open(f'saves/autozone_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autozone_{save_index}', 'rb'))
            elif brand_check == 'MINI':
                save_location = ['MINI',  'Clubman', 'R55', '', 'Air Intake', 'Air Filter', '']
                pickle.dump(save_location, open(f'saves/autozone_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autozone_{save_index}', 'rb'))
            elif brand_check == 'Porsche':
                save_location = ['Porsche', '356', 'Pre-A', '', 'Air Intake', 'Air Filter', '']
                pickle.dump(save_location, open(f'saves/autozone_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autozone_{save_index}', 'rb'))
            elif brand_check == 'Volkswagen':
                save_location = ['Volkswagen', 'Arteon', 'B8', '', 'Air Intake', 'Air Filter', '']
                pickle.dump(save_location, open(f'saves/autozone_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autozone_{save_index}', 'rb'))
            elif brand_check == 'custom':
                customMake = input('Make: ')
                customModel = input('Model: ')
                customGen = input('Generation: ')
                customVTag = input('Vehicle Tag: ')
                customCat = input('Category: ')
                customSubcat = input('Subcategory: ')
                customCTag = input('Category Tag: ')

                save_location = [customMake, customModel, customGen, customVTag, customCat, customSubcat, customCTag]
                pickle.dump(save_location, open(f'saves/autozone_{save_index}', 'wb'))
                load_location = pickle.load(open(f'saves/autozone_{save_index}', 'rb'))
            else:
                print('You literally did not type a single valid brand in. Exiting.')
                exit()

        iterateCycle(load_location, save_index, autozone_URLs, autozone_cats, 'autozone', dest)

    elif dest == 'moss':
        mossmiata_URLs = json.loads(open('data/source-urls/mossmiata/mossmiata-urls.json').read())
        mossmiata_cats = json.loads(open('data/source-urls/mossmiata/mossmiata-cats.json').read())

        save_index = input('Which save file would you like to save your position to? ')
        resume_check = input('Resume from where you left off (y/n)? ')
        if resume_check == 'y':
            load_location = pickle.load(open(f'saves/autozone_{save_index}', 'rb'))
        elif resume_check == 'n':
            make = 'Mazda'
            model = 'MX-5'
            generation = input('Generation: ')
            v_tag = input('Vehicle Tag: ')
            category = input('Category: ')
            subcategory = input('Subcategory: ')
            c_tag = input('Category Tag: ')

            save_location = [make, model, generation, v_tag, category, subcategory, c_tag]
            pickle.dump(save_location, open(f'saves/mossmiata_{save_index}', 'wb'))
            load_location = pickle.load(open(f'saves/mossmiata_{save_index}', 'rb'))
        
        iterateCycle(load_location, save_index, mossmiata_URLs, mossmiata_cats, 'mossmiata', dest)

    else:
        print('Error, code invalid\n')
        codeSelect()
    return

                                            #########################
                                            ### Write to Database ###
                                            #########################

# writeToDatabase serves to function as the interface between the SQLite3 database and the sources through which data is scraped from
def writeToDatabase(partLink, partName, partPrice, partPic, retailer, makePrelim, modelPrelim, generation, categoryPrelim, subcategoryPrelim):
    '''
    Commits data that was scraped to the SQLite3 database and automatically links parts and their information to a vehicle configuration
    '''
    os.chdir(baseDir)
    
    # Checks with database to verify the existence of the part. If it exists, it will check the price, but if nothing has changed, then no new information will be added
    alreadyExisting = 0
    if Part.query.filter_by(url=partLink, name=partName, logo=retailer).first() is None:
        newPart = Part(url=partLink, name=partName, price=partPrice, image=partPic, logo=retailer)

        db.session.add(newPart)
        db.session.commit()
        print('Addition of new part entry successful')
    else:
        currentPart = Part.query.filter_by(url=partLink, name=partName, logo=retailer).first()
        alreadyExisting = 1
        if currentPart.price != partPrice:
            currentPart.price = partPrice
            db.session.commit()
            print('Price updated successfully')
        elif currentPart.image != partPic:
            currentPart.image = partPic
            db.session.commit()
            print('Image path updated successfully')
        else:
            print('Part already exists fully in database')

    make = Make.query.filter_by(name=makePrelim).first()
    model = Model.query.filter_by(make_id=make.id, name=modelPrelim, generation=generation).first()
    category = Category.query.filter_by(name=categoryPrelim).first()
    subcategory = Subcategory.query.filter_by(name=subcategoryPrelim).first()

    # Determines if a part has already been classified to a vehicle or if a new classification need to be made depending on the condition of the part's existence
    if alreadyExisting == 1:
        if Classification.query.filter_by(make_id=make.id, model_id=model.id, cat_id=category.id, subcat_id=subcategory.id, part_id=currentPart.id).first() is None:
            newAssignment = Classification(make_id=make.id, model_id=model.id, cat_id=category.id, subcat_id=subcategory.id, part_id=currentPart.id)
            db.session.add(newAssignment)
            db.session.commit()
            print('Existing part assigned to another vehicle')
        else:
            print('Part is already classified')
    else:
        newAssignment = Classification(make_id=make.id, model_id=model.id, cat_id=category.id, subcat_id=subcategory.id, part_id=newPart.id)
        db.session.add(newAssignment)
        db.session.commit()
        print('New part classified successfully')
    print()
    

                                            ###############
                                            ### Runtime ###
                                            ###############

if __name__ == '__main__':
    user_agent_desktop = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    headers = {'User-Agent': user_agent_desktop}

    baseDir = os.getcwd()

    with open('scraper_config.json') as config_file:
        config = json.load(config_file)

    host = config.get('HOST')
    port = config.get('PORT')
    username = config.get('USERNAME')
    password = config.get('PASSWORD')

    master_password = config.get('KEYRING_PASS')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password, timeout=None)

    destinations = [
        'ECS Tuning (ecs)',
        'FCP Euro (fcp)',
        'Bimmerworld (bw)',
        'Turner Motorsport (tm)',
        '034 Motorsport (034)',
        'UROTUNING (uro)',
        'AutohausAZ (ahaz)',
        'Autozone (autozone)',
        'MossMiata (moss)',
        ]

    print("Here's where we can pull data from:\n")
    for each in destinations:
        print(each)
    print()
    try:
        codeSelect()
        
        yag = yagmail.SMTP('theparthubcontact@gmail.com')
        yag.send(
            to = 'admin@theparthub.com',
            subject = 'Scraping Process Completed Successfully',
            contents = f'A scraping process has successfully completed at {time.ctime()}.'
        )
        print('Done!')

    except (
        RuntimeError,
        TypeError,
        NameError,
        ValueError,
        KeyError,
        AttributeError,
        TimeoutError,
        ConnectionAbortedError,
        ConnectionError,
        ConnectionRefusedError,
        ConnectionResetError,
        requests.exceptions.ConnectionError,
        requests.exceptions.ReadTimeout
        ) as e:

        yag = yagmail.SMTP('theparthubcontact@gmail.com')
        yag.send(
            to = 'admin@theparthub.com',
            subject = 'Scraping Process Terminated Prematurely',
            contents = f'A scraping process has been terminated prematurely at {time.ctime()} with error:\n\n{e}'
        )

        print(e)
        print(f'Script stopped running at approximately {time.ctime()}')