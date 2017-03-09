#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import datetime
from collections import OrderedDict

sys.path.append('/root/AQIDS/wrapper')
from db import connection
from jsonapibase import GetJsonAqiBase

class Aqicn(GetJsonAqiBase):
    def __init__(self, token, **database):
        """
        Init Aqicn:
            set self.token
            create connection with MySQLdb
            set api_base
            update create table name
        """
        super(Aqicn, self).__init__(token, **database)
        self.api_base = 'http://api.waqi.info/feed'
        self.update_table_name()

    def get_aqi_data_by_stations(self, station_url, other_params=None):
        """
        Request data from API.
        Success 200 return json data format:
            {
                "status": "ok",
                "data": {
                    "aqi": xx,
                    "idx": xx,
                    "attribution": [
                        {
                            "url": xx,
                            "name": xx,
                        }
                        ...
                    ],
                    "city": {
                        "geo": [ xx, xx],
                        "name": xx,
                        "url": xx,
                    },
                    "dominentpol": xx,
                    "iaqi":{
                        "pm25": {"v": xx}
                        "pm10": {"v": xx}
                        ...
                    },
                    "time": {
                        "s": "YYYY-mm-dd HH:MM:SS"
                        "tz": xx,
                        "v": xx
                    }
        """
        _api = self.api_base + station_url
        try:
            return self._get_api_base(_api, other_params)
        except Exception, e:
            print "Cannot get data from: ", _api
            print e
            return None

    def handle_data(self, data):
        """
        Handle each station data.
            Filter useful data from original json data,
            Store data into DB and if table has not been created, create it.
        """
        _aqi_data = OrderedDict()
        if data['status'] != 'ok':
            return

        _aqi_data['station_id'] = data['data']['idx']

        # example: city/guangdong/guangzhou/tiyuxi -> guangdong_guangzhou_tiyuxi
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

        # get iaqi detail data:
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
                if _item == 'r': #rain precipitation
                    _aqi_data[_item_mappings[_item]] = ''
                else:
                    _aqi_data[_item_mappings[_item]] = 0.0

        _primary_keys = ['station_id', 'time_point']
        self.insert_db(self.table_name, _primary_keys, _aqi_data)

    def update_table_name(self):
        """
        Every day create a table.
        """
        _today = datetime.datetime.now().strftime("%Y%m%d")
        self.table_name = 'Aqicn' + _today

    def run(self, stations_url_list):
        """
        Input a list of station's API, request it and handle its return data.
        """
        with connection():
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
