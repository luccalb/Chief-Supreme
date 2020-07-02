#!/usr/bin/env python

""" firebase_service.py
A service for detecting the supply drop and finding your desired
product/style and size IDs
"""

from models.item_model import Item

import requests
import urllib.parse
import jwt

STOCK_ENDPOINT = "https://www.supremenewyork.com/mobile_stock.json"
ITEM_ENDPOINT = "https://www.supremenewyork.com/shop/{}.json"
CHECKOUT_ENDPOINT = "https://www.supremenewyork.com/checkout.json"
ORDER_STATUS_ENDPOINT = "https://www.supremenewyork.com/checkout/{}/status.json"


s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5'})


def get_all_stock():
    return s.get(STOCK_ENDPOINT).json()


def wait_for_item(product):
    item = Item()
    cat = product['category']
    while True:
        stock = get_all_stock()['products_and_categories']
        item_id = find_by_keywords(stock, product['keywords'], cat)
        if item_id and 'style' not in product and 'size' not in product:
            item.id = item_id
            return item
        if item_id:
            item.id = item_id
            variants = s.get(ITEM_ENDPOINT.format(item_id)).json()['styles']
            if 'style' in product:
                style_id = find_style_id(variants, product['style'])
                item.style_id = style_id
            if 'size' in product and item.style_id:
                size_id = find_size_id(variants, product['size'], item.style_id)
                item.size_id = size_id
            return item


def find_by_keywords(stock, keywords, cat):
    for existing_item in stock[cat]:
        if all(x in existing_item['name'].lower() for x in keywords):
            return existing_item['id']
    return None


def find_style_id(variants, style_name):
    for style in variants:
        if style_name in style['name'].lower():
            return style['id']
    return None


def find_size_id(variants, size_name, style_id):
    for style in variants:
        if style['id'] == style_id:
            for size in style['sizes']:
                if size_name in size['name'].lower():
                    return size['id']
    return None


def get_item_styles(item_id):
    url = ITEM_ENDPOINT.format(item_id)
    print(url)


def checkout(driver, copper, valid_token, cardinal_id=None):
    card = copper['card']
    form = {
        'from_mobile': '1',
        'utf8': '✓',
        'order[billing_name]': copper['name'],
        'order[email]': copper['email'],
        'order[tel]': copper['tel'],
        'order[billing_address]': copper['address'],
        'order[billing_address_2]': copper['address_2'],
        'order[billing_address_3]': copper['address_3'],
        'order[billing_city]': copper['city'],
        'order[billing_zip]': copper['zip'],
        'order[billing_country]': 'DE',
        'same_as_billing_address': '1',
        'store_credit_id': '',
        'credit_card[type]': card['type'],
        'credit_card[cnb]': card['cnb'],
        'credit_card[month]': card['month'],
        'credit_card[year]': card['year'],
        'credit_card[ovv]': card['ovv'],
        'order[terms]': ['0', '1'],
        'g-recaptcha-response': valid_token
    }

    try:
        atok = driver.find_element_by_name('atok').get_attribute('value')
        form['atok'] = atok
    except:
        pass

    if cardinal_id:
        form['cardinal_id'] = cardinal_id

    form['cookie-sub'] = urllib.parse.quote(driver.get_cookie('pure_cart')['value'])
    cookies = driver.get_cookies()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    s.cookies.set('js-address', '||||||undefined||DE|')

    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.supremenewyork.com',
        'Referer': 'https://www.supremenewyork.com/checkout',
        'TE': 'Trailers',
        'X-Requested-With': 'XMLHttpRequest'
    }
    print(s.cookies.get_dict())
    r = s.post(CHECKOUT_ENDPOINT, headers=headers, data=form)
    print(form)
    print(r.content)
    return r.json()


def get_cardinal_id(server_jwt):
    body = {
        "BrowserPayload": {
            "Order": {
                "OrderDetails": {},
                "Consumer": {
                    "BillingAddress": {},
                    "ShippingAddress": {},
                    "Account": {}
                },
                "Cart": [],
                "Token": {},
                "Authorization": {},
                "Options": {},
                "CCAExtension": {}
            },
            "SupportsAlternativePayments": {
                "cca": True,
                "hostedFields": False,
                "applepay": False,
                "discoverwallet": False,
                "wallet": False,
                "paypal": False,
                "visacheckout": False
            }
        },
        "Client": {
            "Agent": "SongbirdJS",
            "Version": "1.30.2"
        },
        "ServerJWT": server_jwt
    }
    r = requests.post('https://centinelapi.cardinalcommerce.com/V1/Order/JWT/Init', json=body)
    cardinal_id = jwt.decode(r.json()['CardinalJWT'], verify=False)['ConsumerSessionId']
    return cardinal_id


def get_order_status(slug):
    return s.get(ORDER_STATUS_ENDPOINT.format(slug)).json()['status']
