# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-02 15:33
from __future__ import unicode_literals

import ckeditor.fields
from django.conf import settings
import django.contrib.sites.managers
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django_countries.fields
import mptt.fields
import uuid
import waves.models.base
import waves.models.profiles
import waves.models.storage
import waves.models.submissions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('authtools', '0003_auto_20160128_0912'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('slug', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Job title')),
                ('status', models.IntegerField(choices=[(-1, 'Unknown'), (0, 'Created'), (1, 'Prepared for run'), (2, 'Queued'), (3, 'Running'), (4, 'Suspended'), (5, 'Completed'), (6, 'Finished'), (7, 'Cancelled'), (9, 'In Error')], default=0, help_text='Job current run status', verbose_name='Job status')),
                ('status_mail', models.IntegerField(default=9999, editable=False)),
                ('email_to', models.EmailField(blank=True, help_text='Notify results to this email', max_length=254, null=True, verbose_name='Email results')),
                ('exit_code', models.IntegerField(default=0, help_text='Job exit code on relative adaptor', verbose_name='Job system exit code')),
                ('results_available', models.BooleanField(default=False, editable=False, verbose_name='Results are available')),
                ('nb_retry', models.IntegerField(default=0, editable=False, verbose_name='Nb Retry')),
                ('remote_job_id', models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote job ID (on adaptor)')),
                ('remote_history_id', models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote history ID (on adaptor)')),
            ],
            options={
                'ordering': ['-updated', '-created'],
                'abstract': False,
                'db_table': 'waves_job',
                'verbose_name': 'Job',
            },
            bases=(models.Model, waves.models.base.UrlMixin, waves.models.base.DTOAble),
        ),
        migrations.CreateModel(
            name='JobHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='History timestamp', verbose_name='Date time')),
                ('status', models.IntegerField(choices=[(-1, 'Unknown'), (0, 'Created'), (1, 'Prepared for run'), (2, 'Queued'), (3, 'Running'), (4, 'Suspended'), (5, 'Completed'), (6, 'Finished'), (7, 'Cancelled'), (9, 'In Error')], help_text='History job status', verbose_name='Job Status')),
                ('message', models.TextField(blank=True, help_text='History log', null=True, verbose_name='History log')),
                ('is_admin', models.BooleanField(default=False, verbose_name='Admin Message')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_history', to='waves.Job')),
            ],
            options={
                'ordering': ['-timestamp', '-status'],
                'db_table': 'waves_job_history',
            },
        ),
        migrations.CreateModel(
            name='JobInput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('slug', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, unique=True)),
                ('value', models.CharField(blank=True, help_text='Input value (filename, boolean value, int value etc.)', max_length=255, null=True, verbose_name='Input content')),
                ('remote_input_id', models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote input ID (on adaptor)')),
                ('type', models.CharField(choices=[('file', 'Input file'), ('select', 'List of values'), ('boolean', 'Boolean'), ('number', 'Number'), ('text', 'Text')], editable=False, max_length=50, null=True, verbose_name='Param type')),
                ('name', models.CharField(editable=False, max_length=200, null=True, verbose_name='Param name')),
                ('param_type', models.IntegerField(choices=[(0, 'Not used in job submission'), (1, 'Valuated param (--param_name=value)'), (2, 'Simple param (-param_name value)'), (3, 'Option param (-param_name)'), (5, 'Option named param (--param_name)'), (4, 'Positional param (no name)')], default=4, editable=False, verbose_name='Parameter Type')),
                ('label', models.CharField(editable=False, max_length=100, null=True, verbose_name='Label')),
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
                ('slug', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, unique=True)),
                ('value', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Output value')),
                ('optional', models.BooleanField(default=True, verbose_name='MayBe empty')),
                ('remote_output_id', models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote output ID (on adaptor)')),
                ('_name', models.CharField(help_text='Output displayed name', max_length=200, verbose_name='Name')),
                ('type', models.CharField(default='.txt', max_length=5, verbose_name='File extension')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_outputs', to='waves.Job')),
            ],
            options={
                'db_table': 'waves_job_output',
            },
            bases=(models.Model, waves.models.base.UrlMixin),
        ),
        migrations.CreateModel(
            name='JobRunParams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='Param name', max_length=100, null=True, verbose_name='Name')),
                ('value', models.TextField(blank=True, help_text='Default value', max_length=500, null=True, verbose_name='Value')),
                ('prevent_override', models.BooleanField(help_text='Prevent override', verbose_name='Prevent override')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_run_params', to='waves.Job')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RepeatedGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Group name')),
                ('title', models.CharField(max_length=255, verbose_name='Group title')),
                ('max_repeat', models.IntegerField(blank=True, null=True, verbose_name='Max repeat')),
                ('min_repeat', models.IntegerField(default=0, verbose_name='Min repeat')),
                ('default', models.IntegerField(default=0, verbose_name='Default repeat')),
            ],
            options={
                'db_table': 'waves_repeat_group',
            },
            bases=(models.Model, waves.models.base.DTOAble),
        ),
        migrations.CreateModel(
            name='Runner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', ckeditor.fields.RichTextField(blank=True, help_text='Description (HTML)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text)', null=True, verbose_name='Short Description')),
                ('name', models.CharField(help_text='Displayed name', max_length=50, verbose_name='Runner label')),
                ('clazz', models.CharField(max_length=100, verbose_name='Adaptor')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'waves_runner',
                'verbose_name': 'Runner',
            },
            bases=(models.Model, waves.models.base.ExportAbleMixin),
        ),
        migrations.CreateModel(
            name='RunnerParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='Param name', max_length=100, null=True, verbose_name='Name')),
                ('value', models.TextField(blank=True, help_text='Default value', max_length=500, null=True, verbose_name='Value')),
                ('prevent_override', models.BooleanField(help_text='Prevent override', verbose_name='Prevent override')),
                ('runner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='runner_params', to='waves.Runner')),
            ],
            options={
                'db_table': 'waves_runner_run_param',
            },
        ),
        migrations.CreateModel(
            name='SampleDependentParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=200, verbose_name='Set value to ')),
            ],
            options={
                'db_table': 'waves_sample_dependent_input',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('description', ckeditor.fields.RichTextField(blank=True, help_text='Description (HTML)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text)', null=True, verbose_name='Short Description')),
                ('api_name', models.CharField(blank=True, help_text='Api short code, must be unique', max_length=100, null=True)),
                ('name', models.CharField(help_text='Service displayed name', max_length=255, verbose_name='Service name')),
                ('version', models.CharField(blank=True, default='1.0', help_text='Service displayed version', max_length=10, null=True, verbose_name='Current version')),
                ('clazz', models.CharField(blank=True, help_text='Service job submission command', max_length=255, null=True, verbose_name='Parser class')),
                ('status', models.IntegerField(choices=[[0, 'Draft'], [1, 'Test'], [2, 'Restricted'], [3, 'Public']], default=0, help_text='Service online status')),
                ('api_on', models.BooleanField(default=True, help_text='Service is available for api calls', verbose_name='Available on API')),
                ('web_on', models.BooleanField(default=True, help_text='Service is available for web front', verbose_name='Available on WEB')),
                ('email_on', models.BooleanField(default=True, help_text='This service sends notification email', verbose_name='Notify results')),
                ('partial', models.BooleanField(default=False, help_text='Set whether some service outputs are dynamic (not known in advance)', verbose_name='Dynamic outputs')),
                ('remote_service_id', models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote service tool ID')),
                ('edam_topics', models.TextField(blank=True, help_text='Comma separated list of Edam ontology topics', null=True, verbose_name='Edam topics')),
                ('edam_operations', models.TextField(blank=True, help_text='Comma separated list of Edam ontology operations', null=True, verbose_name='Edam operations')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'waves_service',
                'verbose_name': 'Service',
            },
            bases=(models.Model, waves.models.base.ExportAbleMixin, waves.models.base.DTOAble),
        ),
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('description', ckeditor.fields.RichTextField(blank=True, help_text='Description (HTML)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text)', null=True, verbose_name='Short Description')),
                ('api_name', models.CharField(blank=True, help_text='Api short code, must be unique', max_length=100, null=True)),
                ('name', models.CharField(help_text='Category name', max_length=255, verbose_name='Category Name')),
                ('ref', models.URLField(blank=True, help_text='Category online reference', null=True, verbose_name='Reference')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('mptt_level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, help_text='Parent category', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_category', to='waves.ServiceCategory')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'waves_service_category',
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='ServiceMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('description', ckeditor.fields.RichTextField(blank=True, help_text='Description (HTML)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text)', null=True, verbose_name='Short Description')),
                ('type', models.CharField(choices=[('website', 'Online resources'), ('doc', 'Documentation'), ('download', 'Downloads'), ('feat', 'Features'), ('misc', 'Miscellaneous'), ('paper', 'Related Paper'), ('cite', 'Citation'), ('rtfm', 'User Guide'), ('cmd', 'Command line')], max_length=100, verbose_name='Meta type')),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title')),
                ('value', models.CharField(blank=True, max_length=500, null=True, verbose_name='Link')),
                ('is_url', models.BooleanField(default=False, editable=False, verbose_name='Is a url')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metas', to='waves.Service')),
            ],
            options={
                'db_table': 'waves_service_meta',
                'verbose_name': 'Information',
            },
        ),
        migrations.CreateModel(
            name='ServiceRunParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='Param name', max_length=100, null=True, verbose_name='Name')),
                ('value', models.TextField(blank=True, help_text='Default value', max_length=500, null=True, verbose_name='Value')),
                ('prevent_override', models.BooleanField(help_text='Prevent override', verbose_name='Prevent override')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_run_params', to='waves.Service')),
            ],
            options={
                'db_table': 'waves_service_run_param',
                'verbose_name': 'Run configuration',
                'verbose_name_plural': 'Run configuration',
            },
        ),
        migrations.CreateModel(
            name='ServiceSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('order', models.PositiveIntegerField(default=0)),
                ('slug', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, unique=True)),
                ('api_name', models.CharField(blank=True, help_text='Api short code, must be unique', max_length=100, null=True)),
                ('label', models.CharField(max_length=255, null=True, verbose_name='Submission label')),
                ('available_online', models.BooleanField(default=True, verbose_name='Available on Web')),
                ('available_api', models.BooleanField(default=True, verbose_name='Available on API')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='waves.Service')),
            ],
            options={
                'ordering': ('order',),
                'db_table': 'waves_service_submission',
                'verbose_name': 'Submission',
                'verbose_name_plural': 'Submissions',
            },
        ),
        migrations.CreateModel(
            name='SubmissionData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('order', models.PositiveIntegerField(default=0)),
                ('description', ckeditor.fields.RichTextField(blank=True, help_text='Description (HTML)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text)', null=True, verbose_name='Short Description')),
                ('label', models.CharField(help_text='Input displayed label', max_length=100, verbose_name='Label')),
                ('name', models.CharField(help_text="Input runner's job param name", max_length=50, verbose_name='Name')),
                ('default', models.CharField(blank=True, max_length=50, null=True, verbose_name='Default value')),
                ('type', models.CharField(choices=[('file', 'Input file'), ('select', 'List of values'), ('boolean', 'Boolean'), ('number', 'Number'), ('text', 'Text')], default='text', help_text='Input Form generation/control', max_length=15, verbose_name='Control Type')),
                ('cmd_line_type', models.IntegerField(choices=[(0, 'Not used in job submission'), (1, 'Valuated param (--param_name=value)'), (2, 'Simple param (-param_name value)'), (3, 'Option param (-param_name)'), (5, 'Option named param (--param_name)'), (4, 'Positional param (no name)')], default=4, help_text='Input type (used in command line)', verbose_name='Command line type')),
                ('required', models.BooleanField(default=False, verbose_name='Required')),
                ('submitted', models.BooleanField(default=True, verbose_name='Submitted')),
                ('multiple', models.BooleanField(default=False, verbose_name='Multiple')),
                ('true_value', models.CharField(default='True', max_length=50, verbose_name='True value')),
                ('false_value', models.CharField(default='False', max_length=50, verbose_name='False value')),
                ('min_val', models.DecimalField(blank=True, decimal_places=3, default=None, max_digits=50, null=True, verbose_name='Min value')),
                ('max_val', models.DecimalField(blank=True, decimal_places=3, default=None, max_digits=50, null=True, verbose_name='Max value')),
                ('list_display', models.CharField(blank=True, choices=[('select', 'Select List'), ('radio', 'Radio buttons'), ('checkbox', 'Check box')], default='select', help_text='Input list display mode (for type list only)', max_length=100, null=True, verbose_name='List display type')),
                ('list_elements', models.TextField(blank=True, help_text='One Element per line label|value', max_length=500, null=True, verbose_name='List Elements')),
                ('extensions', models.TextField(blank=True, help_text='One extension per line', max_length=500, null=True, verbose_name='Extensions')),
                ('max_size', models.IntegerField(default=0, verbose_name='File Max size')),
                ('when_value', models.CharField(help_text='Input is treated only for this parent value', max_length=255, null=True, verbose_name='When condition')),
                ('edam_formats', models.CharField(blank=True, help_text='comma separated list of supported edam format', max_length=255, null=True, verbose_name='Edam format(s)')),
                ('edam_datas', models.CharField(blank=True, help_text='comma separated list of supported edam data type', max_length=255, null=True, verbose_name='Edam data(s)')),
                ('related_to', models.ForeignKey(help_text='Input is associated to', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dependents_inputs', to='waves.SubmissionData')),
                ('repeat_group', models.ForeignKey(blank=True, help_text='Group and repeat items', null=True, on_delete=django.db.models.deletion.SET_NULL, to='waves.RepeatedGroup')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submission_inputs', to='waves.ServiceSubmission')),
            ],
            bases=(models.Model, waves.models.base.DTOAble),
        ),
        migrations.CreateModel(
            name='SubmissionExitCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exit_code', models.IntegerField(verbose_name='Exit code value')),
                ('message', models.CharField(max_length=255, verbose_name='Exit code message')),
                ('is_error', models.BooleanField(default=False, verbose_name='Is an Error')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exit_codes', to='waves.ServiceSubmission')),
            ],
            options={
                'db_table': 'waves_service_exitcode',
                'verbose_name': 'Exit Code',
            },
        ),
        migrations.CreateModel(
            name='SubmissionOutput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('order', models.PositiveIntegerField(default=0)),
                ('description', ckeditor.fields.RichTextField(blank=True, help_text='Description (HTML)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text)', null=True, verbose_name='Short Description')),
                ('label', models.CharField(blank=True, help_text='Label', max_length=255, null=True, verbose_name='Label')),
                ('name', models.CharField(help_text='Output file name', max_length=200, verbose_name='Name')),
                ('ext', models.CharField(default='.txt', max_length=5, verbose_name='File extension')),
                ('optional', models.BooleanField(default=False, verbose_name='Optional')),
                ('file_pattern', models.CharField(blank=True, default='%s', help_text="Format pattern '%s'", max_length=100, null=True, verbose_name='File name')),
                ('edam_format', models.CharField(blank=True, help_text='Edam format', max_length=255, null=True, verbose_name='Edam format')),
                ('edam_data', models.CharField(blank=True, help_text='Edam data', max_length=255, null=True, verbose_name='Edam data')),
                ('from_input', models.ForeignKey(blank=True, help_text='Valuated with input', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_outputs', to='waves.SubmissionData')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outputs', to='waves.ServiceSubmission')),
            ],
            options={
                'db_table': 'waves_service_output',
                'verbose_name': 'Output',
                'verbose_name_plural': 'Outputs',
            },
        ),
        migrations.CreateModel(
            name='SubmissionRunParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='Param name', max_length=100, null=True, verbose_name='Name')),
                ('value', models.TextField(blank=True, help_text='Default value', max_length=500, null=True, verbose_name='Value')),
                ('prevent_override', models.BooleanField(help_text='Prevent override', verbose_name='Prevent override')),
                ('submission', models.ForeignKey(help_text='Runner init param for this service', on_delete=django.db.models.deletion.CASCADE, related_name='sub_run_params', to='waves.ServiceSubmission')),
            ],
            options={
                'verbose_name': "Submission's adaptor init param",
            },
        ),
        migrations.CreateModel(
            name='SubmissionSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample', models.FileField(blank=True, storage=waves.models.storage.WavesStorage(), upload_to=waves.models.submissions.service_sample_directory, verbose_name='File')),
                ('label', models.CharField(blank=True, max_length=255, verbose_name='Label')),
            ],
        ),
        migrations.CreateModel(
            name='WavesProfile',
            fields=[
                ('slug', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('picture', models.ImageField(blank=True, help_text="Users's avatar", null=True, storage=waves.models.storage.WavesStorage(), upload_to=waves.models.profiles.profile_directory, verbose_name='Profile picture')),
                ('registered_for_api', models.BooleanField(default=False, help_text='Register for REST API use', verbose_name='Registered for api use')),
                ('api_key', models.CharField(blank=True, help_text="User's api access key", max_length=255, null=True, unique=True, verbose_name='Api key')),
                ('institution', models.CharField(help_text="User's laboratory", max_length=255, null=True, verbose_name='Institution')),
                ('country', django_countries.fields.CountryField(blank=True, help_text="User's country", max_length=2, null=True)),
                ('phone', models.CharField(blank=True, help_text="User's phone number", max_length=12, null=True, verbose_name='Phone')),
                ('comment', models.TextField(blank=True, help_text="User's comment", null=True, verbose_name='Comments')),
                ('ip', models.GenericIPAddressField(blank=True, help_text="User's restricted IP", null=True, verbose_name='Restricted IP address')),
                ('banned', models.BooleanField(default=False, verbose_name='Banned (abuse)')),
            ],
        ),
        migrations.CreateModel(
            name='WavesSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(choices=[(b'default', b'Default'), (b'amelia', b'Amelia'), (b'cerulean', b'Cerulean'), (b'cosmo', b'Cosmo'), (b'cyborg', b'Cyborg'), (b'flatly', b'Flatly'), (b'journal', b'Journal'), (b'readable', b'Readable'), (b'simplex', b'Simplex'), (b'slate', b'Slate'), (b'spacelab', b'SpaceLab'), (b'united', b'United'), (b'superhero', b'Superhero'), (b'lumen', b'Lumen')], default='slate', max_length=255, verbose_name='Bootstrap theme')),
                ('site', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sites.Site')),
            ],
            options={
                'verbose_name': 'WAVES configuration',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager('site')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='wavesprofile',
            unique_together=set([('user', 'api_key')]),
        ),
        migrations.AddField(
            model_name='service',
            name='category',
            field=models.ForeignKey(help_text='Service category', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category_tools', to='waves.ServiceCategory'),
        ),
        migrations.AddField(
            model_name='service',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='waves.WavesProfile'),
        ),
        migrations.AddField(
            model_name='service',
            name='restricted_client',
            field=models.ManyToManyField(blank=True, db_table='waves_service_client', help_text='By default access is granted to everyone, you may restrict access here.', related_name='restricted_services', to='waves.WavesProfile', verbose_name='Restricted clients'),
        ),
        migrations.AddField(
            model_name='service',
            name='runner',
            field=models.ForeignKey(help_text='Service job runs adapter', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='runs', to='waves.Runner'),
        ),
        migrations.AddField(
            model_name='sampledependentparam',
            name='submission_sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sp_dep_samples', to='waves.SubmissionSample'),
        ),
        migrations.AddField(
            model_name='repeatedgroup',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submission_groups', to='waves.ServiceSubmission'),
        ),
        migrations.AddField(
            model_name='job',
            name='client',
            field=models.ForeignKey(blank=True, help_text='Associated registered user', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clients_job', to='waves.WavesProfile'),
        ),
        migrations.AddField(
            model_name='job',
            name='submission',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_jobs', to='waves.ServiceSubmission'),
        ),
        migrations.CreateModel(
            name='FileInput',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.submissiondata',),
        ),
        migrations.CreateModel(
            name='JobAdminHistory',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.jobhistory',),
        ),
        migrations.CreateModel(
            name='SubmissionParam',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.submissiondata',),
        ),
        migrations.AddField(
            model_name='submissionsample',
            name='dependent_params',
            field=models.ManyToManyField(blank=True, through='waves.SampleDependentParam', to='waves.SubmissionParam'),
        ),
        migrations.AddField(
            model_name='submissionsample',
            name='param',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='input_sample', to='waves.FileInput'),
        ),
        migrations.AlterUniqueTogether(
            name='submissionrunparam',
            unique_together=set([('submission', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='submissionoutput',
            unique_together=set([('name', 'submission')]),
        ),
        migrations.AlterUniqueTogether(
            name='submissionexitcode',
            unique_together=set([('exit_code', 'submission')]),
        ),
        migrations.AlterUniqueTogether(
            name='submissiondata',
            unique_together=set([('name', 'default', 'type', 'submission')]),
        ),
        migrations.AlterUniqueTogether(
            name='servicesubmission',
            unique_together=set([('service', 'api_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='servicerunparam',
            unique_together=set([('service', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='servicemeta',
            unique_together=set([('type', 'title', 'order', 'service')]),
        ),
        migrations.AlterUniqueTogether(
            name='servicecategory',
            unique_together=set([('api_name',)]),
        ),
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('api_name', 'version', 'status')]),
        ),
        migrations.AddField(
            model_name='sampledependentparam',
            name='dependent_input',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sp_dep_params', to='waves.SubmissionParam'),
        ),
        migrations.AlterUniqueTogether(
            name='runnerparam',
            unique_together=set([('name', 'runner')]),
        ),
        migrations.AlterUniqueTogether(
            name='joboutput',
            unique_together=set([('_name', 'job')]),
        ),
        migrations.AlterUniqueTogether(
            name='jobinput',
            unique_together=set([('name', 'job')]),
        ),
        migrations.AlterUniqueTogether(
            name='jobhistory',
            unique_together=set([('job', 'timestamp', 'status', 'is_admin')]),
        ),
        migrations.CreateModel(
            name='RelatedFileInput',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.fileinput',),
        ),
        migrations.CreateModel(
            name='RelatedParam',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('waves.submissionparam',),
        ),
    ]
