# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-01 10:51
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models
import waves.models.samples


class Migration(migrations.Migration):

    dependencies = [
        ('waves', '0003_auto_20160831_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceinputsample',
            name='file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location=b'/home/marc/git-sources/waves-webapp/data/sample'), upload_to=waves.models.samples.service_sample_directory, verbose_name='File'),
        ),
        migrations.AlterField(
            model_name='serviceinputsample',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Name'),
        ),
    ]
