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

import json

from aria_core import exceptions
from aria_core import logger
from aria_core import utils
from aria_core.dependencies import futures


from aria_core.processor import virtualenv_processor
from aria_core.processor import blueprint_processor

LOG = logger.logging.getLogger(__name__)

initialize_blueprint = virtualenv_processor.initialize_blueprint
create_requirements = blueprint_processor.create_requirements
install_blueprint_plugins = virtualenv_processor.install_blueprint_plugins


def validate(blueprint_path):
    try:
        return futures.aria_dsl_parser.parse_from_path(
            str(blueprint_path)
            if not isinstance(blueprint_path, file)
            else blueprint_path.name)
    except futures.aria_dsl_exceptions.DSLParsingException as e:
        LOG.error(str(e))
        raise Exception("Failed to validate blueprint. %s", str(e))


def init_blueprint_storage(blueprint_id):
    return futures.aria_local.FileStorage(
        storage_dir=utils.storage_dir(blueprint_id))


def with_blueprint_storage(action):

    def with_blueprint_storage_wrapper(*args, **kwargs):
        b_id = args[0]
        env = load_blueprint_storage_env(b_id)
        yield action(env, **kwargs)

    return with_blueprint_storage_wrapper


def coroutine(generator_func):

    def coroutine_wrapper(*args, **kwargs):
        return generator_func(*args, **kwargs).next()

    return coroutine_wrapper


def load_blueprint_storage_env(blueprint_id):
    return futures.aria_local.load_env(
        name=blueprint_id,
        storage=init_blueprint_storage(blueprint_id))


@coroutine
@with_blueprint_storage
def outputs(env):
    _outputs = json.dumps(env.outputs() or {},
                          sort_keys=True, indent=2)
    return _outputs


@coroutine
@with_blueprint_storage
def instances(env, node_id=None):
    node_instances = env.storage.get_node_instances(node_id=node_id)
    if not node_instances:
        raise exceptions.AriaError('No node with id: {0}'
                                   .format(node_id))
    return node_instances
