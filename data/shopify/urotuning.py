import json
import random
import requests
import time
import sqlalchemy as db

##################################
#### UroTuning Product Mapper ####
##################################
VENDOR_NAME = 'urotuning'
BASE_URL = 'https://www.urotuning.com'
PAGE = 1
LIMIT = 250

with open('../../application/config.json', 'r') as config_file:
    db_config = json.load(config_file)

db_engine = db.create_engine(db_config.get('SQLALCHEMY_DATABASE_URI'))
db_conn = db_engine.connect()
metadata = db.MetaData()
shopify_table = db.Table('shopify_product_data', metadata, autoload=True, autoload_with=db_engine)

def db_do_upsert(shopify_id, vendor, handle):
    # First things first we query the database so that we can execute an "upsert" operation, where we update records where applicable and insert where they do not exist
    query = db.select(shopify_table).where(shopify_table.columns.vendor==vendor, shopify_table.columns.shopify_id==shopify_id)
    result = db_conn.execute(query).first()

    # Check to see if record already exists so we can distinguish where we are using UPDATE or INSERT
    if result is not None and result[1] == shopify_id:
        # Check if any changes exist or if we can skip
        if result[1] == shopify_id and result[2] == vendor and result[3] == handle:
            print('No changes found, SKIP')
        else:
            # Build UPDATE operation query
            print('Updating record...')
            upsert_query = db.update(shopify_table).values(handle=handle).where(shopify_table.columns.shopify_id==shopify_id)
            db_conn.execute(upsert_query)
    else:    
        # Build INSERT operation query
        print('Inserting record...')
        upsert_query = db.insert(shopify_table).values(shopify_id=shopify_id, vendor=vendor, handle=handle)
        db_conn.execute(upsert_query)
    return

while True:
    try:
        products_url = f'{BASE_URL}/products.json?limit={LIMIT}&page={PAGE}'
        response = requests.get(products_url, timeout=10).json()
        if len(response['products']) > 0:
            for product in response['products']:
                shopify_id = product['id']
                vendor = VENDOR_NAME
                handle = product['handle']
                print(f'shopify_id: {shopify_id} | vendor: {vendor} | handle: {handle}')
                db_do_upsert(shopify_id, vendor, handle)
            print(f'Moving to the next page of products... PAGE: {PAGE + 1}')
            time.sleep(random.uniform(3, 8))
            PAGE += 1
        else:
            print(f'Finished scraping {VENDOR_NAME}!!!')
            exit()
    except requests.exceptions.ConnectionError as error:
        print(error)
        sleep_timer = random.uniform(900, 1200)
        print(f'Sleeping for approximately {sleep_timer / 60} minutes')
        time.sleep(sleep_timer)