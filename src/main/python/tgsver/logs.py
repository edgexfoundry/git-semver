
# Copyright (c) 2022 Intel Corporation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from colorama import Style
from colorama import Fore
import logging

logger = logging.getLogger(__name__)


class ColoredFormatter(logging.Formatter):
    """  colored formatter
    """
    level_format = {
        logging.DEBUG: Style.DIM + "%(levelname)s" + Style.RESET_ALL,
        logging.INFO: Style.BRIGHT + "%(levelname)s" + Style.RESET_ALL,
        logging.WARNING: Style.BRIGHT + Fore.YELLOW + "%(levelname)s" + Style.RESET_ALL,
        logging.ERROR: Style.BRIGHT + Fore.RED + "%(levelname)s" + Style.RESET_ALL,
        logging.CRITICAL: Style.BRIGHT + Fore.RED + "%(levelname)s" + Style.RESET_ALL,
    }

    def format(self, record):
        level_format = self.level_format.get(record.levelno)
        formatter = logging.Formatter("[" + level_format + "]  %(message)s")
        return formatter.format(record)


def setup_logging():
    """ configure logging and create logfile if specified
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    name = os.path.basename(sys.argv[0])
    file_handler = logging.FileHandler(f'{name}.log')
    file_formatter = logging.Formatter("%(asctime)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)


def add_stream_handler(stream_handler=None):
    """ add stream handler to logging
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    if not stream_handler:
        stream_handler = logging.StreamHandler()
        stream_formatter = ColoredFormatter()
        stream_handler.setFormatter(stream_formatter)
        stream_handler.setLevel(logging.INFO)
    root_logger.addHandler(stream_handler)
    return stream_handler


def remove_stream_handler(stream_handler):
    """ remove stream handler from logging
    """
    root_logger = logging.getLogger()
    root_logger.removeHandler(stream_handler)
