#!/usr/bin/env python

""" cop_task_model.py
Class definition for a single Task for the bot to execute.

Params:

identity    (dict):     Contains all the personal checkout info like address, card, etc
product     (dict):     Keywords and desired styles/size for the item to cop
status      (string):   Contains info about the status of the task like running, success or failure
"""


class CopTask:
    def __init__(self, identity, product):
        self.product = product
        self.identity = identity
        self.status = 'Launched'
