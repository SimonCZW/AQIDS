# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-22 20:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_auto_20170322_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aqicniaqidata',
            name='station_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Station', verbose_name='\u76d1\u6d4b\u70b9'),
        ),
    ]