#!/usr/bin/env python

""" cop_task_model.py
Class definition for a single Item containing all it's IDs
"""


class Item:
    def __init__(self, prod_id=None, style_id=None, size_id=None):
        self.id = prod_id
        self.style_id = style_id
        self.size_id = size_id
