
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
from mock import mock_open
from tgsver.test import Suite
from tgsver.test import Test


class TestSuite(unittest.TestCase):

    @patch('tgsver.test.os.access', return_value=False)
    def test__load_tests_Should_RaiseValueError_When_PathIsNotAccessible(self, *patches):
        with self.assertRaises(ValueError):
            Suite.load_tests('/some/path')

    @patch('tgsver.test.os.access', return_value=True)
    @patch('tgsver.test.open', create=True)
    def test__load_tests_Should_ReturnTests_When_PathIsAccessible(self, open_patch, *patches):
        data = """[{"command": "command1", "expected_result": {"stdout": "0.0.1"}}, {"command": "command2", "expected_result": {"stdout": "0.0.1"}}]"""
        open_patch.side_effect = [
            mock_open(read_data=data).return_value
        ]
        result = Suite.load_tests('/some/path')
        self.assertTrue(len(result) == 2)

    @patch('tgsver.test.log.add_stream_handler')
    @patch('tgsver.test.github.clone_repo')
    @patch('tgsver.test.github.create_branch')
    @patch('tgsver.test.Suite.get_branch_names')
    @patch('tgsver.test.Suite.load_tests')
    @patch('tgsver.test.github.create_repo')
    @patch('tgsver.test.github.get_client')
    @patch('tgsver.test.Suite.ssh_setup')
    def test__Suite_Should_CallExpected_When_Called(self, ssh_setup_patch, get_client_patch, create_repo_patch, load_tests_patch, get_branch_names_patch, create_branch_patch, clone_repo_patch, *patches):
        create_repo_patch.return_value = {
            'ssh_url': 'some-ssh-url',
            'full_name': 'user1/repo1',
            'name': 'repo1'
        }
        client_mock = Mock()
        get_client_patch.return_value = client_mock
        get_branch_names_patch.return_value = ['branch1', 'branch2']
        suite = Suite(path='/some/path')
        # ensure ssh_setup is called
        ssh_setup_patch.assert_called_once()
        # ensure create repo is called
        create_repo_patch.assert_called_once_with(client_mock)
        # ensure load tests is called
        load_tests_patch.assert_called_once_with('/some/path')
        # ensure create branch is called for each branch found
        self.assertTrue(call(client_mock, 'user1/repo1', 'branch1') in create_branch_patch.mock_calls)
        self.assertTrue(call(client_mock, 'user1/repo1', 'branch2') in create_branch_patch.mock_calls)
        # ensure clone repo is called
        clone_repo_patch.assert_called_once_with('some-ssh-url', 'repo1')

    @patch('tgsver.test.log.add_stream_handler')
    @patch('tgsver.test.github.get_client')
    @patch('tgsver.test.github.create_repo')
    def test__get_branch_names_Should_ReturnExpected_When_Called(self, *patches):
        suite = Suite(setup_ssh=False, clone_repo=False)
        suite.tests = [Test(branch_name='branch1'), Test(branch_name='branch2'), Test(branch_name='main')]
        result = suite.get_branch_names()
        expected_result = ['branch1', 'branch2']
        self.assertEqual(result, expected_result)

    @patch('tgsver.test.log.add_stream_handler')
    @patch('tgsver.test.github.get_client')
    @patch('tgsver.test.github.create_repo')
    @patch('tgsver.test.run.run_command')
    def test__ssh_setup_Should_CallSshCommands_When_Called(self, run_command_patch, *patches):
        suite = Suite(setup_ssh=False, clone_repo=False)
        suite.ssh_setup()
        self.assertTrue(call('eval `ssh-agent` && ssh-add', expected_exit_codes=[0], shell=True) in run_command_patch.mock_calls)
        self.assertTrue(call('ssh -T git@github.com') in run_command_patch.mock_calls)

    @patch('tgsver.test.log.add_stream_handler')
    @patch('tgsver.test.github.get_client')
    @patch('tgsver.test.github.create_repo')
    @patch('tgsver.test.ProgressBar')
    def test__execute_Should_CallTestExecute_When_Called(self, *patches):
        suite = Suite(setup_ssh=False, clone_repo=False)
        test1 = Mock(command='command1', branch_name='branch1')
        test2 = Mock(command='command2', branch_name='branch2')
        suite.tests = [test1, test2]
        suite.execute()
        test1.execute.assert_called_once_with(suite.client, suite.repo_name, suite.repo_dir)

    @patch('tgsver.test.log.add_stream_handler')
    @patch('tgsver.test.github.get_client')
    @patch('tgsver.test.github.create_repo')
    @patch('builtins.print')
    @patch('tgsver.test.json.dump')
    @patch('tgsver.test.open', create=True)
    def test__summary_Should_CallExpected_When_SomeTestsFailed(self, mock_open, *patches):
        suite = Suite(setup_ssh=False, clone_repo=False)
        test1 = Mock(passed=True)
        test2 = Mock(passed=False)
        test3 = Mock(passed=True)
        suite.tests = [test1, test2, test3]
        suite.summary()

    @patch('tgsver.test.log.add_stream_handler')
    @patch('tgsver.test.github.get_client')
    @patch('tgsver.test.github.create_repo')
    @patch('builtins.print')
    @patch('tgsver.test.json.dump')
    @patch('tgsver.test.open', create=True)
    def test__summary_Should_CallExpected_When_AllTestsPassed(self, mock_open, json_dump_patch, *patches):
        suite = Suite(setup_ssh=False, clone_repo=False)
        test1 = Mock(passed=True)
        test2 = Mock(passed=True)
        test3 = Mock(passed=True)
        suite.tests = [test1, test2, test3]
        suite.summary()
        json_dump_patch.assert_called()
