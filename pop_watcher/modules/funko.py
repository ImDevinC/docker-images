import requests
import asyncio
import hashlib
import os
import logging
from requests.compat import urljoin, quote_plus

ROOT_URL = 'https://www.funko.com'
SEARCH_ENDPOINT = '/api/search/terms'
DELAY_MINUTES = int(os.environ.get('CHECK_DELAY', 10))


def do_loop(callback, database, table, loop):
    try:
        logging.debug('Starting funko loop')
        products = check_products()
        callback(products, database, table)
    except Exception as ex:
        logging.error(ex)
    asyncio.get_event_loop().call_later(
        DELAY_MINUTES * 60, do_loop, callback, database, table, loop)


def check_products():
    product_list = {}
    payload = {
        'page': 0,
        'pageCount': 60,
        'type': 'catalog',
        'productBrands': ['pop!'],
        'sort': {
            'releaseDate': 'desc'
        }
    }
    url = urljoin(ROOT_URL, SEARCH_ENDPOINT)
    response = requests.post(url, json=payload)
    response.raise_for_status()
    hits = response.json()['hits']
    for hit in hits:
        title = hit['title']
        product_url = '/products/%s/%s/%s/%s' % (
            hit['productCategories'][0], hit['productBrands'][0], hit['licenses'][0], hit['referenceUrl'])
        link = urljoin(ROOT_URL, product_url.replace(' ', '%20'))
        image = urljoin(ROOT_URL, hit['imageUrl'])
        price = '${:,.2f}'.format(
            hit['marketValue']) if 'marketValue' in hit else 'Unknown'
        hash_string = '{}:{}:{}'.format(title, link, image).encode()
        product_list[hashlib.sha256(hash_string).hexdigest()] = {
            'title': title, 'link': link, 'image': image, 'price': price, 'price-change': False}

    return product_list
