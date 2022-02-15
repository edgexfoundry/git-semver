
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
import logging
import unittest
from argparse import Namespace
from mock import patch
from mock import Mock
from pygsver.cli import run_command
from pygsver.cli import main
from pygsver.cli import get_parser
from pygsver.cli import configure_logging
from pygsver.cli import get_settings
from pygsver.cli import is_true
from pygsver.cli import update_settings


logger = logging.getLogger(__name__)

consoleHandler = logging.StreamHandler(sys.stdout)
logFormatter = logging.Formatter("%(asctime)s %(threadName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
consoleHandler.setFormatter(logFormatter)
rootLogger = logging.getLogger()
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.DEBUG)


class TestCli(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('pygsver.cli.read_version', return_value='1.2.3-dev.1')
    @patch('pygsver.cli.update_settings')
    @patch('pygsver.cli.Repo')
    @patch('pygsver.bump.run_bump')
    def test__run_command_Should_CallExpected_When_Called(self, run_bump_patch, repo_patch, *patches):
        function_mock = Mock()
        options = {
            'command': 'bump',
            'prefix': 'pre',
            'subcmd': function_mock
        }
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver',
            'semver_user_name': 'name',
            'semver_user_email': 'email'
        }
        repo_mock = Mock()
        repo_patch.return_value = repo_mock
        run_command(options, settings)
        function_mock.assert_called_once_with(repo_mock, prefix='pre', settings=settings)

    @patch('pygsver.cli.os.getcwd', return_value='.')
    @patch('pygsver.cli.configure_logging')
    @patch('pygsver.cli.run_command')
    @patch('pygsver.cli.get_settings')
    @patch('pygsver.cli.get_parser')
    def test__main_Should_CallExpected_When_Called(self, get_parser_patch, get_settings_patch, run_command_patch, *patches):
        args_mock = Namespace()
        get_parser_patch.return_value.parse_args.return_value = args_mock
        main()
        run_command_patch.assert_called_once_with(vars(args_mock), get_settings_patch.return_value)

    @patch('pygsver.cli.os.getcwd', return_value='.')
    @patch('pygsver.cli.configure_logging')
    @patch('pygsver.cli.sys.exit')
    @patch('pygsver.cli.get_settings')
    @patch('pygsver.cli.get_parser')
    def test__main_Should_CallExpected_When_Exception(self, get_parser_patch, get_settings_patch, exit_patch, *patches):
        args_mock = Namespace()
        get_parser_patch.return_value.parse_args.return_value = args_mock
        get_settings_patch.side_effect = Exception('something bad happened')
        main()
        exit_patch.assert_called_once_with(1)

    @patch('pygsver.cli.argparse.ArgumentParser')
    def test__get_parser_Should_ReturnExpected_When_Called(self, *patches):
        # not much to unit test here
        get_parser()

    @patch('pygsver.cli.is_true', return_value=True)
    @patch('pygsver.cli.logging')
    def test__configure_logging_Should_CallExpected_When_Called(self, logging_patch, *patches):
        root_logger_mock = Mock()
        logging_patch.getLogger.return_value = root_logger_mock
        # not much to test here
        configure_logging()

    @patch.dict(os.environ, {'GIT_COMMITTER_EMAIL': 'kings_of_leon@rock.org', 'GIT_AUTHOR_NAME': 'notion', 'SEMVER_BRANCH': 'mybranch'}, clear=True)
    @patch('pygsver.cli.os.getcwd', return_value='/some/path/here')
    def test__get_settings_Should_ReturnDefaults_When_Called(self, *patches):
        result = get_settings()
        expected_result = {
            'semver_branch': 'mybranch',
            'semver_remote_name': None,
            'semver_user_name': 'notion',
            'semver_user_email': 'kings_of_leon@rock.org',
            'semver_path': '/some/path/here/.semver',
        }
        self.assertEqual(result, expected_result)

    def test__is_true_Should_ReturnExpected_When_Called(self, *patches):
        for value in ['TRUE', '1', 'Yes', 'On']:
            self.assertTrue(is_true(value))
        for value in ['false', '0', 'no', 'off', '']:
            self.assertFalse(is_true(value))

    def test__update_settings_Should_UpdateSettings_When_Called(self, *patches):
        repo_mock = Mock()
        repo_mock.remote.return_value.name = 'remote1'
        repo_mock.active_branch.name = 'branch1'
        settings = {
            'semver_branch': None,
            'semver_remote_name': None
        }
        update_settings(repo_mock, settings)
        self.assertTrue(settings['semver_branch'] == 'branch1')
        self.assertTrue(settings['semver_remote_name'] == 'remote1')
