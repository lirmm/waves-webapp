from __future__ import unicode_literals

from django.contrib import admin, messages
from django.contrib.admin import TabularInline
from django.db.models import Q
import os
import waves.const as const
from waves.forms.admin import JobInputForm, JobOutputForm, JobForm
from waves.models.jobs import *
from waves.compat import WavesModelAdmin


class JobInputInline(TabularInline):
    model = JobInput
    form = JobInputForm
    extra = 0
    suit_classes = 'suit-tab suit-tab-inputs'
    exclude = ('order',)
    readonly_fields = ('name', 'value', 'file_path')
    can_delete = False
    ordering = ('order',)
    fields = ('name', 'value', 'file_path')
    classes = ('grp-collapse grp-closed', 'collapse')

    def has_add_permission(self, request):
        return False


class JobOutputInline(TabularInline):
    model = JobOutput
    form = JobOutputForm
    extra = 0
    suit_classes = 'suit-tab suit-tab-outputs'
    classes = ('grp-collapse grp-closed', 'collapse')
    can_delete = False
    readonly_fields = ('name', 'value', 'file_path')
    ordering = ('order',)
    fields = ('name', 'value', 'file_path')

    # classes = ('grp-collapse grp-closed',)

    def has_add_permission(self, request):
        return False


class JobHistoryInline(TabularInline):
    model = JobHistory
    suit_classes = 'suit-tab suit-tab-history'
    classes = ('grp-collapse grp-closed', 'collapse')
    verbose_name = 'Job History'
    verbose_name_plural = "Job history events"

    readonly_fields = ('status', 'timestamp', 'message')
    fields = ('status', 'timestamp', 'message')
    can_delete = False
    extra = 0

    def has_add_permission(self, request):
        return False


def mark_rerun(modeladmin, request, queryset):
    for job in queryset.all():
        if job.status != const.JOB_CREATED:
            try:
                # Delete old history (except admin messages)
                job.re_run()
                messages.success(request, message="Job [%s] successfully marked for re-run" % job.title)
            except StandardError as e:
                messages.error(request, message="Job [%s] error %s " % (job.title, e))
        else:
            messages.warning(request, 'Job [%s] ignored because its status is already created' % job.title)


def delete_model(modeladmin, request, queryset):
    for obj in queryset.all():
        if obj.client == request.user or obj.service.created_by == request.user or request.user.is_superuser:
            try:
                obj.delete()
                messages.success(request, message="Jobs %s successfully deleted" % obj)
            except StandardError as e:
                messages.error(request, message="Job %s error %s " % (obj, e))
        else:
            messages.warning(request, message="You are not authorized to delete this job %s" % obj)


mark_rerun.short_description = "Re-run jobs"
delete_model.short_description = "Delete selected jobs"


class JobAdmin(WavesModelAdmin):
    model = Job
    form = JobForm
    inlines = [
        JobHistoryInline,
        JobInputInline,
        JobOutputInline,
        # TODO add jobOutputExitCode
        # TODO add JobRunDetails
    ]
    actions = [mark_rerun, delete_model]
    list_filter = ('status', 'submission__service', 'client', 'submission__service__runner')
    list_display = ('get_slug', 'get_colored_status', 'service', 'get_run_on', 'get_client', 'created', 'updated')
    list_per_page = 30
    search_fields = ('client__email', 'submission__service_name', 'submission__service__runner')
    readonly_fields = ('title', 'slug', 'email_to', 'service', 'status', 'created', 'updated', 'get_run_on',
                       'command_line')

    # Suit form params (not used by default)

    suit_form_tabs = (('general', 'General'), ('inputs', 'Inputs'), ('outputs', 'Outputs'), ('history', 'History'))
    # grappelli list filter
    # change_list_template = "admin/change_list_filter_sidebar.html"
    # change_form_template = 'admin/waves/job/' + WavesModelAdmin.admin_template
    fieldsets = [
        ('Main', {'classes': ('collapse', 'suit-tab', 'suit-tab-general',),
                'fields': ['title', 'slug', 'email_to', 'service', 'status', 'created', 'updated', 'get_run_on',
                           'command_line', 'client']
                }
         ),
    ]
    tab_overview = (
        (None, {
            'fields': ['title', 'service', 'status', 'created', 'updated', 'client', 'email_to', 'slug', 'get_run_on',
                       'command_line']
        }),
    )
    tab_history = (JobHistoryInline,)
    tab_inputs = (JobInputInline,)
    tab_outputs = (JobOutputInline,)
    tabs = [
        ('General', tab_overview),
        ('History', tab_history),
        ('Inputs', tab_inputs),
        ('Outputs', tab_outputs),
    ]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False

        return super(JobAdmin, self).change_view(request, object_id, form_url, extra_context)

    def get_slug(self, obj):
        return str(obj.slug)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(JobAdmin, self).get_queryset(request)
        else:
            qs = Job.objects.filter(
                Q(service__created_by=request.user) |
                Q(client=request.user) |
                Q(email_to=request.user.email))
            ordering = self.get_ordering(request)
            if ordering:
                qs = qs.order_by(*ordering)
            return qs

    def get_list_filter(self, request):
        return super(JobAdmin, self).get_list_filter(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or (
            obj is not None and (obj.client == request.user or obj.service.created_by == request.user))

    def get_actions(self, request):
        actions = super(JobAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        has_change = super(JobAdmin, self).has_change_permission(request, obj)
        return has_change or request.user.is_superuser

    def __init__(self, model, admin_site):
        super(JobAdmin, self).__init__(model, admin_site)

    def suit_row_attributes(self, obj, request):
        css_class = {
            const.JOB_COMPLETED: 'success',
            const.JOB_RUNNING: 'warning',
            const.JOB_ERROR: 'error',
            const.JOB_CANCELLED: 'error',
            const.JOB_PREPARED: 'info',
            const.JOB_CREATED: 'info',
        }.get(obj.status)
        if css_class:
            return {'class': css_class}

    def get_form(self, request, obj=None, **kwargs):
        request.current_obj = obj
        form = super(JobAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['client'].widget.can_add_related = False
        return form

    def get_run_on(self, obj):
        return obj.service.runner.name

    def get_client(self, obj):
        return obj.client.email if obj.client else "Anonymous"

    def get_colored_status(self, obj):
        return obj.colored_status()

    def get_row_css(self, obj, index):
        # print 'in get row css'
        return obj.label_class

    def get_readonly_fields(self, request, obj=None):
        read_only_fields = list(super(JobAdmin, self).get_readonly_fields(request, obj))
        return read_only_fields

    get_colored_status.short_description = 'Status'
    get_run_on.short_description = 'Run on'
    get_client.short_description = 'Email'
    get_slug.short_description = 'identifier'
    get_slug.admin_order_field = 'slug'
    get_colored_status.admin_order_field = 'status'
    get_run_on.admin_order_field = 'service__run_on'
    get_client.admin_order_field = 'client'


admin.site.register(Job, JobAdmin)
