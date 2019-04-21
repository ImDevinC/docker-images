from modules import chalicecollectibles, galactictoys
import asyncio
import logging
import requests
import json
import os
from ratelimiter import RateLimiter

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


def callback(products):
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


def main():
    asyncio.get_event_loop().call_soon(
        chalicecollectibles.do_loop, callback, asyncio.get_event_loop())
    asyncio.get_event_loop().call_soon(
        galactictoys.do_loop, callback, asyncio.get_event_loop())
    try:
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    main()
