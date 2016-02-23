# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import contextlib
import os
import sys
import yaml
import pkg_resources

from jinja2 import environment

from aria_core import constants
from aria_core import exceptions
from aria_core import logger_config
from aria_core.dependencies import futures

STORAGE_DIR_NAME = 'local-storage'


def dump_to_file(collection, file_path):
    with open(file_path, 'a') as f:
        f.write(os.linesep.join(collection))
        f.write(os.linesep)


def is_virtual_env():
    return hasattr(sys, 'real_prefix')


def load_aria_working_dir_settings(suppress_error=False):
    try:
        path = get_context_path()
        with open(path, 'r') as f:
            return yaml.load(f.read())
    except exceptions.AriaError:
        if suppress_error:
            return None
        raise


def raise_uninitialized():
    error = exceptions.AriaError(
        'Not initialized: Cannot find {0} in {1}, '
        'or in any of its parent directories'
        .format(constants.ARIA_WD_SETTINGS_DIRECTORY_NAME,
                get_cwd()))
    error.possible_solutions = [
        "Run 'aria init -p [blueprint-path]' in this directory"
    ]
    raise error


def get_context_path():
    init_path = get_init_path()
    if init_path is None:
        raise_uninitialized()
    context_path = os.path.join(
        init_path,
        constants.ARIA_WD_SETTINGS_FILE_NAME
    )
    if not os.path.exists(context_path):
        raise exceptions.AriaError(
            'File {0} does not exist'
            .format(context_path)
        )
    return context_path


def inputs_to_dict(resource, resource_name):
    if not resource:
        return None
    try:
        # parse resource as string representation of a dictionary
        parsed_dict = plain_string_to_dict(resource)
    except exceptions.AriaError:
        try:
            # if resource is a path - parse as a yaml file
            if os.path.exists(resource):
                with open(resource, 'r') as f:
                    parsed_dict = yaml.load(f.read())
            else:
                # parse resource content as yaml
                parsed_dict = yaml.load(resource)
        except yaml.error.YAMLError as e:
            msg = ("'{0}' is not a valid YAML. {1}"
                   .format(resource_name, str(e)))
            raise exceptions.AriaError(msg)

    if isinstance(parsed_dict, dict):
        return parsed_dict
    else:
        msg = (("Invalid input: {0}. {1} must represent a dictionary. Valid "
                "values can either be a path to a YAML file, a string "
                "formatted as YAML or a string formatted as "
                "key1=value1;key2=value2").format(resource, resource_name))
        raise exceptions.AriaError(msg)


def plain_string_to_dict(input_string):
    input_string = input_string.strip()
    input_dict = {}
    mapped_inputs = input_string.split(';')
    for mapped_input in mapped_inputs:
        mapped_input = mapped_input.strip()
        if not mapped_input:
            continue
        split_mapping = mapped_input.split('=')
        if len(split_mapping) == 2:
            key = split_mapping[0].strip()
            value = split_mapping[1].strip()
            input_dict[key] = value
        else:
            msg = "Invalid input format: {0}, the expected format is: " \
                  "key1=value1;key2=value2".format(input_string)
            raise exceptions.AriaError(msg)

    return input_dict


def is_initialized():
    return get_init_path() is not None


def get_init_path():
    current_lookup_dir = get_cwd()
    while True:

        path = os.path.join(current_lookup_dir,
                            constants.ARIA_WD_SETTINGS_DIRECTORY_NAME)

        if os.path.exists(path):
            return path
        else:
            if os.path.dirname(current_lookup_dir) == current_lookup_dir:
                return None
            current_lookup_dir = os.path.dirname(current_lookup_dir)


def get_configuration_path():
    dot_aria = get_init_path()
    return os.path.join(
        dot_aria,
        'config.yaml'
    )


def dump_configuration_file():
    import aria_cli
    config = pkg_resources.resource_string(
        aria_cli.__name__,
        'resources/config.yaml')

    template = environment.Template(config)
    rendered = template.render(
        log_path=logger_config.DEFAULT_LOG_FILE)
    target_config_path = get_configuration_path()
    with open(os.path.join(target_config_path), 'w') as f:
        f.write(rendered)
        f.write(os.linesep)


def dump_aria_working_dir_settings(cosmo_wd_settings=None, update=False):
    if cosmo_wd_settings is None:
        cosmo_wd_settings = AriaWorkingDirectorySettings()
    if update:
        # locate existing file
        # this will raise an error if the file doesnt exist.
        target_file_path = get_context_path()
    else:

        # create a new file
        path = os.path.join(get_cwd(),
                            constants.ARIA_WD_SETTINGS_DIRECTORY_NAME)
        if not os.path.exists(path):
            os.mkdir(path)
        target_file_path = os.path.join(
            get_cwd(), constants.ARIA_WD_SETTINGS_DIRECTORY_NAME,
            constants.ARIA_WD_SETTINGS_FILE_NAME)

    with open(target_file_path, 'w') as f:
        f.write(yaml.dump(cosmo_wd_settings))


def get_import_resolver():
    if not is_initialized():
        return None

    config = logger_config.AriaConfig()
    # get the resolver configuration from the config file
    local_import_resolver = config.local_import_resolver
    return futures.aria_dsl_utils.create_import_resolver(
        local_import_resolver)


@contextlib.contextmanager
def update_wd_settings():
    cosmo_wd_settings = load_aria_working_dir_settings()
    yield cosmo_wd_settings
    dump_aria_working_dir_settings(cosmo_wd_settings, update=True)


def get_cwd():
    return os.getcwd()


def decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = decode_list(item)
        elif isinstance(item, dict):
            item = decode_dict(item)
        rv.append(item)
    return rv


def decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = decode_list(value)
        elif isinstance(value, dict):
            value = decode_dict(value)
        rv[key] = value
    return rv


class AriaWorkingDirectorySettings(yaml.YAMLObject):
    yaml_tag = u'!WD_Settings'
    yaml_loader = yaml.Loader

    def __init__(self):
        self._provider_context = None

    def get_provider_context(self):
        return self._provider_context

    def set_provider_context(self, provider_context):
        self._provider_context = provider_context


def delete_aria_working_dir_settings():
    target_file_path = os.path.join(
        get_cwd(), constants.ARIA_WD_SETTINGS_DIRECTORY_NAME,
        constants.ARIA_WD_SETTINGS_FILE_NAME)
    if os.path.exists(target_file_path):
        os.remove(target_file_path)


def storage_dir(blueprint_id):
    return os.path.join(os.getcwd(),
                        STORAGE_DIR_NAME,
                        blueprint_id)
