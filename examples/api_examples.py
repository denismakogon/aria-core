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

import tempfile
import shutil

from aria_core import api as aria_core_api


def with_aria_core_api(action):
    def wrap(*args, **kwargs):
        aria_core_storage = tempfile.mkdtemp(
                prefix='aria_storage_dir')
        api = aria_core_api.AriaCoreAPI(
            aria_core_storage)
        action(api, *args, **kwargs)
        shutil.rmtree(aria_core_storage, ignore_errors=True)
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
    api.blueprints.teardown(blueprint_id)


if __name__ == "__main__":
    print("Input existing blueprint path")
    _blueprint_path = raw_input()
    validate_blueprint(_blueprint_path)
    init_blueprint('blueprint_id', _blueprint_path, install_plugins=True)
