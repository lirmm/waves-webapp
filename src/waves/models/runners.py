"""
Job Runners related models

"""
from __future__ import unicode_literals
from django.db import models
from waves.models.base import DescribeAble, ExportAbleMixin
from django.utils.module_loading import import_string
import waves.const
from waves.utils.encrypt import EncryptedValue

__all__ = ['Runner', 'RunnerParam']


class RunnerManager(models.Manager):
    pass


class Runner(DescribeAble, ExportAbleMixin):
    """
    Represents a generic job adaptor meta information (resolved at runtime via clazz attribute)
    """

    class Meta:
        ordering = ['name']
        db_table = 'waves_runner'
        verbose_name = 'Service runner'

    #: private attribute to set if clazz have been modified before save
    _clazz = None
    objects = RunnerManager()

    name = models.CharField('Runner name', max_length=50, null=False, help_text='Runner displayed name')
    available = models.BooleanField('Availability', default=True, help_text='Available for job runs')
    clazz = models.CharField('Class implementation', max_length=100, null=False,
                             help_text='Associated implementation class')

    def __str__(self):
        return self.name

    @classmethod
    def from_db(cls, db, field_names, values):
        """
        Update _clazz attribute on model object loading from db
        :param db:
        :param field_names:
        :param values:
        :return:
        """
        instance = super(Runner, cls).from_db(db, field_names, values)
        instance._clazz = instance.clazz
        return instance

    def save(self, **kwargs):
        """
        Override save method in order to setup initial related objects 'RunnerParam' issued from implementation class
        :param force_insert:
        :param force_update:
        :param using:
        :param update_fields:
        :return:
        """
        super(Runner, self).save(**kwargs)
        # Disable all related services upon change on adaptor
        if not self.available:
            for service in self.runs.all():
                service.status = waves.const.SRV_DRAFT
                service.save()

    @property
    def adaptor(self):
        """
        Import and create a new instance of Runner related class implementation
        :return: An waves.adaptors.* instance or None if no class specified
        """
        if self.clazz:
            Adaptor = import_string(self.clazz)
            return Adaptor(init_params=self.default_run_params())
        return None

    @property
    def importer(self):
        """
        Shortcut function to retrieve an importer associated with a runner Model object
        :return: a Importer class instance
        """
        if self.adaptor is not None:
            return self.adaptor.importer
        else:
            raise NotImplementedError("Runner doesn't have import functionality")

    def default_run_params(self):
        """
        Return a list of tuples representing current service adaptor init params

        :return: a dictionary (param_name=runner_param_default)
        :rtype: dict
        """
        runner_params = self.runner_params.values_list('name', 'default')
        returned = dict()
        for name, default in runner_params:
            returned[name] = default
        return returned

    @property
    def has_changed_clazz(self):
        """
        Return True if current object has changed clazz before save
        :return: True / False
        """
        return self._clazz != self.clazz

    @property
    def serializer(self):
        from waves.models.serializers.runners import RunnerSerializer
        return RunnerSerializer

    def publishUnPublish(self):
        self.available = not self.available
        self.save()

class RunnerParamManager(models.Manager):
    pass


class RunnerParam(models.Model):
    """
    Parameters used by related class object (see: waves.runners) for self initialization
    """

    class Meta:
        db_table = 'waves_runner_param'
        unique_together = ('name', 'runner')
    objects = RunnerParamManager()

    name = models.CharField('Name',
                            max_length=100,
                            blank=True,
                            null=True,
                            help_text='Runner init param name')
    default = models.TextField('Default',
                               max_length=500,
                               null=True,
                               blank=True,
                               help_text='Runner init param default value')
    runner = models.ForeignKey(Runner,
                               related_name='runner_params',
                               on_delete=models.CASCADE)

    prevent_override = models.BooleanField('Prevent service override', default=True,
                                           help_text="Prevent service to override this value ")

    def __str__(self):
        return self.name

    def clean(self):
        cleaned_data = super(RunnerParam, self).clean()
        if not self.default:
            # TODO check if still needed, as not defined as an class model attribute
            self.prevent_override = False

        return cleaned_data

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(RunnerParam, cls).from_db(db, field_names, values)
        if instance.name.startswith('encrypt_'):
            instance.default = EncryptedValue.decrypt(instance.default)
        return instance
