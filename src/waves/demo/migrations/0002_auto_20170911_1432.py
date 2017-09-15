# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-11 12:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wcore', '0004_auto_20170911_1138'),
        ('demo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='demowavesservice',
            name='binary_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wcore.ServiceBinaryFile'),
        ),
        migrations.AlterField(
            model_name='demowavesservice',
            name='api_on',
            field=models.BooleanField(default=True, help_text='Service is available for wapi:api_v2 calls', verbose_name='Available on API'),
        ),
    ]
