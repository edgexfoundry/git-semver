
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
from git.exc import InvalidGitRepositoryError
from pygsver.init import remove_entries
from pygsver.init import run_init
from pygsver.init import create_semver_branch
from pygsver.init import clone_semver_branch
from pygsver.init import remove_semver_folder
from pygsver.errors import InvalidPathError
from pygsver.errors import InvalidBranchError
from pygsver.errors import InvalidRepoError


class TestInit(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    def test__remove_entries_Should_CallExpected_When_Called(self, *patches):
        entries_mock = {
            ('groupa', ''): 'a',
            ('groupb', ''): 'b',
            ('groupc', ''): 'c',
            ('groupd', ''): 'd'
        }
        index_mock = Mock(entries=entries_mock)
        keep = [
            'groupb',
            'groupd',
            'groupd'
        ]
        remove_entries(index_mock, keep)
        index_mock.remove.assert_called_once_with(['groupa', 'groupc'])

    @patch('pygsver.init.remove_semver_folder')
    @patch('pygsver.init.clone_semver_branch')
    @patch('pygsver.init.create_semver_branch')
    @patch('pygsver.init.write_version')
    def test__run_init_Should_CreateSemverBranch_When_Expected(self, write_version_patch, create_semver_branch_patch, clone_semver_branch_patch, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver',
            'semver_remote_name': 'origin'
        }
        repo_mock = Mock(active_branch='main', branches=['main'])
        repo_mock.remote.return_value.refs = ['main']
        run_init(repo_mock, version='1.2.3-dev.1', force=False, settings=settings)
        create_semver_branch_patch.assert_called_once_with(repo_mock, '1.2.3-dev.1', settings)
        clone_semver_branch_patch.assert_called_once_with(repo_mock, '/repo/.semver', 'origin')
        write_version_patch.assert_called_once_with(settings, '1.2.3-dev.1', force=False)

    @patch('pygsver.init.remove_semver_folder')
    @patch('pygsver.init.clone_semver_branch')
    @patch('pygsver.init.create_semver_branch')
    @patch('pygsver.init.write_version')
    def test__run_init_Should_CloneSemverBranch_When_Expected(self, write_version_patch, create_semver_branch_patch, clone_semver_branch_patch, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver',
            'semver_remote_name': 'origin'
        }
        repo_mock = Mock(active_branch='main', branches=['main'])
        repo_mock.remote.return_value.refs = ['main', 'semver']
        run_init(repo_mock, version='1.2.3-dev.1', force=False, settings=settings)
        create_semver_branch_patch.assert_not_called()
        clone_semver_branch_patch.assert_called_once_with(repo_mock, '/repo/.semver', 'origin')
        write_version_patch.assert_called_once_with(settings, '1.2.3-dev.1', force=False)

    @patch('pygsver.init.remove_entries')
    @patch('pygsver.init.append_file')
    @patch('pygsver.init.write_file')
    @patch('pygsver.init.Head')
    def test__create_semver_branch_Should_CallExpected_When_Called(self, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_remote_name': 'origin',
            'semver_user_name': 'name',
            'semver_user_email': 'email'
        }
        repo_mock = Mock(git_dir='/some/path/here/.git')
        create_semver_branch(repo_mock, '1.0.0-dev.1', settings)
        repo_mock.git.checkout.assert_called_once_with('main', '-f')
        repo_mock.git.branch.assert_called_once_with('-D', 'semver')

    @patch('pygsver.init.append_file')
    def test__clone_semver_branch_Should_CallExpected_When_Called(self, append_file_patch, *patches):
        config_reader_mock = Mock()
        config_reader_mock.get_value.return_value = '--repo-url--'
        repo_mock = Mock(git_dir='/some/path/.git')
        repo_mock.config_reader.return_value = config_reader_mock
        clone_semver_branch(repo_mock, '/path/to/.semver', 'origin')
        append_file_patch.assert_called_once_with('/some/path/.git/info/exclude', '\n.semver\n')

    @patch('pygsver.init.os.path.exists', return_value=False)
    @patch('pygsver.init.shutil')
    def test__remove_semver_folder_Should_ReturnAndDoNothing_When_SemverPathDoesNotExist(self, shutil_patch, *patches):
        remove_semver_folder('/some/path/.semver')
        shutil_patch.assert_not_called()

    @patch('pygsver.init.os.path.exists', return_value=True)
    @patch('pygsver.init.os.path.isfile', return_value=True)
    def test__remove_semver_folder_Should_RaiseInvalidPathError_When_SemverPathIsAFile(self, *patches):
        with self.assertRaises(InvalidPathError):
            remove_semver_folder('/some/path/.semver')

    @patch('pygsver.init.os.path.exists', return_value=True)
    @patch('pygsver.init.os.path.isfile', return_value=False)
    @patch('pygsver.init.Repo')
    def test__remove_semver_folder_Should_RaiseInvalidBranchError_When_SemverRepoDoesNotHaveSemverBranch(self, repo_patch, *patches):
        repo_mock = Mock()
        repo_mock.remote.return_value.refs = ['main']
        repo_patch.return_value = repo_mock
        with self.assertRaises(InvalidBranchError):
            remove_semver_folder('/some/path/.semver')

    @patch('pygsver.init.os.path.exists', return_value=True)
    @patch('pygsver.init.os.path.isfile', return_value=False)
    @patch('pygsver.init.Repo')
    def test__remove_semver_folder_Should_RaiseInvalidRepoError_When_InvalidGitRepositoryError(self, repo_patch, *patches):
        repo_mock = Mock()
        repo_patch.side_effect = [InvalidGitRepositoryError]
        with self.assertRaises(InvalidRepoError):
            remove_semver_folder('/some/path/.semver')

    @patch('pygsver.init.os.path.exists', return_value=True)
    @patch('pygsver.init.os.path.isfile', return_value=False)
    @patch('pygsver.init.shutil')
    @patch('pygsver.init.Repo')
    def test__remove_semver_folder_Should_CallRemoveFolder_When_Expected(self, repo_patch, shutil_patch, *patches):
        repo_mock = Mock()
        repo_mock.remote.return_value.refs = ['main', 'semver']
        repo_patch.return_value = repo_mock
        remove_semver_folder('/some/path/.semver')
        shutil_patch.rmtree.assert_called_once_with('/some/path/.semver', ignore_errors=True)
