from django.contrib import admin

from mainapp.models import ChinaStandard, USAStandard
from mainapp.models import Station
from mainapp.models import GzepbAqiData, AqicnIAqiData

# Register your models here.
admin.site.register(AqicnIAqiData)
admin.site.register(GzepbAqiData)
admin.site.register(ChinaStandard)
admin.site.register(USAStandard)
admin.site.register(Station)
