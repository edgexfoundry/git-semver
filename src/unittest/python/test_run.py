
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
from tgsver.run import run_command


class TestRun(unittest.TestCase):

    @patch('tgsver.run.subprocess.run')
    def test__run_command_Should_ReturnExpected_When_Called(self, subprocess_run_patch, *patches):
        process_mock = Mock(stdout='stdout', stderr='stderr')
        subprocess_run_patch.return_value = process_mock
        expected_result = run_command('command')
        self.assertEqual(expected_result, process_mock)

    @patch('tgsver.run.subprocess.run')
    def test__run_command_Should_PassKeywordArgumentsToSubprocessRun_When_KeywordArgumentsProvided(self, subprocess_run_patch, *patches):
        run_command('command', k1='v1', k2='v2')
        subprocess_run_patch.assert_called_once_with(['command'], capture_output=True, text=True, k1='v1', k2='v2')

    @patch('tgsver.run.subprocess.run')
    def test__run_command_Should_RaiseException_When_ExpectedExitCodesProvidedAndDoNotMatch(self, subprocess_run_patch, *patches):
        process_mock = Mock(returncode=1)
        subprocess_run_patch.return_value = process_mock
        with self.assertRaises(Exception):
            run_command('command', expected_exit_codes=[0, 255])
