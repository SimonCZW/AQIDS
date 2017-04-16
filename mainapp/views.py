# -*- coding:utf-8 -*-
import datetime

from django.views.generic import TemplateView
from mainapp.models import GzepbAqiData, AqicnIAqiData


class IndexView(TemplateView):
    template_name = "mainapp/index.html"

    def get_last_24h_data(self, model, display_station, time_point):
        time_list_24h = []
        time_list_24h.append(time_point)
        time_point = datetime.datetime.strptime(time_point, "%Y-%m-%d %H:%M:%S")
        for hour in range(1, 24):
            time_list_24h.append((
                time_point-datetime.timedelta(hours=hour)).strftime(
                    "%Y-%m-%d %H:%M:%S"))
        time_list_24h = time_list_24h[::-1]

        data_24h = []
        for time_point in time_list_24h:
            if model.objects.filter(
                    time_point=time_point,
                    station_name__display_name=display_station).exists():
                data_24h.append(model.objects.get(
                    time_point=time_point,
                    station_name__display_name=display_station))
            else:
                data_24h.append(None)

        return (time_list_24h, data_24h)

    def get_line_option(self, model, display_station, time_point):

        option = {
            'color': ['#79b05f'],
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': [display_station]},
            'xAxis': [{
                'type': 'category',
                'boundaryGap': 'false',
                'axisLine': {
                    'lineStyle': {
                        'color': '#d4d4d4'
                    }
                },
                'data': []
            }],
            'yAxis': [{
                'type': 'value',
                'axisLabel': {
                    'formatter': '{value}'
                },
                'axisLine': {
                    'lineStyle': {
                        'color': '#d4d4d4'
                    }
                }
            }],
            'series': [{
                'name': display_station,
                'type': 'line',
                'data': []
            }],
        }

        (time_list, queryset_list) = self.get_last_24h_data(
            model=model,
            display_station=display_station,
            time_point=time_point)

        for time in time_list:
            option['xAxis'][0]['data'].append(
                datetime.datetime.strptime(time,
                    '%Y-%m-%d %H:00:00').strftime('%d号%H时').decode('utf-8'))

        last_aqi=0
        for data in queryset_list:
            if data is None:
                # option['series'][0]['data'].append(None)
                # Using hour ago data if no data.
                option['series'][0]['data'].append(last_aqi)
            else:
                option['series'][0]['data'].append(data.aqi)
                last_aqi=data.aqi

        return option


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

    def _yield_time_point(self, time_point):
        """a generator for time_point.(range:3 day) """
        time_point = datetime.datetime.strptime(time_point, "%Y-%m-%d %H:00:00")
        for hour in range(0, 72):
            last_time_point = (time_point - datetime.timedelta(
                hours=hour)).strftime("%Y-%m-%d %H:00:00")
            yield last_time_point

    def get_model_lastest_data(self, model, time_point):
        """iter to get the lastest model data until success.(range:3 day)"""
        lastest_data = None
        for lastest_time_point in self._yield_time_point(time_point=time_point):
            if model.objects.filter(time_point=lastest_time_point).exists():
                lastest_data = model.objects.filter(
                    time_point=lastest_time_point)
                break
        if lastest_data is None:
            lastest_time_point = None
        return (lastest_data, lastest_time_point)

    def get_model_lastest_station_data(self, model, display_station, time_point):
        """iter to get the lastest station data until success.(range:3 day)"""
        lastest_average_data = None
        for lastest_time_point in self._yield_time_point(time_point=time_point):
            if model.objects.filter(
                    station_name__display_name=display_station,
                    time_point=lastest_time_point).exists():
                lastest_average_data = model.objects.get(
                    time_point = lastest_time_point,
                    station_name__display_name=display_station)
                break

        #special for gzepb dominentpol transfer
        if display_station == "全市平均" and lastest_average_data is not None:
            lastest_average_data.dominentpol = self.sw_gzepb_dominent(
                lastest_average_data.dominentpol)
            # lastest_average_data.values()[0][
                # 'dominentpol'] = self.sw_gzepb_dominent(
                    # lastest_average_data.values()[0])

        return lastest_average_data

    def get_model_lastest_total(self, model, time_point):
        """old version get average data."""
        if model.objects.filter(station_name__display_name="全市平均",
                                time_point=time_point).exists():
            average_data = models.objects.get(
                time_point=time_point, station_name__display_name="全市平均")

            if average_data.values()[0]['station_name_id'].encode(
                    'utf-8') == "全市平均":
                average_data.values()[0]['dominentpol']=self.sw_gzepb_dominent(
                    average_data.values()[0]['dominentpol'])
                return average_data

        elif model.objects.filter(station_name__display_name="广州均值",
                                  time_point=time_point).exists():
            average_data = model.objects.get(
                time_point=time_point, station_name__display_name="广州均值")
        else:
            average_data = None
        return average_data


    def get_context_data(self, **kwargs):
        """
        for all data use in index.html.
        Usage : {{ var }}
        """
        context = super(IndexView, self).get_context_data(**kwargs)

        hour_now = datetime.datetime.now().strftime("%Y-%m-%d %H:00:00")

        (context['lastest_gzepb_data'],
         context['gzepb_time_point'])= self.get_model_lastest_data(
             model=GzepbAqiData, time_point=hour_now)
        context['gzepb_city_average'] = self.get_model_lastest_station_data(
            model=GzepbAqiData,
            display_station="全市平均",
            time_point=hour_now)
        # context['gzepb_city_average'] = self.get_model_lastest_total(
            # model=GzepbAqiData, time_point=hour_now)

        (context['lastest_aqicn_data'],
         context['aqicn_time_point'])= self.get_model_lastest_data(
             model=AqicnIAqiData, time_point=hour_now)

        context['aqicn_city_average'] = self.get_model_lastest_station_data(
            model=AqicnIAqiData,
            display_station="广州均值",
            time_point=hour_now)
        # context['aqicn_city_average'] = self.get_model_lastest_total(
            # model=AqicnIAqiData, time_point=hour_now)

        context['aqicn_option'] = self.get_line_option(
            model=AqicnIAqiData,
            display_station="广州均值",
            time_point=hour_now)
        return context

class TestIndexView(TemplateView):
    template_name = "mainapp/index.html.bak"

    def get_last_24h_data(self, model, display_station, time):
        time_list_24h = []
        time_list_24h.append(time)
        time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        for hour in range(1,24):
            time_list_24h.append((time-datetime.timedelta(hours=hour)).strftime(
                "%Y-%m-%d %H:%M:%S"))
        time_list_24h = time_list_24h[::-1]

        data_24h = []
        for time_point in time_list_24h:
            if model.objects.filter(
                    time_point=time_point,
                    station_name__display_name=display_station).exists():
                data_24h.append(model.objects.get(
                    time_point=time_point,
                    station_name__display_name=display_station))
            else:
                data_24h.append(None)

        return (time_list_24h, data_24h)

    def get_context_data(self, **kwargs):
        context = super(TestIndexView, self).get_context_data(**kwargs)

        hour_now = datetime.datetime.now().strftime("%Y-%m-%d %H:00:00")
        hour_ago = (datetime.datetime.now()
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

        (time_list, queryset_list) = self.get_last_24h_data(
            model=AqicnIAqiData,
            display_station="广州均值",
            time=hour_now)

        context['aqicn_option'] = {
            'color': ['#79b05f'],
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': ['美国领事馆数据']},
            'xAxis': [{
                'type': 'category',
                'boundaryGap': 'false',
                'axisLine': {
                    'lineStyle': {
                        'color': '#d4d4d4'
                    }
                },
                'data': []
            }],
            'yAxis': [{
                'type': 'value',
                'axisLabel': {
                    'formatter': '{value}'
                },
                'axisLine': {
                    'lineStyle': {
                        'color': '#d4d4d4'
                    }
                }
            }],
            'series': [{
                'name': '美国领事馆数据',
                'type': 'line',
                'data': []
            }],
        }
        for time in time_list:
            context['aqicn_option']['xAxis'][0]['data'].append(
                datetime.datetime.strptime(time,
                    '%Y-%m-%d %H:00:00').strftime('%d号%H时').decode('utf-8'))

        last_aqi=0
        for data in queryset_list:
            if data is None:
                # context['aqicn_option']['series'][0]['data'].append(None)
                # Using hour ago data if no data.
                context['aqicn_option']['series'][0]['data'].append(last_aqi)
            else:
                context['aqicn_option']['series'][0]['data'].append(data.aqi)
                last_aqi=data.aqi


        context['option'] = {
            'color': ['#79b05f', '#e58c65'],
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': ['美国标准', '中国标准']},
            'xAxis': [{
                'type': 'category',
                'boundaryGap': 'false',
                'data': ["06号09时", "06月10时", "06月11时",
                       "06月12时", "06月13时", "06月14时",
                       "06月15时", "06月16时", "06月17时",
                       "06月18时", "06月19时", "06月20时",
                       "06月21时", "06月23时", "07月00时",
                       "07月01时", "07月02时", "07月03时",
                       "07月04时", "07月05时", "07月06时",
                       "07月07时", "07月08时", "07月09时"],
                'axisLine': {
                    'lineStyle': {
                        'color': '#d4d4d4'
                    }
                }
            }],
            'yAxis': [{
                'type': 'value',
                'axisLabel': {
                    'formatter': '{value} '
                },
                'axisLine': {
                    'lineStyle': {
                        'color': '#d4d4d4'
                    }
                }
            }],
            'series': [{
                'name': '美国标准',
                'type': 'line',
                'data': [115, None, 118, 116, 114, 115, 114, 116, 120, 120, 119, 117, 102, 91, 92, 95, 98, 101, 102, 102, 104, 105, 110, 111]
            }, {
                'name': '中国标准',
                'type': 'line',
                'data': [67, 69, 70, 71, 69, 71, 69, 72, 74, 75, 74, 77, 71, 59, 57, 59, 59, 62, 62, 63, 63, 65, 67, 70]
            }]
            }
        return context

class StationView(TemplateView):
    template_name = "mainapp/station.html"

    def get_time_list_24h(self, time_point):
        time_list_24h = []
        time_point = datetime.datetime.strptime(time_point, "%Y-%m-%d %H:%M:%S")
        for hour in range(0, 24):
            time_list_24h.append((
                time_point-datetime.timedelta(hours=hour)).strftime(
                    "%Y-%m-%d %H:%M:%S"))
        time_list_24h = time_list_24h[::-1]
        return time_list_24h

    def get_last_24h_data(self, model, display_station, time_list):
        data_24h = []
        for time_point in time_list:
            if model.objects.filter(
                    time_point=time_point,
                    station_name__display_name=display_station).exists():
                data_24h.append(model.objects.get(
                    time_point=time_point,
                    station_name__display_name=display_station))
            else:
                data_24h.append(None)

        return data_24h

    def get_line_option(self, models, display_station, time_point):

        option = {
            'color': [],
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': []},
            'xAxis': [{
                'type': 'category',
                'boundaryGap': 'false',
                'axisLine': {
                    'lineStyle': {
                        'color': '#d4d4d4'
                    }
                },
                'data': []
            }],
            'yAxis': [{
                'type': 'value',
                'axisLabel': {
                    'formatter': '{value}'
                },
                'axisLine': {
                    'lineStyle': {
                        'color': '#d4d4d4'
                    }
                }
            }],
            'series': [],
        }
        time_list = self.get_time_list_24h(time_point)
        for time in time_list:
            option['xAxis'][0]['data'].append(
                datetime.datetime.strptime(time,
                    '%Y-%m-%d %H:00:00').strftime('%d号%H时').decode('utf-8'))

        queryset_dict={}
        if isinstance(models, (list, tuple)):
            for model in models:
                #pass the model station not exists in it.
                if not model.objects.filter(
                        station_name__display_name=display_station).exists():
                    continue
                queryset_dict[model.__name__] = self.get_last_24h_data(
                    model=model,
                    time_list=time_list,
                    display_station=display_station)
        else:
            raise ValueError("models must be a list or a tuple.")

        # for different color line
        color_list = ['#79b05f', '#e58c65', 'blue']
        option['color']+=color_list[:len(queryset_dict)]

        line_name_mapping = {'AqicnIAqiData': '美国领事馆数据',
                             'GzepbAqiData': '广州空气质量发布中心数据'}
        for line_name, datas in queryset_dict.iteritems():
            option['legend']['data'].append(line_name_mapping[line_name])
            series_data = {'name': line_name_mapping[line_name],
                           'type': 'line', 'data': []}

            last_aqi=0
            for data in datas:
                if data is None:
                    # series_data['data'].append(None)
                    # UserWarning hour ago data if no data.
                    series_data['data'].append(last_aqi)
                else:
                    series_data['data'].append(data.aqi)
                    last_aqi=data.aqi

            option['series'].append(series_data)
        return option

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
            return dominentpol

    def _yield_time_point(self, time_point):
        """a generator for time_point.(range:3 day) """
        time_point = datetime.datetime.strptime(time_point, "%Y-%m-%d %H:00:00")
        for hour in range(0, 72):
            last_time_point = (time_point - datetime.timedelta(
                hours=hour)).strftime("%Y-%m-%d %H:00:00")
            yield last_time_point

    def get_model_lastest_station_data(self, model, display_station, time_point):
        """iter to get the lastest station data until success.(range:3 day)"""
        lastest_station_data = None
        for lastest_time_point in self._yield_time_point(time_point=time_point):
            if model.objects.filter(
                    station_name__display_name=display_station,
                    time_point=lastest_time_point).exists():
                lastest_station_data = model.objects.get(
                    time_point = lastest_time_point,
                    station_name__display_name=display_station)
                break

        #special for gzepb dominentpol transfer
        if lastest_station_data is not None:
            lastest_station_data.dominentpol = self.sw_gzepb_dominent(
                lastest_station_data.dominentpol)

        return lastest_station_data


    def get_context_data(self, **kwargs):
        context = super(StationView, self).get_context_data(**kwargs)
        hour_now = datetime.datetime.now().strftime("%Y-%m-%d %H:00:00")

        context['aqicn_lastest_data'] = self.get_model_lastest_station_data(
            model=AqicnIAqiData,
            time_point=hour_now,
            display_station=self.kwargs['display_name'])
        context['gzepb_lastest_data'] = self.get_model_lastest_station_data(
            model=GzepbAqiData,
            time_point=hour_now,
            display_station=self.kwargs['display_name'])

        # context['aqicn_option'] = self.get_line_option(
            # model=AqicnIAqiData,
            # time_point=hour_now,
            # display_station=self.kwargs['display_name'])
        # context['gzepb_option'] = self.get_line_option(
            # model=GzepbAqiData,
            # time_point=hour_now,
            # display_station=self.kwargs['display_name'])
        context['station_option_24h'] = self.get_line_option(
            models=[AqicnIAqiData, GzepbAqiData],
            time_point=hour_now,
            display_station=self.kwargs['display_name'])

        return context
