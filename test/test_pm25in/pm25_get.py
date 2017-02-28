#!/usr/bin/env python
# -*- coding-utf8 -*-

import json
import requests

city="guangzhou"
token="5j1znBVAsnSf5xQyNQyq"

pm25 = requests.get(
    'http://www.pm25.in/api/querys/pm2_5.json?city=%s&token=%s' % (city, token))

# print "pm25 text", pm25.text
# print "type", type(pm25)

# need to be encode
try:
    parse_json2=json.loads(pm25.text)
    print "pm25 json2", parse_json2
    print "pm25 json2[0]", parse_json2[0]
except:
    print "pm25 not json2"

# try:
    # print "pm25.json", pm25.json
    # pj = pm25.json
    # print "type: pj", type(pj)
# except:
    # pass
