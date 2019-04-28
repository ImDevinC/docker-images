import os
import asyncio
import logging
import requests
import json
from ratelimiter import RateLimiter
from db import Database
from modules import chalicecollectibles, galactictoys

logging.basicConfig(level=logging.DEBUG)

WEBHOOK_URL = os.environ['WEBHOOK_URL']
BATCHES_PER_MINUTE = int(os.environ['BATCHES_PER_MINUTE'])


@RateLimiter(max_calls=BATCHES_PER_MINUTE, period=60)
def post(batch):
    data = {'embeds': batch}
    try:
        r = requests.post(WEBHOOK_URL, data=json.dumps(data), headers={
            'Content-Type': 'application/json'})
        r.raise_for_status()
    except Exception as e:
        logging.error(e)


def remove_dups(database, table, products):
    product_hashes = ['"{}"'.format(element) for element in products.keys()]
    product_hashes = ','.join(product_hashes)
    matching_products = database.get_duplicate_items(table, product_hashes)

    for row in matching_products:
        if products[row[0]]['price'] == row[1]:
            products.pop(row[0])
            continue
        products[row[0]]['price-change'] = True

    database.save_products_to_table(table, products)
    return list(products.values())


def callback(products, database, table):
    logging.debug('Found {} products for table {}'.format(
        len(products), table))
    products = remove_dups(database, table, products)
    logging.debug(
        '{} new products to report after removing dups'.format(len(products)))
    embeds = []
    for product in products:
        color = '32768'
        if product['price-change']:
            color = '128'
        if product['price'] == 'Sold Out':
            color = '8388608'
        embeds.append({
            'title': product['title'],
            'url': product['link'],
            'thumbnail': {
                'url': product['image']
            },
            'fields': [{
                'name': 'Price',
                'value': product['price'],
                'inline': True
            }],
            'color': color
        })

    batched_embeds = [embeds[i:i + 10] for i in range(0, len(embeds), 10)]
    for batch in batched_embeds:
        post(batch)


def main(database):
    asyncio.get_event_loop().call_soon(
        chalicecollectibles.do_loop, callback, database, 'chalice_collectibles', asyncio.get_event_loop())
    asyncio.get_event_loop().call_soon(
        galactictoys.do_loop, callback, database, 'galactic_toys', asyncio.get_event_loop())
    try:
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    database = Database('/data/db.sqlite')
    database.do_migrations(os.path.dirname(
        os.path.abspath(__file__)) + '/migrations')
    main(database)
