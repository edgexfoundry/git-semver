
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
from mock import mock_open
from mock import call
from mock import Mock
from pygsver.utils import read_version
from pygsver.utils import write_version
from pygsver.utils import read_file
from pygsver.utils import write_file
from pygsver.utils import append_file
from pygsver.errors import BranchDoesNotExistError
from pygsver.errors import EmptyVersionError


class TestUtils(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('pygsver.utils.os.path.exists', return_value=False)
    def test__read_version_Should_RaiseBranchDoesNotExistError_When_SemverPathDoesNotExist(self, *patches):
        settings = {
            'semver_path': '/repo/.semver',
            'semver_branch': 'main'
        }
        with self.assertRaises(BranchDoesNotExistError):
            read_version(settings)

    @patch('pygsver.utils.os.path.exists', return_value=True)
    @patch('pygsver.utils.read_file', return_value=None)
    def test__read_version_Should_RaiseEmptyVersionError_When_NoVersion(self, *patches):
        settings = {
            'semver_path': '/repo/.semver',
            'semver_branch': 'main'
        }
        with self.assertRaises(EmptyVersionError):
            read_version(settings)

    @patch('pygsver.utils.os.path.exists', return_value=True)
    @patch('pygsver.utils.read_file', return_value='1.2.3-dev.1\n')
    def test__read_version_Should_CallExpected_When_Called(self, *patches):
        settings = {
            'semver_path': '/repo/.semver',
            'semver_branch': 'main'
        }
        result = read_version(settings)
        expected_result = '1.2.3-dev.1'
        self.assertEqual(result, expected_result)

    @patch('pygsver.utils.read_version', return_value='2.2.3-dev.1')
    @patch('pygsver.utils.os.path.exists', return_value=True)
    @patch('pygsver.utils.write_file')
    @patch('pygsver.utils.Actor')
    @patch('pygsver.utils.Repo')
    def test__write_version_Should_CallExpected_When_PathExistsDiffVersionAndForce(self, repo_patch, actor_patch, write_file_patch, *patches):
        repo_mock = Mock()
        repo_patch.return_value = repo_mock
        semver_path = '/repo/.semver'
        filename = 'main'
        version = '1.2.3-dev.1'
        settings = {
            'semver_path': semver_path,
            'semver_branch': filename,
            'semver_user_name': 'name',
            'semver_user_email': 'email'
        }
        write_version(settings, version, force=True)
        write_file_patch.assert_called_once_with(os.path.join(semver_path, filename), version)
        repo_patch.assert_called_once_with(semver_path)
        repo_mock.index.commit.assert_called_once_with('semver(main): 1.2.3-dev.1', author=actor_patch.return_value, committer=actor_patch.return_value, parent_commits=None)

    @patch('pygsver.utils.read_version', return_value='1.2.3-dev.1')
    @patch('pygsver.utils.os.path.exists', return_value=True)
    @patch('pygsver.utils.write_file')
    @patch('pygsver.utils.Repo')
    def test__write_version_Should_ReturnAndDoNothing_When_PathExistsSameVersionAndForce(self, repo_patch, write_file_patch, *patches):
        repo_mock = Mock()
        repo_patch.return_value = repo_mock
        semver_path = '/repo/.semver'
        filename = 'main'
        version = '1.2.3-dev.1'
        settings = {
            'semver_path': semver_path,
            'semver_branch': filename
        }
        write_version(settings, version, force=True)
        write_file_patch.assert_not_called()

    @patch('pygsver.utils.os.path.exists', return_value=False)
    @patch('pygsver.utils.write_file')
    @patch('pygsver.utils.Actor')
    @patch('pygsver.utils.Repo')
    def test__write_version_Should_CallExpected_When_PathDoesNotExistsAndNotForce(self, repo_patch, actor_patch, write_file_patch, *patches):
        repo_mock = Mock()
        repo_patch.return_value = repo_mock
        semver_path = '/repo/.semver'
        filename = 'main'
        version = '1.2.3-dev.1'
        settings = {
            'semver_path': semver_path,
            'semver_branch': filename,
            'semver_user_name': 'name',
            'semver_user_email': 'email'
        }
        write_version(settings, version, force=False)
        write_file_patch.assert_called_once_with(os.path.join(semver_path, filename), version)
        repo_patch.assert_called_once_with(semver_path)
        repo_mock.index.commit.assert_called_once_with('semver(main): 1.2.3-dev.1', author=actor_patch.return_value, committer=actor_patch.return_value, parent_commits=None)

    @patch('pygsver.utils.open', create=True)
    def test__read_file_Should_ReturnExpected_When_Called(self, open_patch, *patches):
        open_patch.side_effect = [
            mock_open(read_data='1.2.3-dev.1\n').return_value
        ]
        result = read_file('/some/path')
        expected_result = '1.2.3-dev.1\n'
        self.assertEqual(result, expected_result)

    @patch('pygsver.utils.open', create=True)
    def test__write_file_Should_CallExpected_When_Called(self, open_patch, *patches):
        write_file('/some/path', 'contents')
        open_patch.assert_called_once_with('/some/path', 'w')

    @patch('pygsver.utils.open', create=True)
    def test__append_file_Should_CallExpected_When_ContentsNotPresent(self, open_patch, *patches):
        file_mock = mock_open(read_data='1.2.3-dev.1\n')
        open_patch.side_effect = [
            file_mock.return_value
        ]
        append_file('/some/path', 'contents')
        open_patch.assert_called_once_with('/some/path', 'r+')
        file_mock().write.assert_called_once_with('contents')

    @patch('pygsver.utils.open', create=True)
    def test__append_file_Should_CallExpected_When_ContentsPresent(self, open_patch, *patches):
        open_patch.side_effect = [
            mock_open(read_data='data1\ncontents\ndata3').return_value
        ]
        append_file('/some/path', 'contents')
        open_patch.assert_called_once_with('/some/path', 'r+')
