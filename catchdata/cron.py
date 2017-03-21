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

from mainapp.models import ChinaStandard, USAStandard, Station
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
    print "%s Start get and store aqicn aqi datas..." % str(
        datetime.datetime.now())
    aqi_datas = Aqicn.get_aqi_data(_AQICN_STATIONS_LIST)
    for aqi_data in aqi_datas:
        pass
        # do_something before store into database:
        # - foreign key

def get_and_store_aqicn_station():
    print "%s Start get and store aqicn station datas..." % str(
        datetime.datetime.now())
    station_datas = Aqicn.get_station_data(_AQICN_STATIONS_LIST)
    for station in station_datas:
        print "%s Trying to insert aqicn stations data:" % str(
            datetime.datetime.now()), station
        try:
            Station.objects.create(**station)
            Station.objects.save()
        except Exception, e:
            print "%s Error: insert aqicn stations data:" % str(
                datetime.datetime.now()), station, e

def get_and_store_gzepb_aqi():
    """
    aqi data.
    """
    print "%s Start get and store gzepb aqi datas..." % str(
        datetime.datetime.now())
    aqi_datas = Gzepb.get_aqi_data()
    for aqi_data in aqi_datas:
        # do_something before store into database:
        # - foreign key
        # - message
        pass

def get_and_store_gzepb_station():
    """
    station data.
    """
    print "%s Start get and store gzepb station's datas..." % str(
        datetime.datetime.now())
    station_datas = Gzepb.get_station_data()
    for station in station_datas:
        print "%s Trying to insert gzepb stations data:" % str(
            datetime.datetime.now()), station
        try:
            Station.objects.create(**station)
            Station.objects.save()
        except Exception, e:
            print "%s Error: insert gzepb stations data:" % str(
                datetime.datetime.now()), station, e

def test_station():
    station_data_example = {'station_name': 'x', 'station_type': '国控点', 'city': 'gz'}
    Station.objects.create(**station_data_example)
    Station.objects.save()
    # print Station.objects.filter(station_type='国控')

def main():
   print ChinaStandard.objects.all()

if __name__ == '__main__':
    pass
    # main()
    # test_station()
    # get_and_store_aqicn_station()
    # get_and_store_gzepb_station()
