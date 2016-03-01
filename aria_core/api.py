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

import shutil
import warnings

from aria_core import blueprints
from aria_core import logger
from aria_core import utils
from aria_core import workflows


LOG = logger.get_logger(__name__)


class BlueprintsAPI(object):

    def __init__(self, storage_path):
        self._storage_path = storage_path

    def validate(self, blueprint_path):
        """
        Validates a blueprint using Aria DSL parser API
        :param blueprint_path: path to a blueprint
        :type blueprint_path: str
        :return: None
        """
        return blueprints.validate(blueprint_path)

    def initialize(self, blueprint_id, blueprint_path,
                   inputs=None, install_plugins=False):
        """
        Initialized a blueprint
        :param blueprint_id: Blueprint ID
        :type blueprint_id: str
        :param blueprint_path: Blueprint path
        :type blueprint_path: str
        :param inputs: Blueprint deployment inputs
        :type inputs: dict
        :param install_plugins: if necessary to install blueprint plugins
        :type install_plugins: bool
        :return:
        """
        try:
            blueprints.initialize_blueprint(
                blueprint_path,
                blueprint_id,
                blueprints.init_blueprint_storage(
                    blueprint_id,
                    storage_path=self._storage_path),
                inputs=inputs,
                install_plugins=install_plugins,
                storage_path=self._storage_path,
            )
        except (Exception, ImportError) as e:
            LOG.exception(str(e))
            raise e

    def teardown(self, blueprint_id):
        blueprint_storage = utils.storage_dir(
            blueprint_id, storage_path=self._storage_path)
        shutil.rmtree(blueprint_storage, ignore_errors=True)

    def load_blueprint_storage(self, blueprint_id, storage_path=None):
        return blueprints.load_blueprint_storage_env(
            blueprint_id, storage_path=storage_path)

    def outputs(self, blueprint_id):
        return blueprints.outputs(
            blueprint_id, storage_path=self._storage_path)

    def instances(self, blueprint_id, node_id=None):
        return blueprints.instances(blueprint_id,
                                    node_id=node_id,
                                    storage_path=self._storage_path)

    def create_requirements(self, blueprint_path):
        return blueprints.create_requirements(blueprint_path)


class ExecutionsAPI(object):

    def __init__(self, storage_path):
        self._storage_path = storage_path

    def install(self,
                blueprint_id,
                parameters=None,
                allow_custom_parameters=None,
                task_retries=None,
                task_retry_interval=None,
                storage_path=None):
        environment = blueprints.load_blueprint_storage_env(
            blueprint_id, storage_path=storage_path)
        workflows.install(
            parameters=parameters,
            allow_custom_parameters=allow_custom_parameters,
            task_retries=task_retries,
            task_retry_interval=task_retry_interval,
            environment=environment)

    def uninstall(self,
                  blueprint_id,
                  parameters=None,
                  allow_custom_parameters=None,
                  task_retries=None,
                  task_retry_interval=None,
                  storage_path=None):
        environment = blueprints.load_blueprint_storage_env(
            blueprint_id, storage_path=storage_path)
        workflows.uninstall(
            parameters=parameters,
            allow_custom_parameters=allow_custom_parameters,
            task_retries=task_retries,
            task_retry_interval=task_retry_interval,
            environment=environment)

    def execute_custom(self,
                       blueprint_id,
                       workflow_id,
                       parameters=None,
                       allow_custom_parameters=None,
                       task_retries=None,
                       task_retry_interval=None,
                       storage_path=None):
        environment = blueprints.load_blueprint_storage_env(
            blueprint_id, storage_path=storage_path)
        workflows.generic_execute(
            blueprint_id=blueprint_id,
            workflow_id=workflow_id,
            parameters=parameters,
            allow_custom_parameters=allow_custom_parameters,
            task_retries=task_retries,
            task_retry_interval=task_retry_interval,
            environment=environment)


class AriaCoreAPI(object):

    def __init__(self, storage_path=None):
        """
        Aria CORE API class
        :param storage_path: Aria CORE storage folder
        :return: None
        """
        self._storage_path = storage_path
        self.blueprints = BlueprintsAPI(storage_path)
        self.executions = ExecutionsAPI(storage_path)

    @property
    def storage_path(self):
        return self._storage_path

    @storage_path.getter
    def storage_path(self):
        return self._storage_path

    @storage_path.setter
    def storage_path(self, new):
        warnings.warn("Setting new storage path, "
                      "it may cause problems for "
                      "accessing previous storage.")
        self._storage_path = new


__all__ = [
    'AriaCoreAPI'
]
