import sys

import waves.settings


def get_runners_list(raw=False):
    """
    Retrieve enabled adaptors list from waves settings env file
    :return: a list of Tuple 'value'/'label'
    """
    from django.utils.module_loading import import_module
    for mod in waves.settings.WAVES_ADAPTORS_MODS:
        available_impl = import_module(mod)
        impls = [adapt for adapt in available_impl.CURRENT_IMPLEMENTATION()]
        grp_impls = {'': 'Select a implementation class...'}
        raw_impls = []
        for adaptor in impls:
            grp_name = getattr(adaptor, 'group', '')
            if grp_name not in grp_impls:
                grp_impls[grp_name] = []
            grp_impls[grp_name].append((adaptor.clazz, adaptor.name))
            raw_impls.append(adaptor.clazz)
    if not raw:
        final = sorted((grp_key, grp_val) for grp_key, grp_val in grp_impls.items())
        return sorted(final, key=lambda tup: tup[0])
    else:
        return raw_impls
