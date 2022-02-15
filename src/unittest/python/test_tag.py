
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
from pygsver.tag import check_head_tag
from pygsver.tag import run_tag
from pygsver.tag import get_head_tags
from pygsver.errors import HeadTaggedError


class TestTag(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('pygsver.tag.get_head_tags', return_value=['v1.2.3-dev.1'])
    def test__check_head_tag_Should_RaiseHeadTaggedError_When_HeadTaggedNoForce(self, *patches):
        repo_mock = Mock()
        with self.assertRaises(HeadTaggedError):
            check_head_tag(repo_mock, False)

    @patch('pygsver.tag.get_head_tags', return_value=['v1.2.3-dev.1'])
    def test__check_head_tag_Should_DoNothing_When_Force(self, *patches):
        repo_mock = Mock()
        result = check_head_tag(repo_mock, True)
        self.assertIsNone(result)

    @patch('pygsver.tag.get_head_tags', return_value=[])
    def test__check_head_tag_Should_DoNothing_When_NoHeadTags(self, *patches):
        repo_mock = Mock()
        result = check_head_tag(repo_mock, False)
        self.assertIsNone(result)

    @patch('pygsver.tag.check_head_tag')
    @patch('pygsver.tag.read_version', return_value='1.2.3-dev.1')
    def test__run_tag_Should_CallExpected_When_Force(self, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver'
        }
        repo_mock = Mock()
        run_tag(repo_mock, force=True, settings=settings)
        repo_mock.git.tag.assert_called_once_with('-a', 'v1.2.3-dev.1', '-m', 'v1.2.3-dev.1', '-f')

    @patch('pygsver.tag.check_head_tag')
    @patch('pygsver.tag.read_version', return_value='1.2.3-dev.1')
    def test__run_tag_Should_CallExpected_When_NoForce(self, *patches):
        settings = {
            'semver_branch': 'main',
            'semver_path': '/repo/.semver'
        }
        repo_mock = Mock()
        run_tag(repo_mock, force=False, settings=settings)
        repo_mock.git.tag.assert_called_once_with('-a', 'v1.2.3-dev.1', '-m', 'v1.2.3-dev.1')

    def test__get_head_tags_Should_ReturnExpected_When_Called(self, *patches):
        repo_mock = Mock()
        repo_mock.head.commit = '1234567890'
        tag1_mock = Mock()
        tag1_mock.commit = '1234567890'
        tag1_mock.name = 'tag1'
        tag2_mock = Mock()
        tag2_mock.commit = '2234567890'
        tag2_mock.name = 'tag2'
        tag3_mock = Mock()
        tag3_mock.commit = '1234567890'
        tag3_mock.name = 'tag3'
        repo_mock.tags = [tag1_mock, tag2_mock, tag3_mock]
        result = get_head_tags(repo_mock)
        expected_result = ['tag1', 'tag3']
        self.assertEqual(result, expected_result)
