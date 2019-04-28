import requests
import asyncio
import hashlib
from bs4 import BeautifulSoup
import os
import logging

ROOT_URL = 'https://chalicecollectibles.com'
PRODUCT_URL = 'https://chalicecollectibles.com/collections/all?sort_by=created-descending'
DELAY_MINUTES = int(os.environ['CHALICE_CHECK_DELAY'])


def do_loop(callback, database, table, loop):
    try:
        logging.debug('Starting loop')
        products = check_products()
        callback(products, database, table)
    except Exception as e:
        logging.error(e)
    asyncio.get_event_loop().call_later(DELAY_MINUTES * 60, do_loop, callback, loop)


def check_products():
    product_list = {}
    page = requests.get(PRODUCT_URL)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, 'html.parser')
    collection = soup.find(class_='collection-main')
    if collection is None:
        logging.debug('No products found')
        return product_list
    products = collection.find_all('li')
    if products is None:
        logging.debug('No collection found')
        return product_list
    for product in products:
        details = product.find('a')
        if not details.has_attr('title') or not details.has_attr('href'):
            logging.debug('Missing required details')
            continue
        title = details['title']
        link = ROOT_URL + details['href']

        image_details = details.find('img')
        if image_details is None or not image_details.has_attr('src'):
            image = 'https://cdn.shopify.com/s/assets/no-image-160-1cfae84eca4ba66892099dcd26e604f5801fdadb3693bc9977f476aa160931ac_120x120.gif'
        else:
            image = 'https:' + image_details['src']

        price_details = details.find(class_='price')
        if price_details is None or not price_details.has_attr('class'):
            price = 'No price information found'
        elif 'sold-out' in price_details['class']:
            price = 'Sold Out'
        else:
            price_usd = price_details.find(class_='price-money')
            if price_usd is None:
                price = 'Unable to find cost'
            else:
                price = price_usd.string
        hash_string = '{}:{}:{}'.format(title, link, image).encode()
        product_list[hashlib.sha256(hash_string).hexdigest()] = {
            'title': title, 'link': link, 'image': image, 'price': price, 'price-change': False}
    return product_list
