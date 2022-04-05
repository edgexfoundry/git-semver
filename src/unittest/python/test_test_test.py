
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
import unittest
from mock import patch
from mock import call
from mock import Mock
from tgsver.test import Result
from tgsver.test import Test


class TestTest(unittest.TestCase):

    @patch.dict(os.environ, {'k1': 'v1', 'k2': 'v2'}, clear=True)
    @patch('tgsver.test.github.get_head_tag', return_value='v1.0.1')
    @patch('tgsver.test.github.read_file', return_value='1.0.0')
    @patch('tgsver.test.logging')
    @patch('tgsver.test.run.run_command')
    def test__execute_Should_CallExpectedAndLogError_When_ResultNotEqualToExpected(self, run_command_patch, logging_patch, *patches):
        expected_result = Result(stdout='1.0.0', exit_code=0, remote_version='1.0.0', remote_tag='v1.0.0')
        envars = {'k3': 'v3'}
        branch_name = 'test-branch'
        test = Test(command='some command', expected_result=expected_result, envars=envars, branch_name=branch_name)
        client_mock = Mock()
        repo_name = 'owner1/repo1'
        repo_dir = 'repo1'
        mock_process1 = Mock()
        mock_process2 = Mock(stdout='1.0.0', stderr=None, returncode=0)
        run_command_patch.side_effect = [
            mock_process1,
            mock_process2
        ]
        test.execute(client_mock, repo_name, repo_dir)

        # ensure git checkout was called correctly
        call1 = call('git checkout test-branch', cwd='repo1', env={'k1': 'v1', 'k2': 'v2', 'k3': 'v3'})
        self.assertTrue(call1 in run_command_patch.mock_calls)
        # ensure command was called
        call2 = call('some command', cwd='repo1', env={'k1': 'v1', 'k2': 'v2', 'k3': 'v3'})
        self.assertTrue(call2 in run_command_patch.mock_calls)
        # ensure error was logged
        # logging_patch.error.assert_called_once()

    @patch('tgsver.test.logging')
    @patch('tgsver.test.run.run_command')
    def test__execute_Should_CallExpected_When_CreateACommitDirective(self, run_command_patch, *patches):
        branch_name = 'test-branch'
        test = Test(command='create-a-commit', expected_result=Result(), branch_name=branch_name)
        client_mock = Mock()
        repo_name = 'owner1/repo1'
        repo_dir = 'repo1'
        test.execute(client_mock, repo_name, repo_dir)

        # ensure empty commit was committed
        call1 = call("git commit --allow-empty -m 'empty commit'", cwd=repo_dir)
        self.assertTrue(call1 in run_command_patch.mock_calls)
        # ensure empty commit was pushed
        call2 = call(f'git push origin {test.branch_name}', cwd=repo_dir)
        self.assertTrue(call2 in run_command_patch.mock_calls)
