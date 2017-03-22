#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import datetime

# standalone init
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AQIDS.settings")
# from django.conf import settings
# settings.configure()
# django.setup()

from mainapp.models import AqiStandard, Station
from mainapp.models import GzepbAqiData, AqicnIAqiData

# import custom get data object
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
from gzepb.gzepb_api import Gzepb
from aqicn.aqicn_api import Aqicn

_AQICN_STATIONS_LIST = ['/guangzhou/',
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

def get_and_store_aqicn_aqi():
    """
    Aqicn aqi data.
    """
    print "%s Start get and store aqicn aqi datas..." % str(
        datetime.datetime.now())
    aqi_datas = Aqicn.get_aqi_data(_AQICN_STATIONS_LIST)

    for aqi_data in aqi_datas:

        if not AqicnIAqiData.objects.filter(
                station_name = aqi_data['station_name'],
                time_point = aqi_data['time_point']).exists():

            print "%s Trying to insert aqicn aqi data:" % str(
                datetime.datetime.now()), aqi_data

            _aqi = aqi_data['aqi']
            _station_name = aqi_data.pop('station_name')
            _aqicn_data = AqicnIAqiData(**aqi_data)

            if Station.objects.filter(station_name=_station_name).exists():
                _aqicn_data.station_name = Station.objects.get(
                    station_name=_station_name)

            if isinstance(_aqi, (int, float)):
                if _aqi > 300:
                    _aqicn_data.quality = AqiStandard.objects.get(
                        usa_quality='危险')
                elif 300 >= _aqi >= 201:
                    _aqicn_data.quality = AqiStandard.objects.get(
                        usa_quality='非常不健康')
                elif 200 >= _aqi >= 151:
                    _aqicn_data.quality = AqiStandard.objects.get(
                        usa_quality='不健康')
                elif 150 >= _aqi >= 101:
                    _aqicn_data.quality = AqiStandard.objects.get(
                        usa_quality='对敏感人群不健康')
                elif 100 >= _aqi >= 51:
                    _aqicn_data.quality = AqiStandard.objects.get(
                        usa_quality='中等')
                elif 50 >= _aqi >= 0:
                    _aqicn_data.quality = AqiStandard.objects.get(
                        usa_quality='好')
                else:
                    _aqicn_data.quality = AqiStandard.objects.get(
                        usa_quality='无效')
            else:
                _aqicn_data.quality = AqiStandard.objects.get(
                    usa_quality='空')

            _aqicn_data.save()

        else:
            print "%s AqicnIAqiData already exists: " % str(
                datetime.datetime.now()), aqi_data

def get_and_store_aqicn_station():
    """
    aqicn station data.
    """
    print "%s Start get and store aqicn station datas..." % str(
        datetime.datetime.now())
    station_datas = Aqicn.get_station_data(_AQICN_STATIONS_LIST)
    for station in station_datas:
        print "%s Trying to insert aqicn stations data:" % str(
            datetime.datetime.now()), station
        try:
            if not Station.objects.filter(
                    station_name = station['station_name'],
                    station_type = station['station_type']).exists():
                station_obj = Station(**station)
                station_obj.save()
            else:
                print "%s Station data already exists: " % str(
                    datetime.datetime.now()), station
        except Exception, e:
            print "%s Error: insert aqicn stations data:" % str(
                datetime.datetime.now()), station, e

def get_and_store_gzepb_aqi():
    """
    Gzepb aqi data.
    """
    print "%s Start get and store gzepb aqi datas..." % str(
        datetime.datetime.now())

    aqi_datas = Gzepb.get_aqi_data()
    for aqi_data in aqi_datas:
        if not GzepbAqiData.objects.filter(
                station_name = aqi_data['station_name'],
                time_point = aqi_data['time_point']).exists():

            print "%s Trying to insert gzepb aqi data:" % str(
                datetime.datetime.now()), aqi_data

            _quality = aqi_data.pop('quality')
            _station_name = aqi_data.pop('station_name')
            _aqicn_data = GzepbAqiData(**aqi_data)

            if Station.objects.filter(station_name=_station_name).exists():
                _aqicn_data.station_name = Station.objects.get(
                    station_name=_station_name)

            _aqicn_data.quality = AqiStandard.objects.get(
                china_quality=_quality)
            _aqicn_data.save()
        else:
            print "%s GzepbAqiData already exists: " % str(
                datetime.datetime.now()), aqi_data

def get_and_store_gzepb_station():
    """
    gzepb station data.
    """
    print "%s Start get and store gzepb station's datas..." % str(
        datetime.datetime.now())
    station_datas = Gzepb.get_station_data()
    for station in station_datas:
        print "%s Trying to insert gzepb stations data:" % str(
            datetime.datetime.now()), station
        try:
            if not Station.objects.filter(
                    station_name = station['station_name'],
                    station_type = station['station_type']).exists():
                station_obj = Station(**station)
                station_obj.save()
            else:
                print "%s Station data already exists: " % str(
                    datetime.datetime.now()), station
        except Exception, e:
            print "%s Error: insert gzepb stations data:" % str(
                datetime.datetime.now()), station, e


if __name__ == '__main__':
    pass
    # get_and_store_aqicn_station()
    # get_and_store_gzepb_station()
    # get_and_store_aqicn_aqi()
    # get_and_store_gzepb_aqi()
