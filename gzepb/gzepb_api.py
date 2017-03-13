#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
# from collections import OrderedDict

sys.path.append('/root/AQIDS/wrapper')
# from db import connection
from jsonapibase import GetJsonApiBase

class Gzepb(GetJsonApiBase):
    """
    For www.gzepb.gov.cn/api/ .
    Request data.
    """
    _headers = {'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64)',
                'Referer': 'http://210.72.1.216:8080/gzaqi_new/RealTimeDate.html',
                'Origin': 'http://210.72.1.216:8080'}

    def __init__(self, **database):
        super(Gzepb, self).__init__(**database)
        self.base_url = 'http://210.72.1.216:8080'

    def get_aqi_time(self):
        """
        POST request for newest aqi data real time.
        Return format(list):
            ["YYYY","mm","dd","HH"]
        """
        _api = self.base_url + '/gzaqi_new/MapData.cshtml'
        _data = 'OpType=GetAQITime'
        aqi_time = self.get_api_base(api_url=_api,
                                     headers=self._headers, data=_data)
        # print aqi_time

    def get_all_data(self):
        """
        POST request for alll station's real time data in GZ.
        Data is string. And transfer the data format to:
        [
           {
           "STCODE":"440100",
           "STNAME":"广州 ",
           "YY":"2017",
           "MM":"03",
           "DD":"10",
           "AQITIME":new Date(1489129200000),
           "DWCODE":51,
           "DWNAME":"广雅中学",
           "SO2_1H":16.0,
           "SO2_24H":11.0,
           "NO2_1H":79.0,
           "NO2_24H":77.0,
           "PM10_1H":89.0,
           "PM10_24H":69.0,
           "CO_1H":1.35,
           "CO_24H":1.17,
           "O3_1H":3.0,
           "O3_1H_24H":8.0,
           "O3_8H":3.0,
           "O3_8H_24H":4.0,
           "PM2_5_1H":46.0,
           "PM2_5_24H":61.0,
           "AQI":70.0,
           "QUALITY":"良 ",
           "PRIMARY":"颗粒物(PM10) ",
           "SO2_1H_AQI":6.0,
           "NO2_1H_AQI":40.0,
           "PM10_1H_A":70.0,
           "CO_1H_AQI":14.0,
           "O3_1H_AQI":1.0,
           "O3_8H_AQI":2.0,
           "PM2_5_1HA":64.0,
           "AQI_":97.0,
           "QUALITY_":"良 ",
           "PRIMARY_":"二氧化氮 ",
           "_NullFlags":null,
           "Msg":"空气质量可以接受，但某些污染物..."
            },
            ...
        ]
        """
        _api = self.base_url + '/gzaqi_new/MapData.cshtml'
        _req_data = 'OpType=GetAllRealTimeData'
        _all_datas = self.get_api_base(api_url=_api, headers=self._headers,
                                       data=_req_data, json_format=False)

        import re
        import json
        _all_datas = re.sub(r'new Date\((\d+)\)', r'\1', _all_datas)
        _jsondata = json.loads(_all_datas)
        # print type(_jsondata)
        # print _jsondata[0]
        # print _jsondata[0]['AQI']

    def get_all_stations(self):
        """
        POST request for alll stations information in GZ.
        And the station's data format is:
        [
            {
            "ID":12,
            "stCode":"从化市",
            "stationName":"从化良口",
            "DisplayName":"从化良口",
            "Type":"城市评价点",
            "Class":null,
            "Address":null,
            "X":113.bit_length"Y":23.7372,
            "center":"否",
            "remark":null
            },
            ...
        ]
        """
        _api = self.base_url + '/gzaqi_new/MapData.cshtml'
        _data = 'OpType=GetAllStations'
        all_stations = self.get_api_base(api_url=_api,
                                         headers=self._headers, data=_data)

    def handle_data(self):
        pass

if __name__ == '__main__':
    database = dict(user='root', password='123456', database='test')
    gz = Gzepb(**database)
    gz.get_all_data()
    # gz.get_aqi_time()
