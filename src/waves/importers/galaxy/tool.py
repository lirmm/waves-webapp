from __future__ import unicode_literals

import logging

import bioblend
from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy.objects import *
from bioblend.galaxy.objects.client import ObjToolClient
import waves.const
from waves.exceptions import RunnerConnectionError
from waves.importers.base import AdaptorImporter
from waves.models import Service, ServiceInput, RelatedInput, ServiceInputFormat, ServiceOutput, \
    ServiceOutputFromInputSubmission

logger = logging.getLogger(__name__)


class GalaxyToolImporter(AdaptorImporter):
    """ Allow Service to automatically import submission parameters from Galaxy bioblend API """
    #: List of tools categories which are not meaning a 'WAVES' service tool
    _unwanted_categories = [None, 'Get Data', 'Filter and sort', 'Collection Operations', 'Graph/Display Data',
                            'Send Data', 'Text Manipulation', 'Fetch Alignments', ]

    _type_map = dict(
        text=waves.const.TYPE_TEXT,
        boolean=waves.const.TYPE_BOOLEAN,
        integer=waves.const.TYPE_INTEGER,
        float=waves.const.TYPE_FLOAT,
        data=waves.const.TYPE_FILE,
        select=waves.const.TYPE_LIST,
        conditional=waves.const.TYPE_LIST,
        data_column=waves.const.TYPE_TEXT,
        data_collection=waves.const.TYPE_FILE,
    )

    def connect(self):
        """
        Connect to remote Galaxy Host
        :return:
        """
        gi = GalaxyInstance(url=self._adaptor.complete_url, api_key=self._adaptor.app_key)
        self._tool_client = ObjToolClient(obj_gi=gi)

    def _list_all_remote_services(self):
        """
        List available tools on remote Galaxy server, filtering with ``_unwanted_categories``
        Group items by categories

        :return: A list of tuples corresponding to format used in Django for Choices
        """
        try:
            tool_list = self._tool_client.list()
            group_list = sorted(set(map(lambda x: x.wrapped['panel_section_name'], tool_list)), key=lambda z: z)
            group_list = [x for x in group_list if x not in self._unwanted_categories]
            return [
                (x,
                 sorted([(y.id, y.name + ' ' + y.version) for y in tool_list if
                         y.wrapped['panel_section_name'] == x and y.wrapped['model_class'] == 'Tool'],
                        key=lambda d: d[1])
                 )
                for x in group_list]
        except ConnectionError as e:
            raise RunnerConnectionError(e.message, 'Connection Error:\n')

    def _update_remote_tool_id(self, remote_tool_id):
        param_service = self._service.service_run_params.get(param__name='remote_tool_id')
        param_service._value = str(remote_tool_id)
        param_service.save()
        # raise RuntimeError('Fake')
        logger.debug('runner_params: %s ',
                     self._service.service_run_params.values_list('_value', 'param__name', 'param__default'))

    def _update_service(self, details):
        self._service.short_description = self._get_input_value(details.wrapped, 'description',
                                                                self._service.short_description)
        self._service.name = details.name
        self._service.status = waves.const.SRV_DRAFT
        self._service.version = details.version
        # check whether another service exists with same generated api_name
        existing_service = Service.objects.filter(api_name__startswith=self._service.api_name)
        if existing_service.count() > 0:
            self._service.api_name += '_%i' % existing_service.count()
            logger.debug('Setting api_name to %s', self._service.api_name)

    def _list_remote_inputs(self, tool_id):
        tool_details = self._get_tool_details(tool_id)
        return tool_details.wrapped['inputs']

    def _list_remote_outputs(self, tool_id):
        tool_details = self._get_tool_details(tool_id)
        return tool_details.wrapped['outputs']

    def _list_exit_codes(self, tool_id):
        # TODO see if galaxy tool give this info
        return []

    def _get_tool_details(self, remote_tool_id):
        details = self._tool_client.get(id_=remote_tool_id, io_details=True, link_details=True)
        description = self._get_input_value(details.wrapped, 'description')
        return waves.const.ImportService(name=details.name, short_description=description,
                                         wrapped=details.wrapped, version=details.version)

    @staticmethod
    def _get_input_value(tool_input, field, default=''):
        return tool_input[field] if field in tool_input and tool_input[field] != '' else default

    def _import_service_inputs(self, data):
        service_inputs = []
        for tool_input in data:
            if 'test_param' in tool_input:
                service_inputs.extend(self._import_conditional_set(tool_input))
            elif 'inputs' in tool_input:
                # section is just rendered as included inputs tag
                service_inputs.extend(self._import_section(tool_input))
            elif 'repeat' in tool_input:
                service_input = ServiceInput(name=tool_input['name'],
                                             label=self._get_input_value(tool_input, 'label', tool_input['name']),
                                             service=self._submission,
                                             multiple=True,
                                             default=self._get_input_value(tool_input, 'value', ''))
                service_input = self._import_param(tool_input, service_input)
                if service_input is not None:
                    service_input.save()
                    service_inputs.append(service_input)
            elif 'expand' not in tool_input:
                service_input = ServiceInput(name=tool_input['name'],
                                             label=self._get_input_value(tool_input, 'label', tool_input['name']),
                                             service=self._submission,
                                             default=self._get_input_value(tool_input, 'value', ''))
                service_input = self._import_param(tool_input, service_input)
                if service_input is not None:
                    service_input.save()
                    service_inputs.append(service_input)
        if logger.isEnabledFor(logging.DEBUG):
            for service_input in service_inputs:
                logger.debug('****' + service_input.label + ' - ' + service_input.name + '****')
                logger.debug('__class__ ' + str(service_input.__class__))
                logger.debug('Type ' + str(service_input.type) + '|' + service_input.get_type_display())
                logger.debug('Mandatory ' + str(service_input.mandatory))
                logger.debug('Help ' + str(service_input.description))
                logger.debug('Default ' + str(service_input.default))
                if isinstance(service_input, RelatedInput):
                    logger.debug('Depends on ' + str(service_input.related_to))
                    logger.debug('Value ' + service_input.when_value)
                logger.debug('Format ' + str(service_input.format))
                # raise ValueError('A value error is set !!!')
        return service_inputs

    def _import_param(self, tool_input, service_input):
        try:
            logger.debug('---------------')
            service_input.type = self.map_type(tool_input['type'])
            logger.debug('name ' + tool_input['name'])
            service_input.mandatory = self._get_input_value(tool_input, 'optional', 'True') is False
            logger.debug('mandatory ' + str(service_input.mandatory))
            service_input.description = self._get_input_value(tool_input, 'help')
            logger.debug('description ' + str(service_input.description))
            result = getattr(self, '_import_' + tool_input['type'])
            logger.debug('import func _import_%s ', tool_input['type'])
            result(tool_input, service_input)
            logger.debug('result %s ', tool_input['type'])
            logger.debug("default : %s ", service_input.default)
            service_input.param_type = ServiceInputFormat.param_type_from_value(service_input.default)
            service_input.order = self._order_input
            self._order_input += 1
            if service_input.param_type is None:
                service_input.param_type = waves.const.OPT_TYPE_POSIX
            logger.debug("param_type: %s ", service_input.param_type)
            return service_input
        except KeyError as e:
            logger.warn(u'Un-managed input param type "' + tool_input['type'] + u'" for input "' + tool_input['name'] +
                        u'"\n' + e.message)
            return None
        except Exception as exc:
            logger.warn(u'Unexpected error "%s" for input "%s"', tool_input['type'], tool_input['name'])
            raise exc
        finally:
            logger.debug('---------------')

    def _import_conditional_set(self, tool_input):
        if 'cases' in tool_input:
            conditional_inputs = []
            conditional = ServiceInput(name=tool_input['name'],
                                       label=self._get_input_value(tool_input['test_param'], 'label',
                                                                   tool_input['name']),
                                       type=waves.const.TYPE_LIST,
                                       service=self._submission)
            conditional = self._import_param(tool_input['test_param'], conditional)
            logger.debug('Test param %s', tool_input['test_param'])
            conditional.save()
            conditional_inputs.append(conditional)

            for tool_input in tool_input['cases']:
                when_value = tool_input['value']
                for when_input in tool_input['inputs']:
                    when_service_input = RelatedInput(name=when_input['name'],
                                                      label=self._get_input_value(when_input, 'label',
                                                                                  when_input['name']),
                                                      related_to=conditional,
                                                      mandatory=False,
                                                      when_value=when_value)
                    when_service_input = self._import_param(when_input, when_service_input)
                    when_service_input.mandatory = False
                    when_service_input.when_value = when_value
                    when_service_input.save()
                    # conditional_inputs.append(when_service_input)
            return conditional_inputs

    def _import_text(self, tool_input, service_input):
        # TODO check if format needed
        pass

    def _import_boolean(self, tool_input, service_input):
        truevalue = self._get_input_value(tool_input, 'truevalue')
        falsevalue = self._get_input_value(tool_input, 'falsevalue')
        service_input.format = self._formatter.format_boolean(truevalue, falsevalue)

    def _import_integer(self, tool_input, service_input):
        return self._import_number(tool_input, service_input)

    def _import_float(self, tool_input, service_input):
        return self._import_number(tool_input, service_input)

    def _import_number(self, tool_input, service_input):
        service_input.default = self._get_input_value(tool_input, 'value')
        if 'min' in tool_input:
            _min = self._get_input_value(tool_input, 'min', '')
        if 'max' in tool_input:
            _max = self._get_input_value(tool_input, 'max', '')
        service_input.format = self._formatter.format_interval(_min, _max)

    def _import_data(self, tool_input, service_input):
        service_input.format = self._formatter.format_list(self._get_input_value(tool_input, 'extensions'))
        service_input.multiple = self._get_input_value(tool_input, 'multiple') is True

    def _import_select(self, tool_input, service_input):
        service_input.default = self._get_input_value(tool_input, 'value')
        options = []
        for option in self._get_input_value(tool_input, 'options'):
            if option[1] == '':
                option[1] = 'None'
            options.append('|'.join([option[0], option[1]]))
        service_input.format = self._formatter.format_list(options)

    def _import_service_outputs(self, outputs):
        logger.debug(u'Managing service outputs')
        service_outputs = []
        index = 0
        for tool_output in outputs:
            logger.debug(tool_output.keys())
            service_output = ServiceOutput(name=tool_output['name'], service=self._service,
                                           file_pattern=tool_output['name'])
            service_output.order = index
            service_output.description = self._get_input_value(tool_input=tool_output,
                                                               field='label',
                                                               default=tool_output['name'])
            if service_output.file_pattern.startswith('$'):
                from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
                try:
                    input_related_name = service_output.description[2:-1]
                    service_output.from_input = True
                    related_input = ServiceInput.objects.get(name=input_related_name,
                                                             service=self._submission)
                    submission_related_output = ServiceOutputFromInputSubmission(
                        submission=self._submission,
                        srv_input=related_input
                    )
                    service_output.from_input_submission.add(submission_related_output, bulk=True)
                    service_output.description = "Issued from input '%s'" % input_related_name
                except ObjectDoesNotExist:
                    logger.warn('Did not found related input by name ' + service_output.description)
                except MultipleObjectsReturned:
                    logger.warn('Did not found related input by name ' + service_output.description)
                except Exception as e:
                    logger.warn('Other Exception %s', e)
            service_output.save()
            service_outputs.append(service_output)
            index += 1
        return service_outputs

    def _import_section(self, tool_input):
        return self._import_service_inputs(tool_input['inputs'])
