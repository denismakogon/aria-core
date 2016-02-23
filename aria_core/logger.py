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
import logging
import logging.config
import os
import copy


_lgr = None

_all_loggers = set()


def get_logger(name=__name__):
    return configure_loggers(name=name)


def all_loggers():
    return _all_loggers


def configure_loggers(name=None):
    # first off, configure defaults
    # to enable the use of the logger
    # even before the init was executed.
    _name = name if name else __name__
    _configure_defaults(name=_name)

    from aria_core import utils
    if utils.is_initialized():
        # init was already called
        # use the configuration file.
        _configure_from_file()

    return logging.getLogger(name=name if name else __name__)


def _configure_defaults(name=None):

    # add handlers to the main logger
    from aria_core import logger_config
    logger_dict = copy.deepcopy(logger_config.LOGGER)
    logger_dict['loggers'] = {
        name: {
            'handlers': list(logger_dict['handlers'].keys())
        }
    }
    from aria_core import logger_config
    logger_dict['handlers']['file'][
        'filename'] = logger_config.DEFAULT_LOG_FILE
    logfile_dir = os.path.dirname(
        logger_config.DEFAULT_LOG_FILE)
    if not os.path.exists(logfile_dir):
        os.makedirs(logfile_dir)

    logging.config.dictConfig(logger_dict)
    logging.getLogger(name).setLevel(logging.INFO)
    _all_loggers.add(name)


def _configure_from_file():

    from aria_core import logger_config
    config = logger_config.AriaConfig()
    logging_config = config.logging
    loggers_config = logging_config.loggers
    logfile = logging_config.filename

    # set filename on file handler
    logger_dict = copy.deepcopy(logger_config.LOGGER)
    logger_dict['handlers']['file']['filename'] = logfile
    logfile_dir = os.path.dirname(logfile)
    if not os.path.exists(logfile_dir):
        os.makedirs(logfile_dir)

    # add handlers to every logger
    # specified in the file
    loggers = {}
    for logger_name in loggers_config:
        loggers[logger_name] = {
            'handlers': list(logger_dict['handlers'].keys())
        }
    logger_dict['loggers'] = loggers

    # set level for each logger
    for logger_name, logging_level in loggers_config.iteritems():
        log = logging.getLogger(logger_name)
        level = logging._levelNames[logging_level.upper()]
        log.setLevel(level)
        _all_loggers.add(logger_name)

    logging.config.dictConfig(logger_dict)


def get_events_logger():

    def generic_events_logger(events):
        """
        The generic events logger logs the entire events.
        :param events: The events to log.
        :return:
        """
        for event in events:
            _lgr.info(json.dumps(event, indent=4))
            _lgr.info(str(Event(event)))

    return generic_events_logger


class Event(object):

    def __init__(self, event):
        self._event = event

    def __str__(self):
        deployment_id = self.deployment_id
        timestamp = self.timestamp
        event_type_indicator = self.event_type_indicator
        message = self.text
        info = self.operation_info

        if info:  # spacing in between of the info and the message
            info += ' '

        return '{0} {1} {2} {3}{4}'.format(timestamp,
                                           event_type_indicator,
                                           deployment_id,
                                           info,
                                           message)

    @property
    def operation_info(self):
        operation = self.operation
        node_id = self.node_id
        source_id = self.source_id
        target_id = self.target_id

        context = self._event['context']
        group = context.get('group')
        policy = context.get('policy')
        trigger = context.get('trigger')

        if source_id is not None:
            info = '{0}->{1}|{2}'.format(source_id, target_id, operation)
        else:
            info_elements = [
                e for e in [node_id, operation, group, policy, trigger]
                if e is not None]
            info = '.'.join(info_elements)
        if info:
            info = '[{0}]'.format(info)
        return info

    @property
    def text(self):
        message = self._event['message']['text'].encode('utf-8')
        if self.is_log_message:
            message = '{0}: {1}'.format(self.log_level, message)
        return message

    @property
    def log_level(self):
        return self._event['level'].upper()

    @property
    def timestamp(self):
        return (self._event.get('@timestamp') or self._event[
            'timestamp']).split('.')[0]

    @property
    def event_type_indicator(self):
        return 'LOG' if self.is_log_message else 'CFY'

    @property
    def operation(self):
        op = self._event['context'].get('operation')
        if op is None:
            return None
        return op.split('.')[-1]

    @property
    def node_id(self):
        return self._event['context'].get('node_id')

    @property
    def source_id(self):
        return self._event['context'].get('source_id')

    @property
    def target_id(self):
        return self._event['context'].get('target_id')

    @property
    def deployment_id(self):
        return '<{0}>'.format(self._event['context']['deployment_id'])

    @property
    def event_type(self):
        return self._event.get('event_type')  # not available for logs

    @property
    def is_log_message(self):
        return 'aria_log' in self._event['type']
