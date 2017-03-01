#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import urllib2

import db

# all datas aqi
api_url = "http://www.pm25.in/api/querys/aqi_details.json"
city = "guangzhou"
token = "5j1znBVAsnSf5xQyNQyq"

values = {'city': city, 'token': token}
datas = urllib.urlencode(values)
url = api_url + '?' + datas

api_details = urllib2.urlopen(url)

try:
    all_datas = json.load(api_details)
    print all_datas
    # for data in datas:

except:
    print "not data"

