#!/usr/bin/env python
# encoding: utf-8
"""
bus.py

Authors:     Hengjie Wang
Authors:     Jordan Thoms
Date:        15 Jan 2012

Copyright (c) 2012. All Rights Reserved.

"""

import sys
import os
from BeautifulSoup import BeautifulSoup    # For processing HTML

import json
import urllib2, urllib

import web
from web import form

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7"

urls = (
    '/route', 'Route',
    '/stop/([0-9]+)', 'BusStopSchedule',
    '/', 'Index',
    '/json_search_addr/', 'SearchAddressWrapper',
)

render = web.template.render('templates/', base='template_layout')
app = web.application(urls, globals())

class Common(object):
    def request(self, url):
        '''
        Common code to handle the request and deal with
        the case where it fail
        '''
        headers = {'User-Agent' : USER_AGENT}
        
        try:
            request = urllib2.Request(url=url, headers=headers)
            response = urllib2.urlopen(request)
        except Exception:
            # Raise exception for now, but in future we should do something
            # graceful
            raise
        
        return response
    
    def bus_stop_schedule(self, bus_stop_number, filter_bus_number=[]):
        '''
        Get the bus stop number and relevant bus numbers to destination
        
        bus_stop_number:
        filter_bus_number: Return only buses found in this list. Default is return all buses
        
        Return a list of dictionaries, return empty list if nothing to return
        '''
        
        bus_stop_parsed = []
        
        if not bus_stop_number:
            return bus_stop_parsed
        
        url = "http://m.maxx.co.nz/mobile-departure-board.aspx?stop=" + str(bus_stop_number)
        response = self.request(url)
        
        soup = BeautifulSoup(response)
        incoming_buses = soup.findAll('tr', attrs={'data-theme' : 'a'})
        
        for row in incoming_buses:
            try:
                # if no buses then we don't want to do anything
                if row.contents[1].contents == "NO BUSES":
                    break
                
                incoming_bus_number = row.contents[1].contents
                incoming_bus_dest = row.contents[3].contents # bound dest
                incoming_bus_due = row.contents[5].contents # in minutes
            except IndexError:
                # deal with it properly later
                raise
            
            incoming_bus = {'bus_number': incoming_bus_number, 'bus_dest': incoming_bus_dest, 'bus_due': incoming_bus_due}
            
            # return only relevant bus data that I care about
            if filter_bus_number:
                # check if you can do that with lists
                if incoming_bus_number in filter_bus_number:
                    bus_stop_parsed.append(incoming_bus)
            else:
                bus_stop_parsed.append(incoming_bus)
        
        return bus_stop_parsed

class SearchAddressWrapper(Common):
    '''
    Wrap around the MAXX JSON API
    '''
    
    def GET(self):
        return self.handle_request()
    def POST(self):
        return self.handle_request()
    
    def handle_request(self):
        user_input = web.input(address="")
        
        result = {'identifier:': '', 'items': []}
        
        if user_input.address:
            # because user_input can be unicode
            address = str(user_input.address)
            
            # dojo likes to put a * (wildcard) at the end of address
            # detect for it and remove it
            if address.endswith("*"):
                address = address[:-1]
            
            # enforce a minimum length before searching
            if len(address) <= 3:
                return result
            
            url = "http://journeyplanner.maxx.co.nz/iptis/ajax/locations-jsonp.asp?" + urllib.urlencode({'term': address})
            response = self.request(url)
            response_text = response.read()
            
            # dirty hack to clean this string to be loaded by json
            parse_text = response_text[1:]
            parse_text = parse_text[:-2]
            parse_list = json.loads(parse_text)
            
            for address in parse_list:
                # dojo configured to search for keys named 'address'
                result['items'].append({'address': str(address['label'])})
        
        return result

class Index(object):
    def GET(self):
        return render.index()

class BusStopSchedule(Common):
    def GET(self, bus_stop_number):
        return self.bus_stop_schedule(bus_stop_number)
    def POST(self, bus_stop_number):
        return self.bus_stop_schedule(bus_stop_number)

class Route:
    def GET(self):
        user_input = web.input(origin="1 George Street, Newmarket", destination="University Of Auckland Clocktower")
        
        url_params = urllib.urlencode({'jp-form-from': user_input.origin, 'jp-form-to': user_input.destination})
        
        request = urllib2.Request(url=("http://m.maxx.co.nz/mobile-journey-detail.aspx?jp-form-to-coords=&jp-form-leave-arrive=A&jp-form-hour=08&jp-form-minute=30&jp-fo-ampm=PM&jp-form-date=16-01-2012&jp-form-index=1&" + url_params))

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
