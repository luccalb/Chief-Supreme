#!/usr/bin/env python

""" firebase_service.py
A service for managing access to the firebase realtime db.
"""

import pyrebase
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "apiKey": os.getenv("fb_api_key"),
    "authDomain": os.getenv("fb_auth_domain"),
    "databaseURL": os.getenv("fb_database_url"),
    "storageBucket": "projectId.appspot.com",  # not actually used but needed by pyrebase
}

firebase = pyrebase.initialize_app(config)

# Get a reference to the auth service
auth = firebase.auth()

# Log the user in
user = auth.sign_in_with_email_and_password(os.getenv("fb_email"), os.getenv("fb_pass"))

# Get a reference to the database service
token_db = firebase.database()

token = None


def stream_handler(message):
    global token
    token = message['data']
    return


def start_token_stream(task_nr):
    return token_db.child("recaptcha_tokens").child(f"token{task_nr}").stream(stream_handler, user["idToken"])


def wait_for_token():
    global token
    while True:
        if token is not None:
            return token


def get_coplist():
    return token_db.child("coplist").get(token=user['idToken']).val()


def get_identities():
    return token_db.child("identities").get(token=user['idToken']).val()
