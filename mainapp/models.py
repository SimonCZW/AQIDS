# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import datetime

# Create your models here.
class AqiStandardBase(models.Model):
    quality = models.CharField('空气质量等级', primary_key=True, max_length=20)
    message = models.CharField('建议信息', max_length=255)

    def __unicode__(self):
        return self.quality

    class Meta:
        abstract = True

class ChinaStandard(AqiStandardBase):
    class Meta:
        db_table = 'chinastandard'
        app_label = 'mainapp'

class USAStandard(AqiStandardBase):
    class Meta:
        db_table = 'usastandard'
        app_label = 'mainapp'

class Station(models.Model):
    STATION_TYPES = (
        ('city_average', '城市均值'),
        ('evaluate_point', '城市评价点'),
        ('trendency_point', '城市趋势点'),
        ('national_point', '国控点'),
        ('roadside_point', '路边站'),
        ('contrast_national_point', '国控对照点'),
        ('us_consulate_point', '美国领事馆点'),
    )
    station_name = models.CharField('监测点名称', primary_key=True,
                                    max_length=20)
    station_type = models.CharField('监测点类型', max_length=25,
                                    choices=STATION_TYPES)
    display_name = models.CharField('监测点显示名称', max_length=30, blank=True)
    latitude = models.FloatField('纬度', blank=True, null=True, default=None)
    longitude = models.FloatField('经度', blank=True, null=True, default=None)
    city = models.CharField('城市', max_length=10)
    district = models.CharField('行政区', max_length=10, blank=True, null=True)
    center = models.BooleanField('是否市中心', max_length=5, default=False)

    def __unicode__(self):
        return "%s - %s" % (self.station_type, self.station_name)

    def save(self, *args, **kwargs):
        """
        Display name is the same as station name if display name isn't set.
        """
        if self.display_name == '':
            self.display_name = self.station_name
        super(Station, self).save(*args, **kwargs)

    class Meta:
        db_table = 'stations'
        unique_together = (('station_name', 'station_type'),)
        app_label = 'mainapp'

class GzepbAqiData(models.Model):
    id = models.AutoField(primary_key=True)
    station_name = models.ForeignKey('Station', on_delete=models.CASCADE,
                                     verbose_name='监测点')#db_column='')
    time_point = models.DateTimeField('发布时间')
    # date = models.DateField('日期', default=datetime.date.today())
    date = models.DateField('日期', default=datetime.date.today)

    aqi = models.FloatField('AQI值', blank=True, null=True)
    dominentpol = models.CharField('主要污染物', max_length=50,
                                   blank=True, null=True)
    quality = models.ForeignKey('ChinaStandard', on_delete=models.DO_NOTHING,
                                verbose_name='空气质量等级')

    so2_1h = models.FloatField('so2 1h浓度', blank=True, null=True)
    so2_24h = models.FloatField('so2 24h滑动平均浓度', blank=True, null=True)
    no2_1h = models.FloatField('no2 1h浓度', blank=True, null=True)
    no2_24h = models.FloatField('no2 24h滑动平均浓度', blank=True, null=True)
    pm10_1h = models.FloatField('pm10 1h浓度', blank=True, null=True)
    pm10_24h = models.FloatField('pm10 24h滑动平均浓度', blank=True, null=True)
    co_1h = models.FloatField('co 1h浓度', blank=True, null=True)
    co_24h = models.FloatField('co 24h滑动平均浓度', blank=True, null=True)
    o3_1h = models.FloatField('o3 1h浓度', blank=True, null=True)
    o3_1h_24h = models.FloatField('o3 最大1h浓度(24h内)', blank=True, null=True)
    o3_8h = models.FloatField('o3 8h滑动平均浓度', blank=True, null=True)
    o3_8h_24h = models.FloatField('o3 最大8h滑动平均浓度(24h内)', blank=True,
                                  null=True)
    pm25_1h = models.FloatField('pm25 1h浓度', blank=True, null=True)
    pm25_24h = models.FloatField('pn24 24h滑动平均浓度', blank=True, null=True)

    so2_aqi = models.FloatField('so2 iaqi值(1h)', blank=True, null=True)
    no2_aqi = models.FloatField('no2 iaqi值(1h)', blank=True, null=True)
    pm10_aqi = models.FloatField('pm10 iaqi值(1h)', blank=True, null=True)
    co_aqi = models.FloatField('co iaqi值(1h)', blank=True, null=True)
    o3_aqi = models.FloatField('o3 iaqi值(1h)', blank=True, null=True)
    o3_aqi_8h = models.FloatField('o3 iaqi值(8h)', blank=True, null=True)
    pm25_aqi = models.FloatField('pm25 iaqi值(1h)', blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (str(self.time_point), self.station_name)

    class Meta:
        db_table = 'gzepbaqidata'
        unique_together = (('station_name', 'time_point'),)
        app_label = 'mainapp'

class AqicnIAqiData(models.Model):
    id = models.AutoField(primary_key=True)
    station_name = models.ForeignKey('Station', models.CASCADE,
                                     verbose_name='监测点')
    time_point = models.DateTimeField('发布时间')
    # date = models.DateField('日期', default=datetime.date.today())
    date = models.DateField('日期', default=datetime.date.today)

    aqi = models.FloatField('AQI值', blank=True, null=True, default=None)
    dominentpol = models.CharField('主要污染物', max_length=50, blank=True,
                                   null=True)
    quality = models.ForeignKey('USAStandard', on_delete=models.DO_NOTHING,
                                verbose_name='空气质量等级')

    pm25_iaqi = models.FloatField('pm25 iaqi值(1h)', blank=True, null=True)
    pm10_iaqi = models.FloatField('pm20 iaqi值(1h)', blank=True, null=True)
    o3_iaqi = models.FloatField('o3 iaqi值(1h)', blank=True, null=True)
    no2_iaqi = models.FloatField('no2 iaqi值(1h)', blank=True, null=True)
    so2_iaqi = models.FloatField('so2 iaqi值(1h)', blank=True, null=True)
    co_iaqi = models.FloatField('co iaqi值(1h)', blank=True, null=True)

    temperature = models.FloatField('温度', blank=True, null=True)
    dew = models.FloatField('露点', blank=True, null=True)
    atmospheric_pressure = models.IntegerField('大气压', blank=True, null=True)
    relative_humidity = models.FloatField('相对湿度', blank=True, null=True)
    wind = models.FloatField('风力', blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (str(self.time_point), self.station_name)

    class Meta:
        db_table = 'aqicniaqidata'
        unique_together = (('station_name', 'time_point'),)
        app_label = 'mainapp'
