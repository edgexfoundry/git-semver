
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

import unittest
from mock import patch
from mock import call
from mock import Mock
from logging import DEBUG as logging_debug
from tgsver.log import add_stream_handler
from tgsver.log import remove_stream_handler
from tgsver.log import setup_logging
from tgsver.log import ColoredFormatter


class TestColoredFormatter(unittest.TestCase):

    @patch('tgsver.log.logging')
    def test__format_Should_CallExpected_When_Called(self, logging_patch, *patches):
        cf = ColoredFormatter()
        record_mock = Mock(levelno=logging_debug)
        cf.format(record_mock)
        # ensure formatter is called
        logging_patch.Formatter.assert_called()


class TestLog(unittest.TestCase):

    @patch('tgsver.log.logging')
    def test__add_stream_handler_ShouldCakkReturnExpected_When_Called(self, logging_patch, *patches):
        logger_mock = Mock()
        logging_patch.getLogger.return_value = logger_mock
        stream_handler_mock = Mock()
        logging_patch.StreamHandler.return_value = stream_handler_mock
        result = add_stream_handler()
        # ensure stream handler is returned
        self.assertEqual(result, stream_handler_mock)
        # ensure stream handler is added to root logger
        logger_mock.addHandler.assert_called_once_with(stream_handler_mock)

    @patch('tgsver.log.logging')
    def test__remove_stream_handler_ShouldCallExpected_When_Called(self, logging_patch, *patches):
        logger_mock = Mock()
        logging_patch.getLogger.return_value = logger_mock
        stream_handler_mock = Mock()
        remove_stream_handler(stream_handler_mock)
        # ensure stream handler is removed from root logger
        logger_mock.removeHandler.assert_called_once_with(stream_handler_mock)

    @patch('tgsver.log.os.path.basename', return_value='script-name')
    @patch('tgsver.log.logging')
    def test__setup_logging_ShouldCallExpected_When_Called(self, logging_patch, *patches):
        logger_mock = Mock()
        logging_patch.getLogger.return_value = logger_mock
        file_handler_mock = Mock()
        logging_patch.FileHandler.return_value = file_handler_mock
        setup_logging()
        # ensure filehandler was called
        logging_patch.FileHandler.assert_called_once_with('script-name.log')
        # ensure filehandler is added to root logger
        logger_mock.addHandler.assert_called_once_with(file_handler_mock)
