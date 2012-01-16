#!/usr/bin/env python
# encoding: utf-8
"""
bus.py

Authors: 	Hengjie Wang
Authors: 	Jordan Thoms
Date:		15 Jan 2012

Copyright (c) 2012. All Rights Reserved.

"""

import sys
import os
from BeautifulSoup import BeautifulSoup	# For processing HTML

import web

urls = (
    '/(.*)', 'hello'
)
app = web.application(urls, globals())

class hello:        
    def GET(self, name):
        if not name: 
            name = 'World'
        return 'Hello, ' + name + '!'

if __name__ == "__main__":
    app.run()