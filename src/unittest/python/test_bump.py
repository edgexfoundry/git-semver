
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
from pygsver.bump import bump_version
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

    @patch('pygsver.bump.write_version')
    @patch('pygsver.bump.bump_version')
    @patch('pygsver.bump.read_version')
    def test__run_bump_Should_CallExpected_When_Called(self, read_version_patch, bump_version_patch, write_version_patch, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver'
        }
        repo_mock = Mock()
        run_bump(repo_mock, axis='--axis--', prefix='--prefix--', settings=settings)
        bump_version_patch.assert_called_once_with(read_version_patch.return_value, '--axis--', '--prefix--')
        write_version_patch.assert_called_once_with(settings, str(bump_version_patch.return_value), force=True)

    def test__check_prerelease_Should_RaisePrereleaseMismatchError_When_PrereleaseMismatch(self, *patches):
        with self.assertRaises(PrereleaseMismatchError):
            check_prerelease('dev.1', 'test')
        check_prerelease('dev.1', 'dev')

    def test__bump_version_Should_ReturnExpectedVersion_When_Called(self, *patches):
        self.assertEqual(str(bump_version('0.1.0', 'major', None)), '1.0.0')
        self.assertEqual(str(bump_version('0.1.0', 'minor', None)), '0.2.0')
        self.assertEqual(str(bump_version('0.1.0', 'patch', None)), '0.1.1')
        self.assertEqual(str(bump_version('0.1.1', 'patch', 'dev')), '0.1.2')
        self.assertEqual(str(bump_version('0.1.0', 'pre', 'dev')), '0.1.1-dev.1')
        self.assertEqual(str(bump_version('0.1.1-dev.1', 'pre', 'dev')), '0.1.1-dev.2')
        self.assertEqual(str(bump_version('0.1.1-dev.2', 'final', None)), '0.1.1')
        with self.assertRaises(PrereleaseMismatchError):
            bump_version('0.1.1-dev.1', 'pre', 'rc')

        self.assertEqual(str(bump_version('1.0.0', 'pre', 'dev')), '1.0.1-dev.1')

        version = bump_version('1.0.1', 'pre', 'dev')
        self.assertEqual(str(version), '1.0.2-dev.1')

        version = bump_version(str(version), 'pre', 'dev')
        self.assertEqual(str(version), '1.0.2-dev.2')

        version = bump_version(str(version), 'patch', None)
        self.assertEqual(str(version), '1.0.3')

        version = bump_version(str(version), 'pre', 'dev')
        self.assertEqual(str(version), '1.0.4-dev.1')

        version = bump_version(str(version), 'minor', None)
        self.assertEqual(str(version), '1.1.0')

        version = bump_version(str(version), 'pre', 'dev')
        self.assertEqual(str(version), '1.1.1-dev.1')

        version = bump_version(str(version), 'major', None)
        self.assertEqual(str(version), '2.0.0')

        version = bump_version(str(version), 'pre', 'dev')
        self.assertEqual(str(version), '2.0.1-dev.1')

        version = bump_version(str(version), 'final', None)
        self.assertEqual(str(version), '2.0.1')

        version = bump_version(str(version), 'pre', 'dev')
        self.assertEqual(str(version), '2.0.2-dev.1')

        version = bump_version(str(version), 'pre', None)
        self.assertEqual(str(version), '2.0.2-dev.2')
