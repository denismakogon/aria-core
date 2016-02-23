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

import os
import sys

from virtualenvapi import manage
from virtualenvapi import exceptions

from aria_core import constants
from aria_core import exceptions as aria_exceptions
from aria_core import logger
from aria_core import logger_config
from aria_core import utils
from aria_core.dependencies import futures
from aria_core.processor import blueprint_processor

LOG = logger.get_logger('aria_cli.cli.main')


def initialize_blueprint(blueprint_path,
                         blueprint_id,
                         storage,
                         install_plugins=False,
                         inputs=None):

    venv_path = install_blueprint_plugins(
        blueprint_id, blueprint_path,
        install_plugins=install_plugins)
    provider_context = (
        logger_config.AriaConfig().local_provider_context)
    inputs = utils.inputs_to_dict(inputs, 'inputs')
    sys.path.append(venv_path)
    env = futures.aria_local.init_env(
        blueprint_path=blueprint_path,
        name=blueprint_id,
        inputs=inputs,
        storage=storage,
        ignored_modules=constants.IGNORED_LOCAL_WORKFLOW_MODULES,
        provider_context=provider_context,
        resolver=utils.get_import_resolver())
    del sys.path[sys.path.index(venv_path)]
    return env


def install_blueprint_plugins(blueprint_id, blueprint_path,
                              install_plugins=False,
                              default_python_interpreter='python2.7'):
    requirements = blueprint_processor.create_requirements(blueprint_path)
    if install_plugins:
        if requirements:
            venv_path = os.path.join(utils.get_cwd(),
                                     '.venv_{0}'.format(blueprint_id))
            venv = manage.VirtualEnvironment(
                venv_path, python=default_python_interpreter)
            venv.open_or_create()
            for req in requirements:
                if not venv.is_installed(req):
                    try:
                        venv.install(req)
                        LOG.info("Installed dependency: {0}".format(req))
                    except exceptions.PackageInstallationException:
                        msg = 'Unable to install {0} dependency'.format(req)
                        LOG.error(msg)
                        raise aria_exceptions.AriaError(msg)
            LOG.info("Virtualenv {0} was used or created.".format(venv_path))
            return os.path.join(venv_path, 'lib', venv.python, 'site-packages')
        else:
            LOG.debug('There are no plugins to install.')
