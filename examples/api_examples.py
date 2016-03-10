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

from aria_core import api as aria_core_api


def with_aria_core_api(action):
    def wrap(*args, **kwargs):
        api = aria_core_api.AriaCoreAPI(
            storage_path=None)
        action(api, *args, **kwargs)
    return wrap


@with_aria_core_api
def validate_blueprint(*args):
    api, blueprint_path = args
    api.blueprints.validate(blueprint_path)


@with_aria_core_api
def init_blueprint(*args, **kwargs):
    api, blueprint_id, blueprint_path = args
    api.blueprints.initialize(blueprint_id,
                              blueprint_path,
                              inputs=kwargs.get('inputs'),
                              install_plugins=kwargs.get(
                                  'install_plugins', False))


@with_aria_core_api
def teardown_blueprint(*args, **kwargs):
    api, blueprint_id = args
    api.blueprints.teardown(blueprint_id)


@with_aria_core_api
def install(*args, **kwargs):
    api, blueprint_id = args
    (parameters, allow_custom_parameters,
     task_retries, task_retry_interval) = (kwargs.get('parameters'),
                                           kwargs.get('allow_custom_parameters'),
                                           kwargs.get('task_retries', 10),
                                           kwargs.get('task_retry_interval', 10))
    api.executions.install(blueprint_id,
                           parameters=parameters,
                           allow_custom_parameters=allow_custom_parameters,
                           task_retries=task_retries,
                           task_retry_interval=task_retry_interval)


@with_aria_core_api
def outputs(*args, **kwargs):
    api, blueprint_id = args
    print(api.blueprints.outputs(blueprint_id))


@with_aria_core_api
def uninstall(*args, **kwargs):
    api, blueprint_id = args
    (parameters, allow_custom_parameters,
     task_retries, task_retry_interval) = (kwargs.get('parameters'),
                                           kwargs.get('allow_custom_parameters'),
                                           kwargs.get('task_retries', 10),
                                           kwargs.get('task_retry_interval', 10))
    api.executions.uninstall(blueprint_id,
                             parameters=parameters,
                             allow_custom_parameters=allow_custom_parameters,
                             task_retries=task_retries,
                             task_retry_interval=task_retry_interval)


if __name__ == "__main__":

    blueprint_id = raw_input("Input blueprint ID:")
    _blueprint_path = raw_input("Input existing blueprint path:")
    inputs_path = raw_input("Input path to a deployment inputs:")
    validate_blueprint(_blueprint_path)
    init_blueprint(blueprint_id, _blueprint_path, inputs=inputs_path, install_plugins=True)
    install(blueprint_id)
    outputs(blueprint_id)
    uninstall(blueprint_id)
    teardown_blueprint(blueprint_id)
