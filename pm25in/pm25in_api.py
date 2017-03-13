#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime

sys.path.append('/root/AQIDS/wrapper')
from db import connection
from jsonapibase import GetJsonApiBase

class Pm25in(GetJsonApiBase):
    def __init__(self, token, city, **database):
        """
        Init Aqicn:
            set self.token
            set self.city
            create connection with MySQLdb
            update create table name
        """
        super(Pm25in, self).__init__(token, **database)
        self.city = city

    def handle_data(self, now_time, data):
        """
        Input params:
            city for create table.
            now_time for newest data.
            data is a dict, key for create table and value store in table.
        There two type of data.(each station data and average data)
        """
        # example: 2017-03-01T16:00:00Z -> 2017030216(year-mon-day-hour)
        hour_timestamp = datetime.datetime.strptime(
            data['time_point'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d%H")

        # is newest data, allow 1 hour error
        if int(now_time) > int(hour_timestamp) + 1:
            print "Not the newest data: ", data

        else:
            timestamp = datetime.datetime.strptime(
                data['time_point'], "%Y-%m-%dT%H:%M:%SZ").strftime(
                    "%Y%m%d%H%M%S")
            data['time_point'] = timestamp

            # last data: average city data
            if data['station_code'] is None and data['position_name'] is None:
                data['station_code'] = self.city
                data['position_name'] = self.city

            _orderlist = ['station_code', 'area', 'position_name', 'time_point',
                          'aqi', 'quality', 'primary_pollutant', 'pm2_5',
                          'pm2_5_24h', 'pm10', 'pm10_24h', 'no2', 'no2_24h',
                          'so2', 'so2_24h', 'co', 'co_24h', 'o3', 'o3_8h',
                          'o3_24h', 'o3_8h_24h']
            data = self.order_data(data, _orderlist)

            _primary_keys = ['station_code', 'time_point']
            _table_name = self.city.capitalize() + now_time[:-2]  # today
            self.insert_db(_table_name, _primary_keys, data)

    def get_all_data_by_city(self):
        """
        input api, city, and token. return json data from api_url.
        """
        _api = "http://www.pm25.in/api/querys/aqi_details.json"
        try:
            _all_datas = self.get_api_base(_api, {'city': self.city})
            # Print sorry message. Cannot get data.
            if isinstance(_all_datas, dict):
                for error in _all_datas.itervalues():
                    print error
                return []
            return _all_datas
        except Exception, e:
            print "not data from %s", _api
            print e

    def get_data_by_station(self, station_code):
        """
        input api, station, and token. return json data from api_url.
        """
        _api = "http://www.pm25.in/api/querys/aqis_by_station.json"
        try:
            _station_datas = self.get_api_base(_api,
                                                {'station_code': station_code})
            return _station_datas
        except Exception, e:
            print "not data from %s", _api

    def get_station_list_by_city(self):
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
        _station_code_list = []
        _api = "http://www.pm25.in/api/querys/station_names.json"
        try:
            _stations_list = self.get_api_base(_api, {'city': self.city})
            for _station in _stations_list.get('stations'):
                _station_code_list.append(
                    _station['station_code'].encode('utf-8'))
            return _station_code_list
        except Exception, e:
            print "not data from %s", _api

    def get_all_data_by_stations(self):
        """
        First, get self.city's stations list.
        Second, get station's data one by one.
        """
        _stations_code_list = self.get_station_list_by_city()
        _all_datas = []
        for station in _stations_code_list:
            _station_data = self.get_data_by_station(station)
            _all_datas = _all_datas + _station_data
        return _all_datas

    def run(self):
        """
        Two usage:
            1. Get all city data in one time
            2. Get data by each station but without average data
        """
        # 1. Get all city data in one time
        all_datas = self.get_all_data_by_city()

        # 2. Get data by each station but without average data
        # all_datas = self.get_all_data_by_stations()

        if len(all_datas) == 0:
            print "No json data."
            return

        now_time = datetime.datetime.now().strftime("%Y%m%d%H")
        with connection():
            for data in all_datas:
                if data['station_code'] == '1347A': # pass Bad station 1347A
                    continue
                self.handle_data(now_time, data)

if __name__ == '__main__':
    city = "guangzhou"
    token = "5j1znBVAsnSf5xQyNQyq"
    database = dict(user='root', password='123456', database='test')

    gz = Pm25in(token, city, **database)
    gz.run()
