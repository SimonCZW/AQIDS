#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import urllib2
import datetime

import db

# all datas aqi
api_url = "http://www.pm25.in/api/querys/aqi_details.json"
city = "guangzhou"
token = "5j1znBVAsnSf5xQyNQyq"

now_time = datetime.datetime.now().strftime("%Y%m%d%H")

values = {'city': city, 'token': token}
datas = urllib.urlencode(values)
url = api_url + '?' + datas
api_details = urllib2.urlopen(url)

# connect to database
db.create_engine(user='root', password='123456', database='test')

def get_items(data):
    """
    return table items from data for create table.
    """
    table_items = {}
    for key, value in data.iteritems():
        if isinstance(value, int):
            table_items[key] = "int"
        elif isinstance(value, float):
            table_items[key] = "float"
        # elif isinstance(value, str):
        else:
            # include time_point
            table_items[key] = "varchar(255)"

def insert_db(table_name, data):
    """
    insert data in to table.
    Fisrtly, judge whether had created table, if not create it.
    """
    # has no table and create it.
    if not db.has_table(table_name):
        table_items = get_items(data)
        # station data, create table each hour data using station as primary
        if data.has_key('station_code') and data.has_key('position_name'):
            primary_keys = ['station_code']
        # average data, create table CityAverage using time_point as primary
        else:
            primary_keys = ['time_point']

        try:
            db.create_table(table_name, primary_keys, table_items)
        except Exception, e:
            print  'Created table failed. Reason:', e

    try:
        db.insert(table_name, data)
    except Exception, e:
        print 'Inserted data into %s failed.(data: %s)' % (table_name, data)
        print e


try:
    all_datas = json.load(api_details)
    # print all_datas
    for data in datas:
        # example: 2017-03-01T16:00:00Z -> 2017030216(year-mon-day-hour)
        timestamp = datetime.datetime.strptime(data['time_point'],
                                               "%Y-%m-%fT%H:%M:%SZ").strftime(
                                                   "%Y%m%d%H")
        data['time_point'] = timestamp

        # is newest data?
        if now_time > timestamp:
            print "Not the newest data: ", data
            datas.remove(data)
        # newest data, insert to db
        else:
            # last data: average city data
            if data['station_code'] is None and data['position_name'] is None:
                table_name = city.capitalize() + "Average"
                data.pop('station_code')
                data.pop('position_name')
                insert_db(table_name, data)
            # station data
            else:
                table_name = city.capitalize() + timestamp
                insert_db(table_name, data)

except:
    print "not data from %s", url

