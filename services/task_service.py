#!/usr/bin/env python

""" task_service.py
A service for auto-generating a task list and then running those tasks.
"""

import services.requests_service as req_service
import services.firebase_service as fb_service
from models.cop_task_model import CopTask

import random
import time
from datetime import datetime

from services import browser_service

token = None


def gen_tasklist(coplist, identities):
    task_list = []
    for product in coplist:
        # only create one task for the product if it's a personal item
        if product['personal']:
            task_list.append(CopTask(random.choice(identities), product))
        # create as much tasks as possible if it's meant for reselling
        else:
            for persona in identities:
                task_list.append(CopTask(persona, product))
    return task_list


def run_task(task_nr, task):
    token_stream = fb_service.start_token_stream(task_nr)
    mobile_browser = browser_service.get_mobile_driver()

    # find desired item
    store_item = req_service.wait_for_item(task.product)
    start = time.time()
    log(task_nr, f"{store_item.__dict__}")

    if store_item.style_id:
        prod_url = f"https://www.supremenewyork.com/mobile/#products/{store_item.id}/{store_item.style_id}"
    else:
        prod_url = f"https://www.supremenewyork.com/mobile/#products/{store_item.id}"

    mobile_browser.get(prod_url)

    # select size if needed
    if store_item.size_id:
        mobile_browser = browser_service.select_size(mobile_browser, store_item.size_id)
    log(task_nr, f"selected size in {time.time()-start}")

    # add to cart
    mobile_browser = browser_service.add_to_cart(mobile_browser)
    log(task_nr, f"atc {time.time()-start}")

    # get cardinal_jwt
    cardinal_jwt = browser_service.get_cardinal_jwt(mobile_browser)
    log(task_nr, f"cardinal jwt {time.time()-start}")

    # get cardinal_id directly from endpoint (quicker than waiting for it in browser)
    cardinal_id = req_service.get_cardinal_id(cardinal_jwt)
    log(task_nr, f"cardinal_id {time.time()-start}")

    # checkout
    recaptcha_token = fb_service.wait_for_token()
    log(task_nr, f"got captcha token {time.time() - start}")
    status = req_service.checkout(mobile_browser, task.identity, recaptcha_token, cardinal_id)
    mobile_browser.close()
    log(task_nr, f"Status {status['status']} {time.time() - start}")

    token_stream.close()

    if status['status'] == 'failed':
        return time.time() - start

    if status['status'] == 'queued':
        slug = status['slug']
        while True:
            status = req_service.get_order_status(slug)
            if status != 'queued':
                print(f"Task {task_nr}: Status {status} {time.time() - start}")
                return time.time() - start


def log(task_nr, text):
    print(f"[{datetime.now().strftime('%H:%M:%S')}][Task {task_nr}]: {text}")
