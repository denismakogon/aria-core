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

    def __init__(self, storage_path=None):
        self._storage_path = storage_path

    def validate(self, blueprint_path):
        """
        Validate blueprint in order to be a valid TOSCA template
        Parameters
        ----------
        blueprint_path: str

        Returns
        -------
        blueprint_plan: dict

        """
        return blueprints.validate(blueprint_path)

    def initialize(self, blueprint_id, blueprint_path,
                   inputs=None, install_plugins=False):
        """
        Initializes blueprint storage and install its plugins if needed
        Parameters
        ----------
        blueprint_id: str
        blueprint_path: str
        inputs: str
        install_plugins: bool

        Returns
        -------
        blueprint_storage: FileStorage

        """
        try:
            blueprint_storage = blueprints.init_blueprint_storage(
                blueprint_id, storage_path=self._storage_path)
            return blueprints.initialize_blueprint(
                blueprint_path,
                blueprint_id,
                blueprint_storage,
                inputs=inputs,
                install_plugins=install_plugins,
                storage_path=self._storage_path,
            )
        except BaseException as e:
            LOG.exception(str(e))
            raise e

    def teardown(self, blueprint_id):
        """
        Destroys blueprint storage once it is not needed
        Parameters
        ----------
        blueprint_id: str

        Returns
        -------

        """
        blueprint_storage = utils.storage_dir(
            blueprint_id, storage_path=self._storage_path)
        shutil.rmtree(blueprint_storage, ignore_errors=True)

    def load_blueprint_storage(self, blueprint_id):
        """
        Loads blueprint storage object
        Parameters
        ----------
        blueprint_id: str

        Returns
        -------
        blueprint_storage: FileStorage
        """
        return blueprints.load_blueprint_storage_env(
            blueprint_id, storage_path=self._storage_path)

    def outputs(self, blueprint_id):
        """
        Retrieves outputs of a deployment
        Parameters
        ----------
        blueprint_id: str

        Returns
        -------
        outputs: dict
        """
        return blueprints.outputs(
            blueprint_id, storage_path=self._storage_path)

    def instances(self, blueprint_id, node_id=None):
        """
        Retrieves instances of a deployment
        Parameters
        ----------
        blueprint_id: str
        node_id: str
        Returns
        -------
        instances: dict
        """
        return blueprints.instances(blueprint_id,
                                    node_id=node_id,
                                    storage_path=self._storage_path)

    def create_requirements(self, blueprint_path):
        """
        Creates blueprint plugin dependencies
        Parameters
        ----------
        blueprint_path: str

        Returns
        -------
        requirements: set

        """
        return blueprints.create_requirements(blueprint_path)


class ExecutionsAPI(object):

    def __init__(self, storage_path=None):
        self._storage_path = storage_path

    def install(self,
                blueprint_id,
                parameters=None,
                allow_custom_parameters=None,
                task_retries=None,
                task_retry_interval=None):
        """
        Starts install workflow for a blueprint deployment
        Parameters
        ----------
        blueprint_id: str
        parameters: dict
        allow_custom_parameters: bool
        task_retries: int
        task_retry_interval: int

        Returns
        -------

        """
        environment = blueprints.load_blueprint_storage_env(
            blueprint_id, storage_path=self._storage_path)
        return workflows.install(
            blueprint_id,
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
                  task_retry_interval=None):
        """
        Starts uninstall workflow for a blueprint deployment
        Parameters
        ----------
        blueprint_id: str
        parameters: dict
        allow_custom_parameters: bool
        task_retries: int
        task_retry_interval: int

        Returns
        -------

        """
        environment = blueprints.load_blueprint_storage_env(
            blueprint_id, storage_path=self._storage_path)
        return workflows.uninstall(
            blueprint_id,
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
                       task_retry_interval=None):
        """
        Starts generic workflow for a blueprint deployment
        Parameters
        ----------
        blueprint_id: str
        parameters: dict
        allow_custom_parameters: bool
        task_retries: int
        task_retry_interval: int

        Returns
        -------

        """
        environment = blueprints.load_blueprint_storage_env(
            blueprint_id, storage_path=self._storage_path)
        return workflows.generic_execute(
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
        self.blueprints = BlueprintsAPI()
        self.executions = ExecutionsAPI()

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
