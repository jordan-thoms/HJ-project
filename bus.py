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

import urllib
import urllib2

import web

urls = (
    '/(.*)/(.*)', 'bus',
)
app = web.application(urls, globals())

class bus:        
    def GET(self, origin, dest):
        # Get the bus stop number and relevant bus numbers to destination

		# Assuming we know it, for dev purposes, we'll hardcode this
		# 7148 - 36 Symonds St - S3
		bus_stop_number = 7148
		
		# ?stop=7148
		headers = { 'User-Agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7" }
		
		request = urllib2.Request(url=("http://m.maxx.co.nz/mobile-departure-board.aspx?stop=" + str(bus_stop_number)), headers=headers)
		response = urllib2.urlopen(request)
		
		soup = BeautifulSoup(response)
		incoming_buses = soup.findAll('tr', attrs={'data-theme' : 'a'})
		
		bus_stop_parsed = []
		for row in incoming_buses:
			incoming_bus_number = row.contents[1].contents
			incoming_bus_dest = row.contents[3].contents # bound dest
			incoming_bus_due = row.contents[5].contents # in minutes
			
			bus_stop_parsed.append({'bus_number': incoming_bus_number, 'bus_dest': incoming_bus_dest, 'bus_due': incoming_bus_due})
		
		return bus_stop_parsed

if __name__ == "__main__":
    app.run()