from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import TabularInline

from waves.admin.base import TinyMCEAdmin
from waves.forms.admin import RunnerParamForm, RunnerForm
from waves.models import RunnerParam, Runner


class RunnerParamInline(TabularInline):
    """
    Job Runner class instantiation parameters insertion field
    """
    model = RunnerParam
    form = RunnerParamForm
    extra = 0
    fields = ['name', 'default']
    readonly_fields = ('name',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class RunnerAdmin(TinyMCEAdmin):
    model = Runner
    form = RunnerForm
    inlines = (
        RunnerParamInline,
    )

    # fields = ('name', 'description', 'available', 'clazz')
    list_display = ('name', 'clazz', 'available')
    list_filter = ('clazz', 'available')
    fieldsets = [
        ('General', {
            'fields': ['name', 'description', 'available', 'clazz', 'update_init_params']
        }
         ),
    ]

    def save_model(self, request, obj, form, change):
        if 'clazz' in form.changed_data:
            obj.runner_params.all().delete()
            messages.warning(request, 'Be aware that related service configuration has been updated ! ')
        if 'update_init_params' in form.changed_data and obj is not None:
            for name, initial in obj.runner.init_params.items():
                param = RunnerParam.objects.update_or_create(defaults={'default': initial}, name=name, runner=obj)
                # param.default = initial
                # param.save()
            for service in obj.runs.all():
                service.save()
            messages.warning(request, 'Be aware that related service configuration has been updated ! ')

        super(RunnerAdmin, self).save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        return super(RunnerAdmin, self).get_form(request=request, obj=obj, **kwargs)

admin.site.register(Runner, RunnerAdmin)