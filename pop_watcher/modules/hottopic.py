import requests
import asyncio
import hashlib
from bs4 import BeautifulSoup
import os
import logging

PRODUCT_URL = 'https://www.hottopic.com/funko/?srule=sortingNewArrival&sz=100'
DELAY_MINUTES = int(os.environ['HOTTOPIC_CHECK_DELAY'])


def do_loop(callback, database, table, loop):
    try:
        logging.debug('Starting Hot Topic loop')
        products = check_products()
        callback(products, database, table)
    except Exception as e:
        logging.error(e)
    asyncio.get_event_loop().call_later(
        DELAY_MINUTES * 60, do_loop, callback, database, table, loop)


def check_products():
    product_list = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
    page = requests.get(PRODUCT_URL, headers=headers)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, 'html.parser')
    collection = soup.find(id='results-products')
    if collection is None:
        logging.debug('No products found')
        return product_list
    products = collection.find_all(class_='product-tile')
    if products is None:
        logging.debug('No product tiles')
        return product_list
    for product in products:
        image_details = product.find(class_='first-image')
        if image_details is None or not image_details.has_attr('src'):
            image = 'https://cdn.shopify.com/s/assets/no-image-160-1cfae84eca4ba66892099dcd26e604f5801fdadb3693bc9977f476aa160931ac_120x120.gif'
        else:
            image = image_details['src']

        title_details = product.find(class_='name-link')
        if title_details is None:
            logging.error('No title found')
            continue
        
        title = title_details.string.strip()
        link = ''
        if title_details.has_attr('href'):
            link = title_details['href']
        
        price_details = product.find(class_='product-price')
        if price_details is None:
            price = 'Unknown'
        else:
            price = get_pricing(price_details)

        hash_string = '{}:{}:{}'.format(title, link, image).encode()
        product_list[hashlib.sha256(hash_string).hexdigest()] = {
            'title': title, 'link': link, 'image': image, 'price': price, 'price-change': False}
    return product_list

def get_pricing(price_details):
    discount_container = price_details.find(class_='product-discounted-price')
    on_sale = False
    if discount_container is None:
        price_span = price_details.find(class_='price-standard')
    else:
        price_span = discount_container.find(class_='price-sales')
        on_sale = True
    price = price_span.string
    if on_sale:
        price = 'On-sale: {}'.format(price)
    return price