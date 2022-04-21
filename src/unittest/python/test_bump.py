
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
from pygsver.bump import run_bump
from pygsver.bump import check_prerelease
from pygsver.errors import PrereleaseMismatchError


class TestBump(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('pygsver.bump.check_prerelease')
    @patch('pygsver.bump.read_version', return_value='1.2.3-dev.1')
    @patch('pygsver.bump.write_version')
    def test__run_bump_Should_CallExpected_When_BumpPre(self, write_version_patch, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver'
        }
        repo_mock = Mock()
        run_bump(repo_mock, axis='pre', prefix='dev', settings=settings)
        write_version_patch.assert_called_once_with(settings, '1.2.3-dev.2', force=True)

    @patch('pygsver.bump.check_prerelease')
    @patch('pygsver.bump.read_version', return_value='4.8.0')
    @patch('pygsver.bump.write_version')
    def test__run_bump_Should_CallExpected_When_BumpPrePatchZeroNoPreRelease(self, write_version_patch, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver'
        }
        repo_mock = Mock()
        run_bump(repo_mock, axis='pre', prefix='dev', settings=settings)
        write_version_patch.assert_called_once_with(settings, '4.8.1-dev.1', force=True)

    @patch('pygsver.bump.read_version', return_value='1.2.3-dev.1')
    @patch('pygsver.bump.write_version')
    def test__run_bump_Should_CallExpected_When_BumpFinal(self, write_version_patch, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver'
        }
        repo_mock = Mock()
        run_bump(repo_mock, axis='final', prefix=None, settings=settings)
        write_version_patch.assert_called_once_with(settings, '1.2.3', force=True)

    @patch('pygsver.bump.read_version', return_value='1.2.3-dev.1')
    @patch('pygsver.bump.write_version')
    def test__run_bump_Should_CallExpected_When_BumpPatch(self, write_version_patch, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver'
        }
        repo_mock = Mock()
        run_bump(repo_mock, axis='patch', prefix=None, settings=settings)
        write_version_patch.assert_called_once_with(settings, '1.2.4', force=True)

    @patch('pygsver.bump.read_version', return_value='1.2.3-dev.1')
    @patch('pygsver.bump.write_version')
    def test__run_bump_Should_CallExpected_When_BumpMinor(self, write_version_patch, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver'
        }
        repo_mock = Mock()
        run_bump(repo_mock, axis='minor', prefix=None, settings=settings)
        write_version_patch.assert_called_once_with(settings, '1.3.0', force=True)

    @patch('pygsver.bump.read_version', return_value='1.2.3-dev.1')
    @patch('pygsver.bump.write_version')
    def test__run_bump_Should_CallExpected_When_BumpMajor(self, write_version_patch, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver'
        }
        repo_mock = Mock()
        run_bump(repo_mock, axis='major', prefix=None, settings=settings)
        write_version_patch.assert_called_once_with(settings, '2.0.0', force=True)

    def test__check_prerelease_Should_RaisePrereleaseMismatchError_When_PrereleaseMismatch(self, *patches):
        with self.assertRaises(PrereleaseMismatchError):
            check_prerelease('dev.1', 'test')
        check_prerelease('dev.1', 'dev')
