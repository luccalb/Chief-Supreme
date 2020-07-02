#!/usr/bin/env python

""" browser_service.py
A service handling all browser based actions.
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def get_mobile_driver():
    chrome_options = Options()

    # selenium detection evasion
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    chrome_options.add_argument("--headless")

    # set the user agent to iPhone
    chrome_options.add_argument("--window-size=375,812")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5")

    driver = webdriver.Chrome('C:/Users/dev/Documents/chromedriver/chromedriver.exe', options=chrome_options)

    # more detection evasion
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """
    })

    driver.get('https://www.supremenewyork.com/mobile')
    return driver


def select_size(driver, size_id):
    # give maximum time of 1 second to select size, continue if not possible
    try:
        select_input = WebDriverWait(driver, 1, poll_frequency=0.1).until(
            EC.presence_of_element_located((By.ID, 'size-options')))
        select = Select(select_input)
        select.select_by_value(str(size_id))
        return driver
    except TimeoutException:
        print('no size select found, or took too long')
        return driver


def add_to_cart(driver):
    """
    Infinite loop that only breaks if we're successful at adding to cart.
    First looks for the add to cart button, if it says 'sold out' it continues to wait for a restock.
    Secondly waits for the checkout now button to click it.
    If it's successful with atc but can't find the checkout button, don't try atc again, only wait for checkout button.

    :param driver: instance of webdriver currently on the product page
    :return: instance of webdriver on checkout page
    """
    atc_success = False
    while True:
        if not atc_success:
            try:
                atc = WebDriverWait(driver, 1, poll_frequency=0.1).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.cart-button')))
                if 'sold-out' in atc.get_attribute('class'):
                    continue
                atc.click()
                atc_success = True
            except TimeoutException:
                print('no atc button found or took too long')
                continue
        try:
            checkout_now = WebDriverWait(driver, 1, poll_frequency=0.1).until(
                EC.visibility_of_element_located((By.ID, 'checkout-now')))
            checkout_now.click()
            return driver
        except TimeoutException:
            print('no checkout button found, or took too long')
            continue


def get_cardinal_id(driver):
    try:
        cardinal_id = WebDriverWait(driver, 1, poll_frequency=0.1).until(
            EC.presence_of_element_located((By.NAME, 'cardinal_id')))
        return cardinal_id.get_attribute('value')
    except TimeoutException:
        print('no cardinal id found or took too long')
        return None


def get_cardinal_jwt(driver):
    # cardinal_jwt is needed to get cardinal_id which is not optional, so keep trying
    while True:
        try:
            cardinal_jwt = WebDriverWait(driver, 1, poll_frequency=0.1).until(
                EC.presence_of_element_located((By.ID, 'jwt_cardinal')))
            return cardinal_jwt.get_attribute('value')
        except TimeoutException:
            pass
