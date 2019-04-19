import requests
import asyncio
import hashlib
from bs4 import BeautifulSoup
import os
import logging

ROOT_URL = 'https://chalicecollectibles.com'
PRODUCT_URL = 'https://chalicecollectibles.com/collections/all?sort_by=created-descending'
DELAY_MINUTES = int(os.environ['CHALICE_CHECK_DELAY'])
FILENAME = '/data/chalicecollectibles.txt'


def do_loop(callback, loop):
    try:
        logging.debug('Starting loop')
        products = check_products()
        products = remove_dups(products)
        callback(products)
    except Exception as e:
        logging.error(e)
    asyncio.get_event_loop().call_later(DELAY_MINUTES * 60, do_loop, callback, loop)


def remove_dups(new_products):
    final_products = []
    old_products = {}
    if not os.path.isfile(FILENAME):
        f = open(FILENAME, 'w+')
        f.close()

    with open(FILENAME, 'r') as f:
        for line in f:
            data = line.strip().split(':')
            old_products[data[0]] = data[1]

    logging.debug('Found {} old products and {} new products'.format(
        len(old_products), len(new_products)))
    for product in new_products:
        if not product in old_products:
            final_products.append(new_products[product])
        if product in old_products and new_products[product]['price'] != old_products[product]:
            new_products[product]['price-change'] = True
            final_products.append(new_products[product])

    with open(FILENAME, 'w') as f:
        for product in new_products:
            f.write('{}:{}\n'.format(product, new_products[product]['price']))

    logging.debug('Found {} new products to send'.format(len(final_products)))
    return final_products


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
