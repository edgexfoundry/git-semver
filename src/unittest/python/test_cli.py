
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
from mock import Mock
from tgsver.cli import get_parser
from tgsver.cli import main


class Testcli(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('tgsver.cli.ArgumentParser')
    def test__get_parser_Should_ReturnExpected_When_Called(self, *patches):
        # not much to unit test here
        get_parser()

    @patch('tgsver.cli.log.setup_logging')
    @patch('tgsver.cli.test.Suite')
    @patch('tgsver.cli.get_parser')
    def test__main_Should_CallExpected_When_Called(self, get_parser_patch, suite_patch, setup_logging_patch, *patches):
        main()
        setup_logging_patch.assert_called_once_with()
        get_parser_patch.assert_called_once_with()
        get_parser_patch.return_value.parse_args.assert_called_once_with()
        suite_patch.assert_called_once_with(path='tests.json', keep_repo=get_parser_patch.return_value.parse_args.return_value.keep_repo)
        suite_patch.return_value.execute.assert_called_once_with()
        suite_patch.return_value.summary.assert_called_once_with()

    @patch('tgsver.cli.log.setup_logging')
    @patch('tgsver.cli.sys.exit')
    @patch('tgsver.cli.get_parser')
    def test__main_Should_Exit_When_Exception(self, get_parser_patch, exit_patch, *patches):
        parser_mock = Mock()
        parser_mock.parse_args.side_effect = Exception('Something bad happened')
        get_parser_patch.return_value = parser_mock
        main()
        exit_patch.assert_called_once_with(1)
