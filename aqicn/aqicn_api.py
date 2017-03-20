#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import datetime
# from collections import OrderedDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
from wrapper.jsonapibase import GetJsonApiBase

class Aqicn(GetJsonApiBase):

    _district_mapping = {'guangzhou': ['广州均值', None, None],
                         'guangdong/guangzhou/us-consulate': ['美国领事馆', '天河区', True],
                         'guangdong/guangzhou/tiyuxi': ['体育西', '天河区', True],
                         'guangdong/guangzhou/modieshazhan': ['磨碟沙', '海珠区', True],
                         'guangdong/guangzhou/haizhuchisha': ['海珠赤沙', '海珠区', True],
                         'guangdong/guangzhou/haizhubaogang': ['海珠宝岗', '海珠区', True],
                         'guangdong/guangzhou/gongyuanqian': ['公园前', '越秀区', True],
                         'guangdong/guangzhou/liwanxicun': ['荔湾西村', '荔湾区', True],
                         'guangdong/guangzhou/luhu': ['白云麓湖', '白云区', False],
                         'guangdong/guangzhou/huaduchengqu': ['花都城区', '花都区', False],
                         'guangdong/guangzhou/zhudong': ['花都竹洞', '花都区', False],
                         'guangdong/guangzhou/tianhu': ['从化天湖', '从化区', False],
                         'guangdong/guangzhou/luogangzhenlong': ['萝岗镇龙', '黄埔区', False],
                         'guangdong/guangzhou/huangpudashadi': ['大沙地', '黄浦区', False],
                         'guangdong/guangzhou/fanyushiqiao': ['番禺市桥', '番禺区', False],
                         'guangdong/guangzhou/wanqingsha': ['万顷沙', '番禺区', False]}

    def __init__(self, token):
        """
        Init Aqicn:
            set self.token
            create connection with MySQLdb
            set api_base
            update create table name
        """
        super(Aqicn, self).__init__(token)
        self.api_base = 'http://api.waqi.info/feed'
        self.station_datas = []
        self.aqi_datas = []

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
            return self.get_api_base(_api, other_params)
        except Exception, e:
            print "Cannot get data from: ", _api
            print e
            return None

    def _handle_aqi_data(self, data):
        """
        Handle each station data.
            Filter useful data from original json data,
            Store data into DB and if table has not been created, create it.
        """
        # _aqi_data = OrderedDict()
        if data['status'] != 'ok':
            return

        _aqi_data = {}

        _station_code = re.match('.*city/(.*)/$' , data['data']['city']['url']).group(1)

        _aqi_data['station_name'] = self._district_mapping[_station_code][0]

        _aqi_data['time_point']= data['data']['time']['s']
        # _aqi_data['time_point'] = datetime.datetime.strptime(
            # data['data']['time']['s'], "%Y-%m-%d %H:%M:%S").strftime(
                # "%Y%m%d%H%M%S")
        _aqi_data['date'] = datetime.datetime.strptime(
            data['data']['time']['s'], "%Y-%m-%d %H:%M:%S").strftime(
                "%Y%m%d")

        if data['data'].has_key('dominentpol'):
            _aqi_data['dominentpol'] = data['data']['dominentpol']
        else:
            _aqi_data['dominentpol'] = None

        if data['data']['aqi'] == '-':
            _aqi_data['aqi'] = None
        else:
            _aqi_data['aqi'] = data['data']['aqi']

        # get iaqi detail data:
        _all_iaqi_items = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co',
                           't', 'w', 'h', 'd', 'p']
        _item_mappings = {'pm25': 'pm25_iaqi', 'pm10': 'pm10_iaqi',
                          'o3': 'o3_iaqi', 'no2': 'no2_iaqi',
                          'so2': 'so2_iaqi', 'co': 'co_iaqi',
                          't': 'temperature', 'w': 'wind',
                          'h': 'relative_humidity', 'd': 'dew',
                          'p': 'atmospheric_pressure'}
        for _item in _all_iaqi_items:
            if data['data']['iaqi'].has_key(_item):
                _aqi_data[_item_mappings[_item]] = data['data'][
                    'iaqi'][_item]['v']
            else:
                if _item == 'r': #rain precipitation
                    _aqi_data[_item_mappings[_item]] = ''
                else:
                    _aqi_data[_item_mappings[_item]] = 0.0

        self.aqi_datas.append(_aqi_data)

    def _handle_station_data(self, data):
        if data['status'] != 'ok':
            return

        _station_data = {}
        _station_code = re.match('.*city/(.*)/$' , data['data']['city']['url']).group(1)

        _station_data['station_name'] = self._district_mapping[_station_code][0]
        if _station_data['station_name'] == '广州均值':
            _station_data['station_type'] = '城市均值'
        else:
            _station_data['station_type'] = '美国领事馆点'

        # wei / jing
        _station_data['latitude'] = data['data']['city']['geo'][0]
        _station_data['longitude'] = data['data']['city']['geo'][1]

        _station_data['city'] = '广州'

        _station_data['district'] = self._district_mapping[_station_code][1]
        _station_data['center'] = self._district_mapping[_station_code][2]

        self.station_datas.append(_station_data)

    def run(self, stations_url_list):
        """
        Input a list of station's API, request it and handle its return data.
        """
        for station_url in stations_url_list:
            _station_data = self.get_aqi_data_by_stations(station_url)
            self._handle_aqi_data(_station_data)
            self._handle_station_data(_station_data)



if __name__ == '__main__':
    token = 'de552bc7dcefe469e68466f97d31f0c88faef2c1'
    gz = Aqicn(token)


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
