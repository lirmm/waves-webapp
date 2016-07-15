# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-15 10:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django_countries.fields
import mptt.fields
import uuid
import waves.models.profiles
import waves.models.services


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authtools', '0003_auto_20160128_0912'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIProfile',
            fields=[
                ('slug', models.UUIDField(blank=True, default=uuid.uuid1, editable=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('picture', models.ImageField(blank=True, help_text="Users's avatar", null=True, upload_to=waves.models.profiles.profile_directory, verbose_name='Profile picture')),
                ('registered_for_api', models.BooleanField(default=False, help_text='Register for REST API use', verbose_name='Registered for api use')),
                ('api_key', models.CharField(blank=True, help_text="User's api access key", max_length=255, null=True, unique=True, verbose_name='Api key')),
                ('institution', models.CharField(help_text="User's laboratory", max_length=255, null=True, verbose_name='Institution')),
                ('country', django_countries.fields.CountryField(blank=True, help_text="User's country", max_length=2, null=True)),
                ('phone', models.CharField(blank=True, help_text="User's phone number", max_length=12, null=True, verbose_name='Phone')),
                ('comment', models.TextField(blank=True, help_text="User's comment", null=True, verbose_name='Comments')),
                ('ip', models.GenericIPAddressField(blank=True, help_text="User's restricted IP", null=True, verbose_name='Restricted IP address')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('slug', models.UUIDField(blank=True, default=uuid.uuid1, editable=False)),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Job title')),
                ('status', models.IntegerField(choices=[[-1, 'Unknown'], [0, 'Created'], [2, 'Queued'], [1, 'Prepared for run'], [3, 'Running'], [6, 'Done'], [5, 'Completed'], [7, 'Cancelled'], [4, 'Suspended'], [9, 'In Error']], default=0, help_text='Job current run status', verbose_name='Job status')),
                ('status_mail', models.IntegerField(default=9999, editable=False)),
                ('email_to', models.EmailField(blank=True, help_text='Notify results to this email', max_length=254, null=True, verbose_name='Email results')),
                ('exit_code', models.IntegerField(default=0, help_text='Job exit code on relative runner', verbose_name='Job system exit code')),
                ('results_available', models.BooleanField(default=False, editable=False, verbose_name='Results are available')),
                ('remote_job_id', models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote Job ID (on runner)')),
                ('client', models.ForeignKey(blank=True, help_text='Associated registered user', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clients_job', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated', '-created'],
                'abstract': False,
                'db_table': 'waves_job',
                'verbose_name': 'Job',
            },
        ),
        migrations.CreateModel(
            name='JobHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='History timestamp', verbose_name='Date time')),
                ('status', models.IntegerField(choices=[[-1, 'Unknown'], [0, 'Created'], [2, 'Queued'], [1, 'Prepared for run'], [3, 'Running'], [6, 'Done'], [5, 'Completed'], [7, 'Cancelled'], [4, 'Suspended'], [9, 'In Error']], help_text='History job status', verbose_name='Job Status')),
                ('message', models.TextField(blank=True, help_text='History message', null=True, verbose_name='Status message')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_history', to='waves.Job')),
            ],
            options={
                'ordering': ['-timestamp'],
                'db_table': 'waves_job_history',
            },
        ),
        migrations.CreateModel(
            name='JobInput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('slug', models.UUIDField(blank=True, default=uuid.uuid1, editable=False)),
                ('param_type', models.IntegerField(choices=[(0, 'Not used in job submission'), (1, 'Valuated param (--param_name=value)'), (2, 'Simple param (-param_name value)'), (3, 'Option param (-param_name)'), (5, 'Option named param (--param_name)'), (4, 'Positional param (no name)')], default=4, help_text='Input type (used in command line)', verbose_name='Parameter Type')),
                ('name', models.CharField(blank=True, help_text='This is the parameter name for the runs', max_length=20)),
                ('type', models.CharField(choices=[('file', 'Input file'), ('select', 'List of values'), ('boolean', 'Boolean'), ('number', 'Integer'), ('float', 'Float'), ('text', 'Text')], help_text='Type of parameter (bool, int, text, file etc.)', max_length=50, null=True)),
                ('value', models.CharField(blank=True, help_text='Input value (filename, boolean value, int value etc.)', max_length=255, null=True, verbose_name='Input content')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_inputs', to='waves.Job')),
            ],
            options={
                'db_table': 'waves_job_input',
            },
        ),
        migrations.CreateModel(
            name='JobOutput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('slug', models.UUIDField(blank=True, default=uuid.uuid1, editable=False)),
                ('name', models.CharField(help_text='This is the parameter name for the runs', max_length=200, verbose_name='Name')),
                ('label', models.CharField(blank=True, help_text='This is the displayed name for output (default is name)', max_length=255, null=True, verbose_name='Label')),
                ('value', models.TextField(blank=True, default='', null=True, verbose_name='Output value')),
                ('type', models.CharField(blank=True, default='.txt', max_length=255, null=True, verbose_name='Output file ext')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_outputs', to='waves.Job')),
            ],
            options={
                'db_table': 'waves_job_output',
            },
        ),
        migrations.CreateModel(
            name='Runner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, help_text='Full description (HTML enabled)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text only)', null=True, verbose_name='Short Description')),
                ('name', models.CharField(help_text='Runner displayed name', max_length=50, verbose_name='Runner name')),
                ('available', models.BooleanField(default=True, help_text='Available for job runs', verbose_name='Availability')),
                ('clazz', models.CharField(help_text='Associated implementation class', max_length=100, verbose_name='Class implementation')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'waves_runner',
                'verbose_name': 'Service runner',
            },
        ),
        migrations.CreateModel(
            name='RunnerParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='Runner init param name', max_length=100, null=True, verbose_name='Name')),
                ('default', models.CharField(blank=True, help_text='Runner init param default value', max_length=50, null=True, verbose_name='Default')),
                ('runner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='runner_params', to='waves.Runner')),
            ],
            options={
                'db_table': 'waves_runner_param',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('description', models.TextField(blank=True, help_text='Full description (HTML enabled)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text only)', null=True, verbose_name='Short Description')),
                ('name', models.CharField(help_text='Service displayed name', max_length=255, verbose_name='Service name')),
                ('api_name', models.CharField(blank=True, help_text='Service API name (for urls)', max_length=50, unique=True, verbose_name='Api name')),
                ('version', models.CharField(blank=True, default='1.0', help_text='Service displayed version', max_length=10, null=True, verbose_name='Current version')),
                ('run_on_version', models.CharField(blank=True, help_text='Remote runner tool version', max_length=15, null=True, verbose_name='Runner tool version')),
                ('clazz', models.CharField(blank=True, help_text='Service job submission command', max_length=255, null=True, verbose_name='Parser class')),
                ('status', models.IntegerField(choices=[[0, 'Draft'], [1, 'Test'], [2, 'Restricted'], [3, 'Public']], default=0, help_text='Service online status')),
                ('api_on', models.BooleanField(default=True, help_text='Service is available for api calls ?', verbose_name='Available on API')),
                ('email_on', models.BooleanField(default=True, help_text='This service sends notification email', verbose_name='Notify results to client')),
                ('partial', models.BooleanField(default=False, help_text='Set whether this service has outputs while still running', verbose_name='Allow retrieval of partial results')),
                ('authorized_clients', models.ManyToManyField(blank=True, db_table='waves_service_client', help_text='Access to specific client', related_name='authorized_services', to='waves.APIProfile')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'waves_service',
                'verbose_name': 'Service',
            },
        ),
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('description', models.TextField(blank=True, help_text='Full description (HTML enabled)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text only)', null=True, verbose_name='Short Description')),
                ('name', models.CharField(help_text='Category displayed name', max_length=255, unique=True, verbose_name='Category Name')),
                ('ref', models.URLField(blank=True, help_text='Category description reference', null=True, verbose_name='Reference')),
                ('api_name', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, help_text='This is parent category', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_category', to='waves.ServiceCategory')),
            ],
            options={
                'db_table': 'waves_service_category',
                'verbose_name': "Service's category",
                'verbose_name_plural': "Services' categories",
            },
            managers=[
                ('_default_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ServiceExitCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exit_code', models.IntegerField(verbose_name='Exit code value')),
                ('message', models.CharField(max_length=255, verbose_name='Exit code message')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_exit_codes', to='waves.Service')),
            ],
            options={
                'db_table': 'waves_service_exitcode',
                'verbose_name': 'Service Exit Code',
            },
        ),
        migrations.CreateModel(
            name='ServiceInput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('order', models.PositiveIntegerField(default=0)),
                ('description', models.TextField(blank=True, help_text='Full description (HTML enabled)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text only)', null=True, verbose_name='Short Description')),
                ('label', models.CharField(help_text='Input displayed label', max_length=100, verbose_name='Label')),
                ('name', models.CharField(help_text="Input runner's job param name", max_length=50, verbose_name='Name')),
                ('default', models.CharField(blank=True, help_text="Input runner's job param default value", max_length=255, null=True, verbose_name='Default')),
                ('type', models.CharField(choices=[('file', 'Input file'), ('select', 'List of values'), ('boolean', 'Boolean'), ('number', 'Integer'), ('float', 'Float'), ('text', 'Text')], default='text', help_text='Input Form generation/control', max_length=15, verbose_name='Control Type')),
                ('param_type', models.IntegerField(choices=[(0, 'Not used in job submission'), (1, 'Valuated param (--param_name=value)'), (2, 'Simple param (-param_name value)'), (3, 'Option param (-param_name)'), (5, 'Option named param (--param_name)'), (4, 'Positional param (no name)')], default=4, help_text='Input type (used in command line)', verbose_name='Parameter Type')),
                ('format', models.CharField(blank=True, help_text='ONE PER LINE<br/>For File: fileExt...<br/>For List: label|value ..."<br/>For Number(optional]: min|max<br/>For Boolean(optional): labelTrue|LabelFalse', max_length=500, null=True, verbose_name='Type format')),
                ('mandatory', models.BooleanField(default=False, help_text='Input needs a value to submit job', verbose_name='Mandatory')),
                ('multiple', models.BooleanField(default=False, help_text='Input may be multiple values', verbose_name='Multiple')),
                ('editable', models.BooleanField(default=True, help_text='Input is displayed for job submission if checked', verbose_name='Submitted by user')),
                ('display', models.CharField(blank=True, choices=[('select', 'Select List'), ('radio', 'Radio buttons'), ('checkbox', 'Check box')], default='select', help_text='Input list display mode (for type list only)', max_length=100, null=True, verbose_name='List display type')),
            ],
            options={
                'ordering': ['order'],
                'db_table': 'waves_service_input',
                'verbose_name': 'Input parameter',
            },
        ),
        migrations.CreateModel(
            name='ServiceInputSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='File name')),
                ('file', models.FileField(blank=True, null=True, upload_to=waves.models.services.service_sample_directory, verbose_name='File path')),
                ('when_value', models.CharField(blank=True, help_text='For dependency, related value', max_length=255, null=True, verbose_name='Depending on input value')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'waves_service_sample',
            },
        ),
        migrations.CreateModel(
            name='ServiceMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('description', models.TextField(blank=True, help_text='Full description (HTML enabled)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text only)', null=True, verbose_name='Short Description')),
                ('type', models.CharField(choices=[('website', 'Dedicated website link'), ('doc', 'Documentation link'), ('download', 'Download link'), ('feat', 'Tool features'), ('misc', 'Miscellaneous'), ('paper', 'Related Paper link'), ('cite', 'Citation'), ('rtfm', 'User Guide'), ('cmd', 'Command line')], max_length=100, verbose_name='Meta type')),
                ('value', models.CharField(max_length=500, verbose_name='Meta value')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metas', to='waves.Service')),
            ],
            options={
                'db_table': 'waves_service_meta',
                'verbose_name': 'Service Meta information',
            },
        ),
        migrations.CreateModel(
            name='ServiceOutput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('order', models.PositiveIntegerField(default=0)),
                ('description', models.TextField(blank=True, help_text='Full description (HTML enabled)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text only)', null=True, verbose_name='Short Description')),
                ('name', models.CharField(help_text='Output displayed name', max_length=200, verbose_name='Name')),
            ],
            options={
                'db_table': 'waves_service_output',
                'verbose_name': 'Service Output',
            },
        ),
        migrations.CreateModel(
            name='ServiceRunnerParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, help_text='Runner init param value for this service', max_length=255, null=True, verbose_name='Param value')),
                ('param', models.ForeignKey(help_text='Initial runner param', on_delete=django.db.models.deletion.CASCADE, related_name='param_srv', to='waves.RunnerParam')),
                ('service', models.ForeignKey(help_text='Runner init param for this service', on_delete=django.db.models.deletion.CASCADE, related_name='service_run_params', to='waves.Service')),
            ],
            options={
                'db_table': 'waves_service_runner_param',
                'verbose_name': "Service's runner init param",
            },
        ),
        migrations.CreateModel(
            name='RelatedInput',
            fields=[
                ('serviceinput_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='waves.ServiceInput')),
                ('when_value', models.CharField(help_text='Input is treated only for this parent value', max_length=255, verbose_name='When condition')),
            ],
            options={
                'db_table': 'waves_service_conditional_when',
                'verbose_name': 'Dependent parameter',
            },
            bases=('waves.serviceinput',),
        ),
        migrations.AddField(
            model_name='serviceoutput',
            name='from_input',
            field=models.ForeignKey(blank=True, help_text='Output is valued from an input', null=True, on_delete=django.db.models.deletion.CASCADE, to='waves.ServiceInput'),
        ),
        migrations.AddField(
            model_name='serviceoutput',
            name='service',
            field=models.ForeignKey(help_text='Output associated service', on_delete=django.db.models.deletion.CASCADE, related_name='service_outputs', to='waves.Service'),
        ),
        migrations.AddField(
            model_name='serviceinputsample',
            name='dependent_input',
            field=models.ForeignKey(blank=True, help_text='Dependent on another input value', null=True, on_delete=django.db.models.deletion.SET_NULL, to='waves.ServiceInput'),
        ),
        migrations.AddField(
            model_name='serviceinputsample',
            name='input',
            field=models.ForeignKey(help_text='Associated input', on_delete=django.db.models.deletion.CASCADE, related_name='input_samples', to='waves.ServiceInput'),
        ),
        migrations.AddField(
            model_name='serviceinputsample',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services_sample', to='waves.Service'),
        ),
        migrations.AddField(
            model_name='serviceinput',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_inputs', to='waves.Service'),
        ),
        migrations.AddField(
            model_name='service',
            name='category',
            field=models.ForeignKey(help_text='Service category', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category_tools', to='waves.ServiceCategory'),
        ),
        migrations.AddField(
            model_name='service',
            name='run_on',
            field=models.ForeignKey(blank=True, help_text='Service job runs adapter', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='runs', to='waves.Runner'),
        ),
        migrations.AddField(
            model_name='service',
            name='runner_params',
            field=models.ManyToManyField(help_text='Runner initial parameter', related_name='service_init_params', through='waves.ServiceRunnerParam', to='waves.RunnerParam'),
        ),
        migrations.AlterUniqueTogether(
            name='runner',
            unique_together=set([('name', 'clazz')]),
        ),
        migrations.AddField(
            model_name='jobinput',
            name='related_service_input',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='waves.ServiceInput'),
        ),
        migrations.AddField(
            model_name='job',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_jobs', to='waves.Service'),
        ),
        migrations.CreateModel(
            name='CitationMeta',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.servicemeta',),
        ),
        migrations.CreateModel(
            name='CommandLineMeta',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.servicemeta',),
        ),
        migrations.CreateModel(
            name='DocumentationMeta',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.servicemeta',),
        ),
        migrations.CreateModel(
            name='DownloadLinkMeta',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.servicemeta',),
        ),
        migrations.CreateModel(
            name='FeatureMeta',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.servicemeta',),
        ),
        migrations.CreateModel(
            name='MiscellaneousMeta',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.servicemeta',),
        ),
        migrations.CreateModel(
            name='RelatedPaperMeta',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.servicemeta',),
        ),
        migrations.CreateModel(
            name='WebSiteMeta',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.servicemeta',),
        ),
        migrations.AlterUniqueTogether(
            name='servicerunnerparam',
            unique_together=set([('service', 'param')]),
        ),
        migrations.AlterUniqueTogether(
            name='serviceoutput',
            unique_together=set([('name', 'service')]),
        ),
        migrations.AlterUniqueTogether(
            name='serviceinputsample',
            unique_together=set([('name', 'input', 'service')]),
        ),
        migrations.AlterUniqueTogether(
            name='serviceinput',
            unique_together=set([('name', 'service', 'type')]),
        ),
        migrations.AlterUniqueTogether(
            name='servicecategory',
            unique_together=set([('name',)]),
        ),
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('api_name', 'category', 'version', 'status')]),
        ),
        migrations.AlterUniqueTogether(
            name='runnerparam',
            unique_together=set([('name', 'runner')]),
        ),
        migrations.AddField(
            model_name='relatedinput',
            name='related_to',
            field=models.ForeignKey(help_text='Input is associated to', on_delete=django.db.models.deletion.CASCADE, related_name='dependent_inputs', to='waves.ServiceInput'),
        ),
    ]
