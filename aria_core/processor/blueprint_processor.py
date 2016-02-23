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

from aria_core.dependencies import futures


def create_requirements(blueprint_path):

    parsed_dsl = futures.aria_dsl_parser.parse_from_path(
        dsl_file_path=blueprint_path)

    requirements = _plugins_to_requirements(
        blueprint_path=blueprint_path,
        plugins=parsed_dsl[
            futures.aria_dsl_constants.DEPLOYMENT_PLUGINS_TO_INSTALL
        ]
    )

    for node in parsed_dsl['nodes']:
        requirements.update(
            _plugins_to_requirements(
                blueprint_path=blueprint_path,
                plugins=node['plugins']
            )
        )

    return requirements


def _plugins_to_requirements(blueprint_path, plugins):

    sources = set()
    for plugin in plugins:
        if plugin[futures.aria_dsl_constants.PLUGIN_INSTALL_KEY]:
            source = plugin[
                futures.aria_dsl_constants.PLUGIN_SOURCE_KEY
            ]
            if '://' in source:
                # URL
                sources.add(source)
            else:
                # Local plugin (should reside under the 'plugins' dir)
                plugin_path = os.path.join(
                    os.path.abspath(os.path.dirname(blueprint_path)),
                    'plugins',
                    source)
                sources.add(plugin_path)
    return sources
