# -*- coding:utf-8 -*-
#from django.shortcuts import render
from django.views.generic import TemplateView
from mainapp.models import GzepbAqiData, AqicnIAqiData

import datetime


class IndexView(TemplateView):
    template_name = "mainapp/index.html"

    def sw_gzepb_dominent(self, dominentpol):
        """
        switching gzepb dominentpol
        """
        import re
        if re.match(u'^二氧化氮.*', dominentpol):
            return 'NO2'
        elif re.match(u'^颗粒物\(PM10\).*', dominentpol):
            return 'PM10'
        elif re.match(u'^臭氧1小时.*', dominentpol):
            return 'O3'
        elif re.match(u'^二氧化硫.*', dominentpol):
            return 'SO2'
        elif re.match(u'^一氧化碳.*', dominentpol):
            return 'CO'
        elif re.match(u'^颗粒物\(PM2.5\).*', dominentpol):
            return 'PM2.5'
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        hour_now = datetime.datetime.now().strftime("%Y-%m-%d %H:00:00")
        hour_ago = (datetime.datetime.now()
                    - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:00:00")
        if GzepbAqiData.objects.filter(time_point=hour_now).exists():
            context['lastest_gzepb_data'] = GzepbAqiData.objects.filter(
                time_point=hour_now).exclude(
                    station_name__display_name="全市平均")
            context['gzepb_time_point'] = hour_now
            context['gzepb_city_average'] = GzepbAqiData.objects.get(
                time_point=hour_now, station_name__display_name="全市平均")
            # switch dominentpol
            context['gzepb_city_average'].dominentpol = self.sw_gzepb_dominent(
                context['gzepb_city_average'].dominentpol)

        elif GzepbAqiData.objects.filter(time_point=hour_ago).exists():
            context['lastest_gzepb_data'] = GzepbAqiData.objects.filter(
                time_point=hour_ago).exclude(
                    station_name__display_name="全市平均")
            context['gzepb_time_point'] = hour_ago
            context['gzepb_city_average'] = GzepbAqiData.objects.get(
                time_point=hour_ago, station_name__display_name="全市平均")
            # switch dominentpol
            context['gzepb_city_average'].dominentpol = self.sw_gzepb_dominent(
                context['gzepb_city_average'].dominentpol)

        if AqicnIAqiData.objects.filter(time_point=hour_now).exists():
            context['lastest_aqicn_data'] = AqicnIAqiData.objects.filter(
                time_point=hour_now).exclude(
                    station_name__display_name="广州均值")
            context['aqicn_time_point'] = hour_now
            context['aqicn_city_average'] = AqicnIAqiData.objects.get(
                time_point=hour_now, station_name__display_name="广州均值")
        elif AqicnIAqiData.objects.filter(time_point=hour_ago).exists():
            context['lastest_aqicn_data'] = AqicnIAqiData.objects.filter(
                time_point=hour_ago).exclude(
                    station_name__display_name="广州均值")
            context['aqicn_time_point'] = hour_ago
            context['aqicn_city_average'] = AqicnIAqiData.objects.get(
                time_point=hour_ago, station_name__display_name="广州均值")

        return context

class TestIndexView(TemplateView):
    template_name = "mainapp/index.html.bak"

    def get_context_data(self, **kwargs):
        context = super(TestIndexView, self).get_context_data(**kwargs)

        hour_ago = (datetime.datetime.now()
                    - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:00:00")
        hour_now = (datetime.datetime.now()
                    - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:00:00")
        if GzepbAqiData.objects.filter(time_point=hour_now).exists():
            context['lastest_gzepb_data'] = GzepbAqiData.objects.filter(
                time_point=hour_now)
        elif GzepbAqiData.objects.filter(time_point=hour_ago).exists():
            context['lastest_gzepb_data'] = GzepbAqiData.objects.filter(
                time_point=hour_ago)

        if AqicnIAqiData.objects.filter(time_point=hour_now).exists():
            context['lastest_aqicn_data'] = AqicnIAqiData.objects.filter(
                time_point=hour_now)
        elif AqicnIAqiData.objects.filter(time_point=hour_ago).exists():
            context['lastest_aqicn_data'] = AqicnIAqiData.objects.filter(
                time_point=hour_ago)

        return context
