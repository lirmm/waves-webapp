"""
WAVES Services related models objects
"""
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from mptt.models import MPTTModel, TreeForeignKey
from waves_adaptors.const import JOB_CREATED, JOB_COMPLETED

import waves.settings
from waves.models.adaptors import *
from waves.models.base import *
from waves.models.config import WavesSiteConfig
from waves.models.managers.services import *

__all__ = ['ServiceRunParam', 'ServiceCategory', 'Service']


class ServiceCategory(MPTTModel, Ordered, Described, ApiModel):
    """ Service category """

    class Meta:
        db_table = 'waves_service_category'
        unique_together = ('api_name',)
        ordering = ['name']
        verbose_name_plural = "Categories"
        verbose_name = "Category"

    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by = ['name']

    objects = ServiceCategoryManager()
    name = models.CharField('Category Name', null=False, blank=False, max_length=255, help_text='Category name')
    ref = models.URLField('Reference', null=True, blank=True, help_text='Category online reference')
    parent = TreeForeignKey('self', null=True, blank=True, help_text='Parent category',
                            related_name='children_category', db_index=True)

    def __str__(self):
        return self.name


class ServiceRunParam(AdaptorInitParam):
    """ Defined runner param for Service model objects """

    class Meta:
        proxy = True


class Service(TimeStamped, Described, ApiModel, ExportAbleMixin, DTOMixin, HasRunnerParamsMixin):
    """
    Represents a service on the platform
    """
    SRV_DRAFT = 0
    SRV_TEST = 1
    SRV_RESTRICTED = 2
    SRV_PUBLIC = 3
    SRV_STATUS_LIST = [
        [SRV_DRAFT, 'Draft'],
        [SRV_TEST, 'Test'],
        [SRV_RESTRICTED, 'Restricted'],
        [SRV_PUBLIC, 'Public'],
    ]

    # TODO add version number validation
    # TODO add check for mandatory expected params setup (mandatory with no default, not mandatory with default)
    class Meta:
        ordering = ['name']
        db_table = 'waves_service'
        verbose_name = 'Service'
        unique_together = (('api_name', 'version', 'status'),)

    # manager
    objects = ServiceManager()
    # fields
    name = models.CharField('Service name', max_length=255, help_text='Service displayed name')
    version = models.CharField('Current version', max_length=10, null=True, blank=True, default='1.0',
                               help_text='Service displayed version')
    restricted_client = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='restricted_services', blank=True,
                                               verbose_name='Restricted clients', db_table='waves_service_client',
                                               help_text='By default access is granted to everyone, '
                                                         'you may restrict access here.')
    cmd_parser = models.CharField('Parser class', null=True, blank=True, max_length=255,
                                  help_text='Service job submission command')
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, related_name='category_tools',
                                 help_text='Service category')
    status = models.IntegerField(choices=SRV_STATUS_LIST, default=SRV_DRAFT,
                                 help_text='Service online status')
    api_on = models.BooleanField('Available on API', default=True, help_text='Service is available for api calls')
    web_on = models.BooleanField('Available on WEB', default=True, help_text='Service is available for web front')
    email_on = models.BooleanField('Notify results', default=True,
                                   help_text='This service sends notification email')
    partial = models.BooleanField('Dynamic outputs', default=False,
                                  help_text='Set whether some service outputs are dynamic (not known in advance)')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    remote_service_id = models.CharField('Remote service tool ID', max_length=255, editable=False, null=True)
    edam_topics = models.TextField('Edam topics', null=True, blank=True,
                                   help_text='Comma separated list of Edam ontology topics')
    edam_operations = models.TextField('Edam operations', null=True, blank=True,
                                       help_text='Comma separated list of Edam ontology operations')

    def clean(self):
        cleaned_data = super(Service, self).clean()
        # TODO check changed status with at least one submission available on each submission channel (web/api)
        return cleaned_data

    def __str__(self):
        return "%s v(%s)" % (self.name, self.version)

    def set_run_params_defaults(self):
        super(Service, self).set_run_params_defaults()
        for sub in self.submissions.all():
            sub.set_run_params_defaults()

    @property
    def jobs(self):
        """ Get current Service Jobs """
        from waves.models import Job
        return Job.objects.filter(submission__in=self.submissions.all())

    @property
    def pending_jobs(self):
        """ Get current Service Jobs """
        from waves.models import Job
        return Job.objects.filter(submission__in=self.submissions.all(), status__in=Job.PENDING_STATUS)

    def import_service_params(self):
        """ Try to import service param configuration issued from adaptor

        :return: None
        """
        if not self.runner:
            raise ImportError(u'Unable to import if no adaptor is set')

    @property
    def command(self):
        """ Return command parser for current Service """
        if self.cmd_parser:
            from django.utils.module_loading import import_string
            command_parser = import_string(self.cmd_parser)
            return command_parser(service=self)
        else:
            from waves.commands.command import BaseCommand

            return BaseCommand(service=self)

    def service_submission_inputs(self, submission=None):
        """
        Retrieve all
        :param submission:
        :return: corresponding QuerySet object
        :rtype: QuerySet
        """
        if not submission:
            return self.default_submission.submission_inputs
        return submission.submission_inputs

    @transaction.atomic
    def duplicate(self):
        """ Duplicate  a Service / with inputs / outputs / exit_code / runner params """
        from .serializers.services import ServiceSerializer
        from django.contrib import messages
        serializer = ServiceSerializer()
        data = serializer.to_representation(self)
        srv = self.serializer(data=data)
        if srv.is_valid():
            srv.validated_data['name'] += ' (copy)'
            new_object = srv.save()
        else:
            messages.warning('Object could not be duplicated')
            new_object = self
        return new_object

    @property
    def sample_dir(self):
        """ Return expected sample dir for a Service """
        return os.path.join(waves.settings.WAVES_SAMPLE_DIR, self.api_name)

    @property
    def default_submission(self):
        """ Return Service default submission for web forms """
        try:
            return self.submissions.filter(availability__in=(1, 3)).first()
        except ObjectDoesNotExist:
            return None

    @property
    def default_submission_api(self):
        """ Return Service default submission for api """
        try:
            return self.submissions.filter(availability__gt=2).first()
        except ObjectDoesNotExist:
            return None

    @property
    def submissions_web(self):
        """ Returned submissions available on WEB forms """
        return self.submissions.filter(availability__in=(1, 3))

    @property
    def submissions_api(self):
        """ Returned submissions available on API """
        return self.submissions.filter(availability__gt=2)

    def available_for_user(self, user):
        """ Access rules for submission form according to user
        :param user: Request User
        :return: True or False
        """
        if user.is_anonymous():
            return (self.status == Service.SRV_PUBLIC and
                    WavesSiteConfig.objects.get_current_config().allow_submits is True)
        # RULES to set if user can access submissions
        return (self.status == Service.SRV_PUBLIC and
                WavesSiteConfig.objects.get_current_config().allow_submits is True) or \
               (self.status == Service.SRV_DRAFT and self.created_by == user) or \
               (self.status == Service.SRV_TEST and user.is_staff) or \
               (self.status == Service.SRV_RESTRICTED and (
                   user in self.restricted_client.all() or user.is_staff)) or \
               user.is_superuser

    @property
    def serializer(self):
        from waves.models.serializers.services import ServiceSerializer
        return ServiceSerializer

    @property
    def importer(self):
        """ Short cut method to access runner importer (if any)"""
        return self.runner.importer

    def publishUnPublish(self):
        self.status = Service.SRV_DRAFT if Service.SRV_PUBLIC else Service.SRV_PUBLIC
        self.save()

    @property
    def running_jobs(self):
        return self.jobs.filter(status__in=[JOB_CREATED, JOB_COMPLETED])
