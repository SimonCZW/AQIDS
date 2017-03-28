from django.shortcuts import render
from django.views.generic import TemplateView
from mainapp.models import GzepbAqiData, AqicnIAqiData

import datetime


class IndexView(TemplateView):
    template_name = "mainapp/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

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
