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


# flake8: noqa

from cloudify import exceptions as aria_aside_exceptions
from cloudify import ctx as aria_ctx
from cloudify import utils as aria_side_utils

from cloudify.decorators import operation as aria_operation
from cloudify.decorators import workflow as aria_workflow
from cloudify.workflows import ctx as aria_workflow_ctx
from cloudify.workflows import local as aria_local

from dsl_parser import constants as aria_dsl_constants
from dsl_parser import exceptions as aria_dsl_exceptions
from dsl_parser import parser as aria_dsl_parser
from dsl_parser import utils as aria_dsl_utils

IGNORED_LOCAL_WORKFLOW_MODULES = (
    'cloudify_agent.operations',
    'cloudify_agent.installer.operations',
    'worker_installer.tasks',
    'plugin_installer.tasks',
    'windows_agent_installer.tasks',
    'windows_plugin_installer.tasks',
)
