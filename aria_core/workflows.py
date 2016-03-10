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

import sys
import os

from aria_core import utils


def generic_execute(blueprint_id=None,
                    workflow_id=None,
                    parameters=None,
                    allow_custom_parameters=None,
                    task_retries=None,
                    task_retry_interval=None,
                    environment=None,
                    default_python_interpreter='python2.7',
                    storage_path=None):
    root_venv_path = utils.venv_path(blueprint_id,
                                     storage_path=storage_path)
    venv_path = os.path.join(root_venv_path, 'lib',
                             default_python_interpreter,
                             'site-packages')
    sys.path.append(venv_path)
    result = environment.execute(
        workflow=workflow_id,
        parameters=parameters,
        allow_custom_parameters=allow_custom_parameters,
        task_retries=task_retries,
        task_retry_interval=task_retry_interval)
    del sys.path[sys.path.index(venv_path)]
    return result


def install(blueprint_id,
            parameters=None,
            allow_custom_parameters=None,
            task_retries=None,
            task_retry_interval=None,
            environment=None):
    return generic_execute(blueprint_id=blueprint_id,
                           workflow_id='install',
                           parameters=parameters,
                           allow_custom_parameters=allow_custom_parameters,
                           task_retries=task_retries,
                           task_retry_interval=task_retry_interval,
                           environment=environment)


def uninstall(blueprint_id,
              parameters=None,
              allow_custom_parameters=None,
              task_retries=None,
              task_retry_interval=None,
              environment=None):
    return generic_execute(blueprint_id=blueprint_id,
                           workflow_id='uninstall',
                           parameters=parameters,
                           allow_custom_parameters=allow_custom_parameters,
                           task_retries=task_retries,
                           task_retry_interval=task_retry_interval,
                           environment=environment)
