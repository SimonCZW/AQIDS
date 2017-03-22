#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import urllib2
import datetime

class Gzepb(object):
    """
    For www.gzepb.gov.cn/api/ .
    Request data.
    """
    _headers = {'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64)',
                'Referer': 'http://210.72.1.216:8080/gzaqi_new/RealTimeDate.html',
                'Origin': 'http://210.72.1.216:8080'}

    def __init__(self):
        self.api = 'http://210.72.1.216:8080/gzaqi_new/MapData.cshtml'

    @classmethod
    def get_station_data(cls):
        """
        Return all station information list.
        """
        return cls()._handle_station_data()

    @classmethod
    def get_aqi_data(cls):
        """
        # Return all aqi information list.
        """
        return cls()._handle_aqi_data()

    @classmethod
    def get_aqi_time(cls):
        """
        Return newest aqi time.
        """
        return cls()._get_aqi_time()

    def _gzepb_base_api(self, data=None, json_format=True, other_params=None):
        """
        Base api request function, return data from API.

        Argument data is request data.
        Argument json_format is a mark that use to judging
            whether the response data is json format or not.(default: json)
        Arguement other_params is a dict for url params.

        For example:
            params: {'city': 'guangzhou', 'station': 'no'}
            And the request url:
                http://api.com?city=guangzhou&station=no
            data: post request data
        """
        params = {}
        if other_params is not None:
            params.update(other_params)
        url_params = urllib.urlencode(params)
        if url_params != '':
            url = self.api + '?' + url_params
        else:
            url = self.api

        req = urllib2.Request(url, self._headers)
        req.add_data(data)
        try:
            response = urllib2.urlopen(req)
            if json_format is True:
                return json.load(response)
            else:
                return response.read()
        except Exception, e:
            print "Request %s error." % url,
            print e

    def _get_aqi_time(self):
        """
        POST request for newest aqi data real time.
        Return format(list):
            ["YYYY","mm","dd","HH"]
        """
        _req_data = 'OpType=GetAQITime'
        _aqi_time = self._gzepb_base_api(data=_req_data)
        return _aqi_time

    def _get_aqi_data(self):
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
        _req_data = 'OpType=GetAllRealTimeData'
        _all_datas = self._gzepb_base_api(data=_req_data, json_format=False)

        import re
        import json
        _all_datas = re.sub(r'new Date\((\d+)\)', r'\1', _all_datas)
        _aqi_json_data = json.loads(_all_datas)
        return _aqi_json_data

    def _get_all_stations(self):
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
        _req_data = 'OpType=GetAllStations'
        _all_stations = self._gzepb_base_api(data=_req_data)
        return _all_stations

    def _handle_aqi_data(self):
        """
        handle the original response data for all realtime aqi data.
        """
        _aqi_datas = []
        _origin_aqi_datas = self._get_aqi_data()
        for _origin_data in _origin_aqi_datas:
            _aqi_data = {}
            _aqi_data['time_point'] = datetime.datetime.fromtimestamp(
                int(str(_origin_data['AQITIME'])[:10])).strftime(
                    "%Y-%m-%d %H:%M:%S")
            _aqi_data['date'] = "%s-%s-%s"  % (_origin_data['YY'],
                                              _origin_data['MM'],
                                              _origin_data['DD'])
            _aqi_data['aqi'] = _origin_data['AQI']
            _aqi_data['dominentpol'] = _origin_data['PRIMARY'].strip()
            _aqi_data['so2_1h'] = _origin_data['SO2_1H']
            _aqi_data['so2_24h'] = _origin_data['SO2_24H']
            _aqi_data['no2_1h'] = _origin_data['NO2_1H']
            _aqi_data['no2_24h'] = _origin_data['NO2_24H']
            _aqi_data['pm10_1h'] = _origin_data['PM10_1H']
            _aqi_data['pm10_24h'] = _origin_data['PM10_24H']
            _aqi_data['co_1h'] = _origin_data['CO_1H']
            _aqi_data['co_24h'] = _origin_data['CO_24H']
            _aqi_data['o3_1h'] = _origin_data['O3_1H']
            _aqi_data['o3_1h_24h'] = _origin_data['O3_1H_24H']
            _aqi_data['o3_8h'] = _origin_data['O3_8H']
            _aqi_data['o3_8h_24h'] = _origin_data['O3_8H_24H']
            _aqi_data['pm25_1h'] = _origin_data['PM2_5_1H']
            _aqi_data['pm25_24h'] = _origin_data['PM2_5_24H']
            _aqi_data['so2_iaqi'] = _origin_data['SO2_1H_AQI']
            _aqi_data['no2_iaqi'] = _origin_data['NO2_1H_AQI']
            _aqi_data['pm10_iaqi'] = _origin_data['PM10_1H_A']
            _aqi_data['co_iaqi'] = _origin_data['CO_1H_AQI']
            _aqi_data['o3_iaqi'] = _origin_data['O3_1H_AQI']
            _aqi_data['o3_iaqi_8h'] = _origin_data['O3_8H_AQI']
            _aqi_data['pm25_iaqi'] = _origin_data['PM2_5_1HA']
            _aqi_data['quality'] = _origin_data['QUALITY'].strip()
            _aqi_data['station_name'] = _origin_data['DWNAME'].strip()

            _aqi_datas.append(_aqi_data)
        return _aqi_datas

    def _handle_station_data(self):
        """
        handle the original response data for all realtime station data.
        """
        _station_datas = []
        _origin_station_datas = self._get_all_stations()
        for _origin_data in _origin_station_datas:
            _station_data = {}
            _station_data['station_name'] = _origin_data['stationName'].strip()
            _station_data['station_type'] = _origin_data['Type'].strip()
            _station_data['display_name'] = _origin_data['DisplayName'].strip()
            # wei / jing
            _station_data['latitude'] = _origin_data['Y']
            _station_data['longitude'] = _origin_data['X']
            _station_data['city'] = '广州'
            _station_data['district'] = _origin_data['stCode'].strip()

            if _origin_data['center'].strip() == u'是':
                _station_data['center'] = True
            else:
                _station_data['center'] = False

            _station_datas.append(_station_data)
        return _station_datas

if __name__ == '__main__':
    pass
    # print Gzepb.get_aqi_data()
    # print Gzepb.get_station_data()
    # print Gzepb.get_aqi_time()
