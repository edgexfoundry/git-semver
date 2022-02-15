
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
from pygsver.push import run_push


class TestPush(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('pygsver.push.Repo')
    def test__run_push_Should_CallExpected_When_Called(self, repo_patch, *patches):
        semver_repo_mock = Mock()
        repo_patch.return_value = semver_repo_mock
        settings = {
            'semver_remote_name': 'origin',
            'semver_path': '/repo/.semver'
        }
        repo_mock = Mock()
        run_push(repo_mock, settings=settings)
        self.assertTrue(call('origin', 'semver') in semver_repo_mock.git.push.mock_calls)
        self.assertTrue(call('origin', 'refs/tags/v*:refs/tags/v*') in repo_mock.git.push.mock_calls)
