#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys

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

def get_and_store_aqicn():
    print "start get and store aqicn..."
    token = 'de552bc7dcefe469e68466f97d31f0c88faef2c1'
    gz_aqicn = Aqicn(token)

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
    gz_aqicn.run(stations_url_list)
    # gz_aqicn.aqi_datas
    for station in gz_aqicn.station_datas:
        print station
        try:
            Station.objects.create(**station)
            Station.objects.save()
        except Exception, e:
            print e

def get_and_store_gzepb():
    pass

def test_station():
    station_data_example = {'station_name': 'ss', 'station_type': 'evaluate_point', 'city': 'gz'}
    Station.objects.create(**station_data_example)
    Station.objects.save()

def main():
   print ChinaStandard.objects.all()

if __name__ == '__main__':
    # pass
    # main()
    # test_station()
    get_and_store_aqicn()
