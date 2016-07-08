from __future__ import unicode_literals

import logging
import os
from django.conf import settings
from django.db import models, transaction
from django.db import IntegrityError
from mptt.models import MPTTModel, TreeForeignKey

import waves.const
import waves.managers.services as managers
from waves.models.base import TimeStampable, DescribeAble, OrderAble
from waves.models.runners import RunnerParam, Runner
from waves.models.profiles import APIProfile

logger = logging.getLogger(__name__)


def set_api_name(value):
    import inflection
    import re
    temp_name = re.sub(r'\W+', '_', value)
    return inflection.underscore(temp_name)


class ServiceInputFormat(object):
    @staticmethod
    def format_number(number):
        return number

    @staticmethod
    def format_boolean(truevalue, falsevalue):
        return '{}|{}'.format(truevalue, falsevalue)

    @staticmethod
    def format_interval(minimum, maximum):
        return '{}|{}'.format(minimum, maximum)

    @staticmethod
    def format_list(values):
        return (''+os.linesep).join(values)

    @staticmethod
    def param_type_from_value(value):
        import re
        param_type = waves.const.OPT_TYPE_SIMPLE
        if not value or value == '':
            return param_type
        try:
            """
            (OPT_TYPE_NONE, 'Not used in job submission'),
            (OPT_TYPE_VALUATED, 'Valuated param (--param_name=value)'),
            (OPT_TYPE_SIMPLE, 'Simple param (-param_name value)'),
            (OPT_TYPE_OPTION, 'Option param (-param_name)'),
            (OPT_TYPE_NAMED_OPTION, 'Option named param (--param_name)'),
            (OPT_TYPE_POSIX, 'Positional param (no name)')
            """
            if re.match('--\w+=\w+', value):
                param_type = waves.const.OPT_TYPE_VALUATED
            elif re.match('-\w+ \w+', value):
                param_type = waves.const.OPT_TYPE_SIMPLE
            elif re.match('-{1}\w{1}', value):
                param_type = waves.const.OPT_TYPE_OPTION
            elif re.match('--{1}\w+', value):
                param_type = waves.const.OPT_TYPE_NAMED_OPTION
            else:
                param_type = waves.const.OPT_TYPE_POSIX
            logger.debug("matched %i ", param_type)
        except Exception as e:
            logger.warn("Exception in regexp %s %s", value, e.message)
        return param_type

    @staticmethod
    def choice_list(value):
        list_choice = []
        if value:
            try:
                for param in value.splitlines(False):
                    if '|' in param:
                        val = param.split('|')
                        list_choice.append((val[1], val[0]))
                    else:
                        list_choice.append((param, param))
            except ValueError as e:
                logger.warn('Error Parsing list values %s - value:%s - param:%s', e.message, value, param)
        return list_choice


def service_sample_directory(instance, filename):
    return 'sample/{0}/{1}'.format(instance.service.api_name, filename)


class ServiceRunnerParam(models.Model):
    class Meta:
        db_table = 'waves_service_runner_param'
        verbose_name = 'Service\'s runner init param'
        unique_together = ('service', 'param')

    service = models.ForeignKey('Service',
                                null=False,
                                related_name='service_run_params',
                                on_delete=models.CASCADE,
                                help_text='Runner init param for this service')
    param = models.ForeignKey(RunnerParam,
                              null=False,
                              on_delete=models.CASCADE,
                              related_name='param_srv',
                              help_text='Initial runner param')
    value = models.CharField('Param value',
                             max_length=255,
                             null=True,
                             blank=True,
                             help_text='Runner init param value for this service')

    def __str__(self):
        return str(self.param.name) + u'[' + str(self.value) + u']'

    def clean(self):
        super(ServiceRunnerParam, self).clean()

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = self.param.default
        super(ServiceRunnerParam, self).save(*args, **kwargs)


class ServiceCategory(MPTTModel, OrderAble, DescribeAble):
    class Meta:
        db_table = 'waves_service_category'
        verbose_name = 'Service\'s category'
        verbose_name_plural = 'Services\' categories'
        unique_together = ('name',)

    class MPTTMeta:
        order_insertion_by = ['name']

    name = models.CharField('Category Name',
                            null=False,
                            blank=False,
                            max_length=255,
                            unique=True,
                            help_text='Category displayed name')
    ref = models.URLField('Reference',
                          null=True,
                          blank=True,
                          help_text='Category description reference')
    api_name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, help_text='This is parent category',
                            related_name='children_category', db_index=True)

    def save(self, *args, **kwargs):
        if not self.api_name:
            self.api_name = set_api_name(self.name)
        super(ServiceCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ServiceInputSample(models.Model):
    class Meta:
        ordering = ['name']
        db_table = 'waves_service_sample'
        unique_together = ('name', 'input', 'service')

    name = models.CharField('File name', max_length=200, null=False)
    file = models.FileField('File path', upload_to=service_sample_directory, null=True, blank=True)
    input = models.ForeignKey('ServiceInput', on_delete=models.CASCADE, related_name='input_samples',
                              help_text='Associated input')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='services_sample', null=True)
    dependent_input = models.ForeignKey('ServiceInput',
                                        on_delete=models.SET_NULL, null=True, blank=True,
                                        help_text='Dependent on another input value')
    when_value = models.CharField('Depending on input value', max_length=255, null=True, blank=True,
                                  help_text='For dependency, related value')


class Service(TimeStampable, DescribeAble):
    """
    Represents a service on the platform
    """

    class Meta:
        ordering = ['name']
        db_table = 'waves_service'
        verbose_name = 'Service'
        unique_together = ('api_name', 'category', 'version', 'status')

    # manager
    objects = managers.ServiceManager()
    # fields
    name = models.CharField('Service name',
                            max_length=255,
                            help_text='Service displayed name')
    api_name = models.CharField('Api name',
                                max_length=50,
                                unique=True,
                                blank=True,
                                help_text='Service API name (for urls)')
    version = models.CharField('Current version',
                               max_length=10,
                               null=True,
                               blank=True,
                               default='1.0',
                               help_text='Service displayed version')
    run_on_version = models.CharField('Runner tool version',
                                      max_length=15,
                                      null=True,
                                      blank=True,
                                      help_text='Remote runner tool version')
    run_on = models.ForeignKey(Runner,
                               related_name='runs',
                               null=True,
                               blank=True,
                               on_delete=models.SET_NULL,
                               help_text='Service job runs adapter')
    runner_params = models.ManyToManyField(RunnerParam,
                                           through=ServiceRunnerParam,
                                           related_name='service_init_params',
                                           help_text='Runner initial parameter')
    authorized_clients = models.ManyToManyField(APIProfile,
                                                related_name='authorized_services',
                                                blank=True,
                                                db_table='waves_service_client',
                                                help_text='Access to specific client')
    clazz = models.CharField('Parser class',
                             null=True,
                             blank=True,
                             max_length=255,
                             help_text='Service job submission command')
    category = models.ForeignKey(ServiceCategory,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='category_tools',
                                 help_text='Service category')
    status = models.IntegerField(choices=waves.const.SRV_STATUS_LIST,
                                 default=waves.const.SRV_DRAFT,
                                 help_text='Service online status')
    api_on = models.BooleanField('Available on API',
                                 default=True,
                                 help_text='Service is available for api calls ?')

    email_on = models.BooleanField('Notify results to client',
                                   default=True,
                                   help_text='This service sends notification email')

    partial = models.BooleanField('Allow retrieval of partial results',
                                  default=False,
                                  help_text='Set whether this service has outputs while still running')

    def __str__(self):
        return "%s v(%s)" % (self.name, self.version)

    def clean(self):
        # TODO add version number validation
        # TODO add check for mandatory expected params setup (mandatory with no default, not mandatory with default)
        logger.debug('Cleaning api_name')
        if not self.api_name:
            self.set_api_name()
        existing = Service.objects.filter(api_name__startswith=self.api_name).exclude(id=self.pk)
        if existing.count() > 0:
            self.api_name += '_%i' % (existing.count() + 1)
        super(Service, self).clean()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Service, self).save(force_insert, force_update, using, update_fields)
        if self.run_on and self.service_run_params.count() != self.run_on.runner_params.count():
            # initialize runner params with defaults
            self.set_default_params_4_runner(self.run_on)

    def set_api_name(self):
        self.api_name = set_api_name(self.name + ' ' + self.version)

    def set_default_params_4_runner(self, run_on):
        for param in run_on.runner_params.all():
            ServiceRunnerParam.objects.update_or_create(defaults={'value': param.default}, service=self, param=param)

    def run_params(self):
        """
        Return a list of tuples representing current service runner init params
        Returns:
            List of Tuple (param_name, param_service_value, runner_param_default)
        """
        runner_params = self.service_run_params.values_list('param__name', 'value', 'param__default')
        returned = dict()
        for name, value, default in runner_params:
            returned[name] = value if value else default
        return returned

    def import_service_params(self):
        """
        Try to import service param configuration issued from runner
        Returns:
            None
        """
        if not self.run_on:
            raise ImportError(u'Unable to import if no runner is set')

    @property
    def runner(self):
        if self.run_on:
            from django.utils.module_loading import import_string
            job_runner = import_string(self.run_on.clazz)
            return job_runner(init_params=self.run_params())
        return None

    @property
    def command(self):
        if self.clazz:
            from django.utils.module_loading import import_string
            command_parser = import_string(self.clazz)
            return command_parser(service=self)
        else:
            from waves.commands.command import BaseCommand
            return BaseCommand(service=self)

    @property
    def base_inputs(self):
        return self.service_inputs.filter(relatedinput=None)

    def allow_partial(self):
        return self.partial is True

    @transaction.atomic
    def duplicate(self):
        service_inputs = self.service_inputs.filter(relatedinput=None)
        service_outputs = self.service_outputs.all()
        service_metas = self.metas.all()
        service_exit_codes = self.service_exit_codes.all()
        service_runner_params = self.service_run_params.all()
        service_samples = self.services_sample.all()
        nb_copy = Service.objects.filter(api_name__startswith=self.api_name).count()
        old_pk = self.pk
        self.pk = None
        self.name += ' (copy %i)' % nb_copy
        self.api_name += '_%i' % nb_copy
        self.status = waves.const.SRV_DRAFT
        self.save()
        self.service_run_params.all().delete()
        # Duplicate Runner params
        for srv_run_param in service_runner_params.all():
            logger.debug("class %s ", srv_run_param.__class__.__name__)
            srv_run_param.pk = None
            srv_run_param.service = self
            srv_run_param.save()
        # Duplicate Inputs
        for srv_input in service_inputs:
            logger.debug('Duplicate input %s ', srv_input)
            dependents = None
            if srv_input.dependent_inputs.count() > 0:
                logger.debug('Input has dependents !!!! %i', srv_input.dependent_inputs.count())
                dependents = srv_input.dependent_inputs.all()
            srv_input.pk = None
            srv_input.service = self
            srv_input.save()
            if dependents:
                logger.debug('Duplicate dependents parameters ')
                for dep_input in dependents:
                    logger.debug('dep_input %s', dep_input)
                    dep_input.pk = None
                    dep_input.related_to = srv_input
                    dep_input.service = self
                    dep_input.save()
            else:
                logger.debug("No Dependency")
        # Duplicates outputs
        for srv_output in service_outputs:
            logger.debug('Duplicate output %s ', srv_output)
            srv_output.pk = None
            # TODO manage this relationship to set it up with new related input
            srv_output.from_input = None
            srv_output.service = self
            srv_output.save()
        # Duplicate Metas
        for srv_meta in service_metas:
            logger.debug('Duplicate meta %s ', srv_meta)
            srv_meta.pk = None
            srv_output.service = self
            srv_meta.save()
        # Duplicate exit codes
        for srv_exit_code in service_exit_codes:
            logger.debug('Duplicate exitcode %s ', srv_exit_code)
            srv_exit_code.pk = None
            srv_output.service = self
            srv_exit_code.save()
        # Duplicate samples
        import shutil
        import os
        for srv_sample in service_samples:
            logger.debug('Duplicate sample %s', srv_sample.file)
            srv_sample.pk = None
            srv_sample.service = self
            # copy file to destination path
            destination = service_sample_directory(srv_sample, os.path.basename(srv_sample.file.name))

            logger.debug('copy from %s to %s : %s ', srv_sample.file.path,
                         settings.WAVES_SAMPLE_DIR + '/' + self.api_name, destination)
            shutil.copy(srv_sample.file.path, settings.WAVES_SAMPLE_DIR + '/' + self.api_name)
            srv_sample.file = destination
            srv_sample.input = ServiceInput.objects.get(name=srv_sample.input.name, service__pk=old_pk)
            if srv_sample.dependent_input:
                srv_sample.dependent_input = ServiceInput.objects.get(name=srv_sample.dependent_input.name,
                                                                      service__pk=old_pk)
            srv_sample.save()
        return self


class ServiceInput(DescribeAble, TimeStampable, OrderAble):
    class Meta:
        db_table = 'waves_service_input'
        verbose_name = 'Input parameter'
        unique_together = ('name', 'service', 'type')
        ordering = ['order']

    label = models.CharField('Label',
                             max_length=100,
                             blank=False,
                             null=False,
                             help_text='Input displayed label')
    name = models.CharField('Name',
                            max_length=50,
                            blank=False,
                            null=False,
                            help_text='Input runner\'s job param name')
    default = models.CharField('Default',
                               max_length=255,
                               null=True,
                               blank=True,
                               help_text='Input runner\'s job param default value')
    type = models.CharField('Control Type',
                            choices=waves.const.IN_TYPE,
                            null=False,
                            default=waves.const.TYPE_TEXT,
                            max_length=15,
                            help_text='Input Form generation/control')
    param_type = models.IntegerField('Parameter Type',
                                     choices=waves.const.OPT_TYPE,
                                     default=waves.const.OPT_TYPE_POSIX,
                                     help_text='Input type (used in command line)')
    format = models.CharField('Type format',
                              null=True,
                              max_length=500,
                              blank=True,
                              help_text='ONE PER LINE<br/>'
                                        'For File: fileExt...<br/>'
                                        'For List: label|value ..."<br/>'
                                        'For Number(optional]: min|max<br/>'
                                        'For Boolean(optional): labelTrue|LabelFalse')
    service = models.ForeignKey(Service,
                                related_name='service_inputs',
                                on_delete=models.CASCADE)
    mandatory = models.BooleanField('Mandatory',
                                    default=False,
                                    help_text='Input needs a value to submit job')
    multiple = models.BooleanField('Multiple',
                                   default=False,
                                   help_text='Input may be multiple values')
    editable = models.BooleanField('Submitted by user',
                                   default=True,
                                   help_text='Input is displayed for job submission if checked')
    display = models.CharField('List display type',
                               choices=waves.const.LIST_DISPLAY_TYPE,
                               default='select',
                               max_length=100,
                               null=True,
                               blank=True,
                               help_text='Input list display mode (for type list only)')

    def save(self, *args, **kwargs):
        if self.type == waves.const.TYPE_LIST:
            if self.display == waves.const.DISPLAY_RADIO:
                self.multiple = False

        super(ServiceInput, self).save(*args, **kwargs)

    def get_choices(self):
        #if self.type in (waves.const.TYPE_LIST, waves.const.TYPE_FILE):
        return ServiceInputFormat.choice_list(self.format)
        """
        elif self.type == waves.const.TYPE_BOOLEAN:
            return [(1, 'True'), (0, 'False')]
        else:
            return []
        """

    def get_min(self):
        if self.type == waves.const.TYPE_INTEGER or self.type == waves.const.TYPE_FLOAT:
            if self.format:
                return eval(self.format.split('|')[0])
            return None
        else:
            return None

    def get_max(self):
        if self.type == waves.const.TYPE_INTEGER or self.type == waves.const.TYPE_FLOAT:
            if self.format:
                return eval(self.format.split('|')[1])
            return None
        else:
            return None

    def __str__(self):
        return '%s (%s)' % (self.label, self.type)


class RelatedInput(ServiceInput):
    class Meta:
        verbose_name = 'Dependent parameter'
        db_table = 'waves_service_conditional_when'
        # unique_together = ('when_value', 'related_to')

    when_value = models.CharField('When condition',
                                  max_length=255,
                                  null=False,
                                  blank=False,
                                  help_text='Input is treated only for this parent value')
    related_to = models.ForeignKey(ServiceInput,
                                   related_name="dependent_inputs",
                                   on_delete=models.CASCADE,
                                   help_text='Input is associated to')

    def get_value_for_choice(self, value):
        choices = self.related_to.get_choices()
        for (code, choice) in choices:
            if code == value:
                return choice
        return None


class ServiceExitCode(models.Model):
    class Meta:
        db_table = 'waves_service_exitcode'
        verbose_name = 'Service Exit Code'

    exit_code = models.IntegerField('Exit code value')
    message = models.CharField('Exit code message', max_length=255)
    service = models.ForeignKey(Service, related_name='service_exit_codes',
                                on_delete=models.CASCADE)


class ServiceOutput(TimeStampable, OrderAble, DescribeAble):
    """
    Represents usual service parameters output values (share same attributes with ServiceParameters)
    """

    class Meta:
        db_table = 'waves_service_output'
        verbose_name = 'Service Output'
        unique_together = ('name', 'service')

    name = models.CharField('Name',
                            max_length=200,
                            null=False,
                            blank=False,
                            help_text='Output displayed name')
    service = models.ForeignKey(Service,
                                related_name='service_outputs',
                                on_delete=models.CASCADE,
                                help_text='Output associated service')
    from_input = models.ForeignKey(ServiceInput,
                                   null=True,
                                   blank=True,
                                   help_text='Output is valued from an input')

    def __str__(self):
        if self.from_input:
            return 'from input "%s"' % self.from_input.label
        return '%s (%s)' % (self.name, self.description)


class ServiceMeta(OrderAble, DescribeAble):
    """
    Represents all meta information associated with a ATGC service service.
    Ex : website, documentation, download, related paper etc...
    """

    class Meta:
        db_table = 'waves_service_meta'
        verbose_name = 'Service Meta information'

    type = models.CharField('Meta type', max_length=100, choices=waves.const.SERVICE_META)
    value = models.CharField('Meta value', max_length=500, blank=False, null=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='metas')


class WebSiteMeta(ServiceMeta):
    objects = managers.WebSiteMetaMngr()

    class Meta:
        proxy = True


class DocumentationMeta(ServiceMeta):
    objects = managers.DocumentationMetaMngr()

    class Meta:
        proxy = True


class DownloadLinkMeta(ServiceMeta):
    objects = managers.DownloadLinkMetaMngr()

    class Meta:
        proxy = True


class FeatureMeta(ServiceMeta):
    objects = managers.FeatureMetaMngr()

    class Meta:
        proxy = True


class MiscellaneousMeta(ServiceMeta):
    objects = managers.MiscellaneousMetaMngr()

    class Meta:
        proxy = True


class RelatedPaperMeta(ServiceMeta):
    objects = managers.RelatedPaperMetaMngr()

    class Meta:
        proxy = True


class CitationMeta(ServiceMeta):
    objects = managers.CitationMetaMngr()

    class Meta:
        proxy = True


class CommandLineMeta(ServiceMeta):
    objects = managers.CommandLineMetaMngr()

    class Meta:
        proxy = True