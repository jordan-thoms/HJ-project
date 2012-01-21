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
from web import form

urls = (
    '/route', 'Route',
    '/stop/(.*)', 'BusStopSchedule',
    '/', 'Index'
)

render = web.template.render('templates/', base='template_layout')
app = web.application(urls, globals())

class Index(object):	
	def GET(self):		
		return render.index()

class BusStopSchedule(object):
	def GET(self, bus_stop_number=7148, filter_bus_number=[]):
		'''
		Get the bus stop number and relevant bus numbers to destination
		
		bus_stop_number:
		filter_bus_number: Return only buses found in this list. Default is return all buses
		'''

		headers = {'User-Agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7"}
		
		request = urllib2.Request(url=("http://m.maxx.co.nz/mobile-departure-board.aspx?stop=" + str(bus_stop_number)), headers=headers)
		response = urllib2.urlopen(request)

		soup = BeautifulSoup(response)
		incoming_buses = soup.findAll('tr', attrs={'data-theme' : 'a'})
		
		bus_stop_parsed = []
		for row in incoming_buses:
			incoming_bus_number = row.contents[1].contents
			incoming_bus_dest = row.contents[3].contents # bound dest
			incoming_bus_due = row.contents[5].contents # in minutes

			# return only relevant bus data that I care about
			if filter_bus_number:
				# check if you can do that with lists
				if incoming_bus_number in filter_bus_number:
					bus_stop_parsed.append({'bus_number': incoming_bus_number, 'bus_dest': incoming_bus_dest, 'bus_due': incoming_bus_due})
			else:
				bus_stop_parsed.append({'bus_number': incoming_bus_number, 'bus_dest': incoming_bus_dest, 'bus_due': incoming_bus_due})
		
		return render.bus_stop_schedule(bus_stop_parsed)

class Route:
	def GET(self):
		
		user_input = web.input(origin="1 George Street, Newmarket", destination="University Of Auckland Clocktower")
		
		origin = user_input.origin
		destination = user_input.destination

		request = urllib2.Request(url=("http://m.maxx.co.nz/mobile-journey-detail.aspx?jp-form-from=1%20George%20Street,%20Newmarket&jp-form-from-coords=&jp-form-to=University%20Of%20Auckland%20Clocktower&jp-form-to-coords=&jp-form-leave-arrive=A&jp-form-hour=08&jp-form-minute=30&jp-form-ampm=PM&jp-form-date=16-01-2012&jp-form-index=2"))
		response = urllib2.urlopen(request)
                soup = BeautifulSoup(response)
                route_table = soup.find('table', {'id': 'journey-details'})
                steps =  route_table.findAll('tr')
                output = ""
                for step in steps:
                        output += str(step) + "\n\n\n"
                
                return output

	def POST(self):
		'''
		When form gets posted, it calls POST method
		'''
		user_input = web.input(origin="1 George Street, Newmarket", destination="University Of Auckland Clocktower")
		
		origin = user_input.origin
		destination = user_input.destination
		
		print origin

if __name__ == "__main__":
    app.run()
