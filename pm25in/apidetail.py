#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import urllib2
import datetime

import db

def get_items(data):
    """
    return table items from data for create table.
    """
    _table_items = {}
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
        data['time_point'], "%Y-%m-%fT%H:%M:%SZ").strftime("%Y%m%d%H")
    data['time_point'] = timestamp

    # is newest data?
    if now_time > timestamp:
    # if now_time < timestamp: #Testing data
        print "Not the newest data: ", data
        # all_datas.remove(data)
    # newest data, insert to db
    else:

        # last data: average city data
        if data['station_code'] is None and data['position_name'] is None:
            data.pop('station_code')
            data.pop('position_name')

            table_name = city.capitalize() + "Average"
            primary_keys = ['time_point']
            insert_db(table_name, primary_keys, data)
        # station data
        else:
            primary_keys = ['station_code']
            table_name = city.capitalize() + timestamp
            insert_db(table_name, primary_keys, data)

def get_api_details_by_city(api_url, city, token):
    """
    input api, city, and token. return json data from api_url.
    """
    values = {'city': city, 'token': token}
    params = urllib.urlencode(values)
    url = api_url + '?' + params
    print url
    try:
        # for API data:
        api_details = urllib2.urlopen(url)
        all_datas = json.load(api_details)
        # 增加返回类型? #############################all_datas是什么类型.
        return all_datas
    except:
        print "not data from %s", url

def get_api_details_by_station(api_url, station_code, token):
    """
    input api, station, and token. return json data from api_url.
    """
    values = {'station_code': station_code, 'token': token}
    params = urllib.urlencode(values)
    url = api_url + '?' + params
    try:
        station_api_details = urllib2.urlopen(url)
        station_datas = json.load(station_api_details)
        return station_datas
    except:
        print "not data from %s", url

def get_station_list_by_city(api_url, city, token):
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
    values = {'city': city, 'token': token}
    params = urllib.urlencode(values)
    url = api_url + '?' + params
    station_code_list = []
    try:
        stations_response = urllib2.urlopen(url)
        stations_list = json.load(stations_response)
        for station in stations_list.get('stations'):
            station_code_list.append(station['station_code'].encode('utf-8'))
        return station_code_list
    except:
        print "not data from %s", url

def main():
    # connect to database
    db.create_engine(user='root', password='123456', database='test')

    city = "guangzhou"
    api_url = "http://www.pm25.in/api/querys/aqi_details.json"
    token = "5j1znBVAsnSf5xQyNQyq"
    # all_datas = get_api_details_by_city(api_url, city, token)

    stations_code_list = get_station_list_by_city(
        'http://www.pm25.in/api/querys/station_names.json', 'guangzhou', token)

    all_datas = []
    for station in stations_code_list:
        station_data = get_api_details_by_station(
            'http://www.pm25.in/api/querys/aqis_by_station.json',
            station, token)
        all_datas = all_datas + station_data

    if isinstance(all_datas, dict):
        for v in all_datas.itervalues():
            print v
        return

    now_time = datetime.datetime.now().strftime("%Y%m%d%H")
    with db.connection():
        for data in all_datas:
            handle_data(city, now_time, data)

if __name__ == '__main__':
    main()

    # Testing for insert_db() function...
    # db.create_engine(user='root', password='123456', database='test')
    # testdata={'it1': 'itttttt1', 'it2': 1.5, 'it3': 123}
    # table_name = 'TestTable'
    # primary_keys = ['it1', 'it2']
    # with db.connection():
        # insert_db(table_name, primary_keys, testdata)

    # Testing data
    # all_datas = [{u'pm2_5': 41,
                  # u'primary_pollutant': u'\u9897\u7c92\u7269(PM10)',
                  # u'co': 0.8,
                  # u'pm10': 72,
                  # u'area': u'\u5e7f\u5dde',
                  # u'o3_8h': 45,
                  # u'o3': 66,
                  # u'o3_24h': 72,
                  # u'station_code': u'1345A',
                  # u'quality': u'\u826f',
                  # u'co_24h': 1.1,
                  # u'no2_24h': 82,
                  # u'so2': 13,
                  # u'so2_24h': 17,
                  # u'time_point': u'2017-03-01T16:00:00Z',
                  # u'pm2_5_24h': 67,
                  # u'position_name': u'\u5e7f\u96c5\u4e2d\u5b66',
                  # u'o3_8h_24h': 45,
                  # u'aqi': 61,
                  # u'pm10_24h': 106,
                  # u'no2': 66},
                 # {u'pm2_5': 34,
                  # u'primary_pollutant': u'\u9897\u7c92\u7269(PM10)',
                  # u'co': 0.755,
                  # u'pm10': 53,
                  # u'area': u'\u5e7f\u5dde',
                  # u'o3_8h': 60,
                  # u'o3': 99,
                  # u'o3_24h': 104,
                  # u'station_code': None,
                  # u'quality': u'\u826f',
                  # u'co_24h': 0.927,
                  # u'no2_24h': 66,
                  # u'so2': 12,
                  # u'so2_24h': 18,
                  # u'time_point': u'2017-03-01T16:00:00Z',
                  # u'pm2_5_24h': 59,
                  # u'position_name': None,
                  # u'o3_8h_24h': 60,
                  # u'aqi': 53,
                  # u'pm10_24h': 86,
                  # u'no2': 35}
                # ]
