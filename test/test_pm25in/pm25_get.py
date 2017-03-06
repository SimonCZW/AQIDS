#!/usr/bin/env python
# -*- coding-utf8 -*-

import json
import urllib
import urllib2

# just for pm10
# url = "http://www.pm25.in/api/querys/pm10.json"
# just for pm2.5
# url = "http://www.pm25.in/api/querys/pm2_5.json"
# all datas
url = "http://www.pm25.in/api/querys/aqi_details.json"
city = "guangzhou"
token = "5j1znBVAsnSf5xQyNQyq"

values = {'city': city, 'token': token}
datas = urllib.urlencode(values)
lurl = url + '?' + datas
req = urllib2.Request(lurl)

# urllib2respose = urllib2.urlopen(lurl)
urllib2respose = urllib2.urlopen(req)
# print urllib2respose.headers.type
try:
    jdata = json.load(urllib2respose)
    print "jdata", jdata
    # for data in jdata:
        # print data["aqi"]
        # try:
            # with open('simple_data.txt', 'w+') as dfile:
                # dfile.write(data)
        # except:
            # print "cannot write."
except:
    print "not jdata"


# requests lib:
# import requests
# pm25 = requests.get(
    # 'http://www.pm25.in/api/querys/pm2_5.json?city=%s&token=%s' % (city, token))

# print "pm25 text", pm25.text
# print "type", type(pm25)

# need to be encode
# try:
    # parse_json2=json.loads(pm25.text)
    # print "pm25 json2", parse_json2
    # print "pm25 json2[0]", parse_json2[0]
# except:
    # print "pm25 not json2"
