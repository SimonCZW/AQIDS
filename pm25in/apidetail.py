#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import urllib2
import datetime
from collections import OrderedDict

import db

def get_items(data):
    """
    return table items from data for create table.
    """
    _table_items = OrderedDict()
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, int):
            _table_items[key] = "int"
        elif isinstance(value, float):
            _table_items[key] = "float"
        else:
            # include time_point
            _table_items[key] = "varchar(255)"
    return _table_items

def insert_db(table_name, primary_keys, data):
    """
    Insert data in to table.

    First, judging whether had created table, if not create it(having primary).
    Second, it will get the type of data items for creating table.//get_items()
    After creating table, insert data into table.

    Usage:
        with db.connection():
            apidetail.insert_db(table_name, primary_keys, data)

        Using "with db.connection():":
        Because insert_db do multiply action in one MySQLdb connection.
    """
    # has no table and create it.
    if not db.has_table(table_name):
        table_items = get_items(data)

        try:
            db.create_table(table_name, primary_keys, table_items)
        except Exception, e:
            print  'Created table failed. Reason:', e

    try:
        db.insert(table_name, data)
    except Exception, e:
        print 'Inserted data into %s failed.(data: %s)' % (table_name, data)
        print e

def encode_data(data):
    """ input dict, encode k & v  utf8 """
    for k, v in data.iteritems():
        data.pop(k)
        k = k.encode('utf-8')
        if isinstance(v, unicode):
            data[k] = v.encode('utf-8')
        else:
            data[k] = v
    return data

def order_data(data, orderlist):
    """
    Input a dict, and return Orderdict().Order by orderlist.
    """
    order_data = OrderedDict()
    for item in orderlist:
        order_data[item] = data.get(item)
    return order_data

def handle_data(city, now_time, data):
    """
    Input params:
        city for create table.
        now_time for newest data.
        data is a dict, key for create table and value store in table.
    There two type of data.(each station data and average data)
    """
    # example: 2017-03-01T16:00:00Z -> 2017030216(year-mon-day-hour)
    timestamp = datetime.datetime.strptime(
        data['time_point'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d%H")
    data['time_point'] = timestamp

    # is newest data, allow 1 hour error
    if int(now_time) > int(timestamp) + 1:
        print "Not the newest data: ", data
    # newest data, insert to db
    else:

        # last data: average city data
        if data['station_code'] is None and data['position_name'] is None:
            data.pop('station_code')
            data.pop('position_name')

            orderlist = ['time_point', 'area', 'aqi', 'quality',
                         'primary_pollutant', 'pm2_5', 'pm2_5_24h', 'pm10',
                         'pm10_24h', 'no2', 'no2_24h', 'so2', 'so2_24h', 'co',
                         'co_24h', 'o3', 'o3_8h', 'o3_24h', 'o3_8h_24h']
            data = order_data(data, orderlist)

            table_name = city.capitalize() + "Average"
            primary_keys = ['time_point']
            insert_db(table_name, primary_keys, data)
        # station data
        else:
            orderlist = ['station_code', 'area', 'position_name', 'time_point',
                         'aqi', 'quality', 'primary_pollutant', 'pm2_5',
                         'pm2_5_24h', 'pm10', 'pm10_24h', 'no2', 'no2_24h',
                         'so2', 'so2_24h', 'co', 'co_24h', 'o3', 'o3_8h',
                         'o3_24h', 'o3_8h_24h']
            data = order_data(data, orderlist)
            primary_keys = ['station_code']
            table_name = city.capitalize() + timestamp
            insert_db(table_name, primary_keys, data)


def _get_api_base(api_url, token, other_params):
    """
    Base api request function, Return json type data from API.
    Params is a dict for url params.

    For example:
        api_url: http://api.com
        token: xxxxxxx
        params: {'city': 'guangzhou', 'station': 'no'}
        And the request url:
            http://api.com?token=xxxxxxx&city=guangzhou&station=no

    Has no "try, except" syntaxa, so the best USAGE is:
        try:
            _get_api_base()
        except:
            ...
    """
    params = {'token': token}
    params.update(other_params)
    url_params = urllib.urlencode(params)
    url = api_url + '?' + url_params
    req = urllib2.urlopen(url)
    json_datas = json.load(req)
    return json_datas

def get_api_details_by_city(city, token):
    """
    input api, city, and token. return json data from api_url.
    """
    api = "http://www.pm25.in/api/querys/aqi_details.json"
    try:
        all_datas = _get_api_base(api, token, {'city': city})
        return all_datas
    except Exception, e:
        print "not data from %s", api
        print e

def get_api_details_by_station(station_code, token):
    """
    input api, station, and token. return json data from api_url.
    """
    api = "http://www.pm25.in/api/querys/aqis_by_station.json"
    try:
        station_datas = _get_api_base(api, token,
                                      {'station_code': station_code})
        return station_datas
    except Exception, e:
        print "not data from %s", api

def get_station_list_by_city(city, token):
    """
    Return a city's stations code list.
    original return data format:
        {
          "city": "广州",
            "stations": [
                    {
                              "station_name": "广雅中学",
                              "station_code": "1345A"
                            },
                    ...
            ]
        }
    """
    station_code_list = []
    api = "http://www.pm25.in/api/querys/station_names.json"
    try:
        stations_list = _get_api_base(api, token, {'city': city})
        for station in stations_list.get('stations'):
            station_code_list.append(station['station_code'].encode('utf-8'))
        return station_code_list
    except Exception, e:
        print "not data from %s", api


def main():
    # connect to database
    db.create_engine(user='root', password='123456', database='test')

    city = "guangzhou"
    token = "5j1znBVAsnSf5xQyNQyq"

    # 1. Get all city data in one time
    all_datas = get_api_details_by_city(city, token)

    # 2. Get data by each station
    # stations_code_list = get_station_list_by_city(city, token)
    # all_datas = []
    # for station in stations_code_list:
        # station_data = get_api_details_by_station(station, token)
        # all_datas = all_datas + station_data

    # Print sorry message. Cannot get data.
    if isinstance(all_datas, dict):
        for v in all_datas.itervalues():
            print v
        return

    # print all_datas

    now_time = datetime.datetime.now().strftime("%Y%m%d%H")
    # print now_time
    with db.connection():
        for data in all_datas:
            # pass Bad station 1347A
            if data['station_code'] == '1347A':
                continue
            handle_data(city, now_time, data)

if __name__ == '__main__':
    main()
