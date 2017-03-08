#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import json
import urllib
import urllib2
import datetime
from collections import OrderedDict

sys.path.append('/root/AQIDS/wrapper')
import db

class GetJsonAqiBase(object):
    def __init__(self, token, **database):
        self.token = token
        db.create_engine(**database)

    def _get_api_base(self, api_url, other_params=None):
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
        params = {'token': self.token}
        if other_params is not None:
            params.update(other_params)
        url_params = urllib.urlencode(params)
        url = api_url + '?' + url_params
        req = urllib2.urlopen(url)
        json_datas = json.load(req)
        return json_datas

    def order_data(self, data, orderlist):
        """
        Input a dict, and return Orderdict().Order by orderlist.
        """
        order_data = OrderedDict()
        for item in orderlist:
            order_data[item] = data.get(item)
        return order_data

    def insert_db(self, table_name, primary_keys, data):
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
            table_items = self.get_items(data)

            try:
                db.create_table(table_name, primary_keys, table_items)
            except Exception, e:
                print  'Created table failed. Reason:', e

        try:
            db.insert(table_name, data)
        except Exception, e:
            print 'Inserted data into %s failed.(data: %s)' % (table_name, data)
            print e

    def get_items(self, data):
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
                _table_items[key] = "varchar(255)"
        return _table_items

    def handle_data(self, data):
        pass


class Aqicn(GetJsonAqiBase):
    def __init__(self, token, **database):
        super(Aqicn, self).__init__(token, **database)
        self.json_order_datas = []
        self.api_base = 'http://api.waqi.info/feed'

    def get_aqi_data_by_stations(self, station_url, other_params=None):
        _api = self.api_base + station_url
        try:
            return self._get_api_base(_api, other_params)
        except Exception, e:
            print "Cannot get data from: ", _api
            print e
            return None

    def handle_data(self, data):
        _aqi_data = OrderedDict()
        if data['status'] != 'ok':
            return

        _aqi_data['idx'] = data['data']['idx']
        _aqi_data['station_name'] = re.match(
            '.*city/(.*)/$' , data['data']['city']['url']).group(1).replace(
                '/', '_')
        _aqi_data['time_point'] = datetime.datetime.strptime(
            data['data']['time']['s'], "%Y-%m-%d %H:%M:%S").strftime(
                "%Y%m%d%H%M%S")

        if data['data'].has_key('dominentpol'):
            _aqi_data['dominentpol'] = data['data']['dominentpol']
        else:
            _aqi_data['dominentpol'] = ''

        if data['data']['aqi'] == '-':
            _aqi_data['aqi'] = 0
        else:
            _aqi_data['aqi'] = data['data']['aqi']

        _all_iaqi_items = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co',
                           't', 'w', 'r', 'h', 'd', 'p', 'wd']
        _item_mappings = {'pm25': 'pm25', 'pm10': 'pm10', 'o3': 'o3',
                          'no2': 'no2', 'so2': 'so2', 'co': 'co',
                          't': 'temperature', 'w': 'wind', 'r': 'rain',
                          'h': 'relative_humidity', 'd': 'dew',
                          'p': 'atmospheric_pressure', 'wd': 'wd'}
        for _item in _all_iaqi_items:
            if data['data']['iaqi'].has_key(_item):
                _aqi_data[_item_mappings[_item]] = data['data'][
                    'iaqi'][_item]['v']
            else:
                #rain precipitation
                if _item == 'r':
                    _aqi_data[_item_mappings[_item]] = ''
                else:
                    _aqi_data[_item_mappings[_item]] = 0.0


        _table_name = 'Aqicn'
        _primary_keys = ['idx', 'time_point']
        self.insert_db(_table_name, _primary_keys, _aqi_data)

    def run(self, stations_url_list):
        with db.connection():
            for station_url in stations_url_list:
                _station_data = self.get_aqi_data_by_stations(station_url)
                self.handle_data(_station_data)


if __name__ == '__main__':
    token = 'de552bc7dcefe469e68466f97d31f0c88faef2c1'
    database = dict(user='root', password='123456', database='test')
    gz = Aqicn(token, **database)

    stations_url_list = ['/guangzhou/',
                         '/guangdong/guangzhou/us-consulate/',
                         '/guangdong/guangzhou/tiyuxi/',
                         '/guangdong/guangzhou/modieshazhan/',
                         '/guangdong/guangzhou/haizhuchisha/',
                         '/guangdong/guangzhou/haizhubaogang/',
                         '/guangdong/guangzhou/gongyuanqian/',
                         '/guangdong/guangzhou/liwanxicun/',
                         '/guangdong/guangzhou/luhu/',
                         '/guangdong/guangzhou/huaduchengqu/',
                         '/guangdong/guangzhou/zhudong/',
                         '/guangdong/guangzhou/tianhu/',
                         '/guangdong/guangzhou/luogangzhenlong/',
                         '/guangdong/guangzhou/huangpudashadi/',
                         '/guangdong/guangzhou/fanyushiqiao/',
                         '/guangdong/guangzhou/wanqingsha/']

    gz.run(stations_url_list)
