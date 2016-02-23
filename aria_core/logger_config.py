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


"""
Logging configuration (formatters, handlers..)

Note:
-----

This file doe's not include the actual loggers.
The loggers are configured in the config.yaml file
in order to expose them to cli users.

"""
import os
import yaml
import tempfile
import getpass

from aria_core import constants
from aria_core.dependencies import futures


DEFAULT_LOG_FILE = os.path.expanduser(
    '{0}/aria-{1}/aria-cli.log'
    .format(tempfile.gettempdir(),
            getpass.getuser()))


def get_init_path():
    current_lookup_dir = os.getcwd()
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


class AriaConfig(object):
    class Logging(object):
        def __init__(self, logging):
            self._logging = logging or {}

        @property
        def filename(self):
            return self._logging.get('filename')

        @property
        def loggers(self):
            return self._logging.get('loggers', {})

    def __init__(self):
        with open(get_configuration_path()) as f:
            self._config = yaml.safe_load(f.read())

    @property
    def logging(self):
        return self.Logging(self._config.get('logging', {}))

    @property
    def local_provider_context(self):
        return self._config.get('local_provider_context', {})

    @property
    def local_import_resolver(self):
        return self._config.get(
            futures.aria_dsl_constants.IMPORT_RESOLVER_KEY, {})


LOGGER = {
    "version": 1,
    "formatters": {
        "file": {
            "format": "%(asctime)s [%(levelname)s] %(message)s"
        },
        "console": {
            "format": "%(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "file",
            "maxBytes": "5000000",
            "backupCount": "20"
        },
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "console"
        }
    }
}
