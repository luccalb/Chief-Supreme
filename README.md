# Chief Supreme
A hybrid auto checkout solution for https://www.supremenewyork.com/shop (EU).

The bots workflow can be divided into 3 stages:  
**Stage 1**: Drop detection and size/style ID gathering _(request based)_  
**Stage 2**: ATC procedure                              _(browser based)_  
**Stage 3**: Checkout                                   _(request based)_  

## Installation

Tested with Python 3.7  

### 1. Firebase RTDB setup

This bot uses a Google Firebase Realtime Database for storing profile information
and item details (keywords, style, size). `chief-supreme-export.json` File is an example
for what the DBs content should look like an can be imported using the firebase console.  

The realtime DB is also used as captcha "queue". You can use any open source captcha harvester
and make it write the captcha tokens to the DB using the tasks number as key like this "token{task_nr}"
(Check `chief-supreme-export.json` for an example). Firebases' stream functionality will automatically
detect the fresh token and pass it to the task.

### 2. Install requirements

`pip install -r requirements.txt`

### 3. Install chromedriver

Install chromedriver, then head to `services/browser_service.py` and change the path
to the `chromedriver.exe` to match yours.

### 4. Run the bot

`python chief_supreme.py`
