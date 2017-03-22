from django.contrib import admin

from mainapp.models import AqiStandard
from mainapp.models import Station
from mainapp.models import GzepbAqiData, AqicnIAqiData

# Register your models here.
admin.site.register(AqicnIAqiData)
admin.site.register(GzepbAqiData)
admin.site.register(AqiStandard)
admin.site.register(Station)
