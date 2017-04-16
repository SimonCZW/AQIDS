# -*- coding:utf-8 -*-_
from django.contrib import admin

from mainapp.models import AqiStandard
from mainapp.models import Station
from mainapp.models import GzepbAqiData, AqicnIAqiData
from mainapp.models import GzepbAqiDataUsaStandard

admin.site.site_header = 'AQIDS后台管理系统'
admin.site.site_title = 'AQIDS后台管理'
admin.site.index_title = 'AQIDS'
admin.site.name = 'AQIDS'

# Register your models here.
# admin.site.unregister(Station)
# admin.site.unregister(AqiStandard)
# admin.site.unregister(GzepbAqiData)
# admin.site.unregister(AqicnIAqiData)
# Customizing adminsite
# class AQIDSAdminSite(admin.AdminSite):
    # site_header = 'AQIDS后台管理系统'
    # site_title = 'AQIDS后台管理'
    # index_title = 'AQIDS'
    # def __init__(self, *args, **kw):
        # super(AQIDSAdminSite, self).__init__(*args, **kw)
# myadmin_site = AQIDSAdminSite(name='AQIDS')
# myadmin_site.register(Station)

class StationAdmin(admin.ModelAdmin):
    fields = ('station_name', 'station_type', 'display_name', 'latitude',
              'longitude', 'city', 'district', 'center')
    list_display = ('station_name', 'station_type', 'display_name', 'latitude',
                    'longitude', 'city', 'district', 'center')
    list_display_links = ('station_name',)
    list_filter = ('district', 'station_type', 'center')
    readonly_fields = ('station_name', 'station_type', 'display_name',
                       'latitude', 'longitude', 'city', 'district', 'center')
    search_fields = ['station_name', 'station_type', 'display_name']
    show_full_result_count = True
admin.site.register(Station, StationAdmin)
# myadmin_site.register(Station, StationAdmin)

class AqiStandardAdmin(admin.ModelAdmin):
    fields = ('aqi_range', 'china_quality', 'usa_quality',
              'color', 'message', 'advice')
    list_display = ('aqi_range', 'china_quality', 'usa_quality',
                    'color', 'message', 'advice')
    list_display_links = ('aqi_range',)
    readonly_fields = ('aqi_range', 'china_quality', 'usa_quality')
    search_fields = ['china_quality', 'usa_quality']
    show_full_result_count = True
admin.site.register(AqiStandard, AqiStandardAdmin)
# myadmin_site.register(AqiStandard, AqiStandardAdmin)

class AqicnIAqiDataAdmin(admin.ModelAdmin):
    fieldsets = (
        ('basic', {
            'fields': ('time_point', 'station_name', 'quality',
                       'aqi', 'dominentpol')
        }),
        ('iaqi', {
            'classes': ('collapse',),
            'fields': ('pm25_iaqi', 'pm10_iaqi', 'o3_iaqi', 'no2_iaqi',
                       'so2_iaqi', 'co_iaqi')
        }),
        ('weather', {
            'classes': ('collapse',),
            'fields': ('temperature', 'dew', 'atmospheric_pressure',
                       'relative_humidity', 'wind')
        }),
    )
    list_display = ('time_point', 'station_name', 'quality', 'aqi',
                    'dominentpol', 'temperature')
    list_display_links = ('aqi',)
    list_filter = ('quality', 'dominentpol', 'station_name')
    readonly_fields = ('time_point', 'station_name', 'quality', 'aqi',
                       'dominentpol', 'pm25_iaqi', 'pm10_iaqi', 'o3_iaqi',
                       'no2_iaqi', 'so2_iaqi', 'co_iaqi', 'temperature', 'dew',
                       'atmospheric_pressure', 'relative_humidity', 'wind')
    # raw_id_fields = ('station_name', 'quality')
    # search foreignkey
    search_fields = ['station_name__station_name',
                     'station_name__station_type',
                     'station_name__display_name']
admin.site.register(AqicnIAqiData, AqicnIAqiDataAdmin)
# myadmin_site.register(AqicnIAqiData, AqicnIAqiDataAdmin)

class GzepbAqiDataAdmin(admin.ModelAdmin):
    fieldsets = (
        ('basic', {
            'fields': ('time_point', 'station_name', 'quality',
                       'aqi', 'dominentpol')
        }),
        ('detail concentration', {
            'classes': ('collapse',),
            'fields': ('so2_1h', 'so2_24h', 'no2_1h', 'no2_24h', 'pm10_1h',
                       'pm10_24h', 'co_1h', 'co_24h', 'o3_1h', 'o3_1h_24h',
                       'o3_8h', 'o3_8h_24h', 'pm25_1h', 'pm25_24h')
        }),
        ('iaqi', {
            'classes': ('collapse',),
            'fields': ('pm25_iaqi', 'pm10_iaqi', 'o3_iaqi', 'no2_iaqi',
                       'so2_iaqi', 'co_iaqi', 'o3_iaqi_8h')
        }),
    )
    list_display = ('time_point', 'station_name', 'quality', 'aqi',
                    'dominentpol')
    list_display_links = ('aqi',)
    list_filter = ('quality', 'dominentpol', 'station_name')
    readonly_fields = ('time_point', 'station_name', 'quality', 'aqi',
                       'dominentpol', 'so2_1h', 'so2_24h', 'no2_1h', 'no2_24h',
                       'pm10_1h', 'pm10_24h', 'co_1h', 'co_24h', 'o3_1h',
                       'o3_1h_24h', 'o3_8h', 'o3_8h_24h', 'pm25_1h', 'pm25_24h',
                       'pm25_iaqi', 'pm10_iaqi', 'o3_iaqi', 'no2_iaqi',
                       'so2_iaqi', 'co_iaqi', 'o3_iaqi_8h')
    search_fields = ['station_name__station_name',
                     'station_name__station_type',
                     'station_name__display_name']
admin.site.register(GzepbAqiData, GzepbAqiDataAdmin)
# myadmin_site.register(AqiStandard, GzepbAqiDataAdmin)

class GzepbAqiDataUsaStandardAdmin(admin.ModelAdmin):
    fieldsets = (
        ('basic', {
            'fields': ('time_point', 'station_name', 'quality',
                       'aqi', 'dominentpol', 'origin_data')
        }),
        ('iaqi', {
            'classes': ('collapse',),
            'fields': ('pm25_iaqi', 'pm10_iaqi', 'no2_iaqi',
                       'so2_iaqi', 'co_iaqi', 'o3_iaqi_8h')
        }),
    )
    list_display = ('time_point', 'station_name', 'quality', 'aqi',
                    'dominentpol')
    list_display_links = ('aqi',)
    list_filter = ('quality', 'dominentpol', 'station_name')
    readonly_fields = ('time_point', 'station_name', 'quality', 'aqi',
                       'dominentpol', 'origin_data',
                       'pm25_iaqi', 'pm10_iaqi', 'no2_iaqi',
                       'so2_iaqi', 'co_iaqi', 'o3_iaqi_8h')
    search_fields = ['station_name__station_name',
                     'station_name__station_type',
                     'station_name__display_name']
admin.site.register(GzepbAqiDataUsaStandard, GzepbAqiDataUsaStandardAdmin)
