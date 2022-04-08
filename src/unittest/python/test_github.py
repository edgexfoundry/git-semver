
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
from tgsver.github import get_client
from tgsver.github import create_repo
from tgsver.github import delete_repo
from tgsver.github import create_branch
from tgsver.github import remove_branch
from tgsver.github import branch_exists
from tgsver.github import get_file_url
from tgsver.github import read_file
from tgsver.github import is_head_tagged
from tgsver.github import get_head_tag
from tgsver.github import clone_repo


class Testgithub(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('tgsver.github.os.getenv')
    @patch('tgsver.github.GitHubAPI')
    def test__get_client_Should_ReturnExpected_When_Called(self, githubapi_patch, *patches):
        expected = githubapi_patch.return_value
        actual = get_client()
        self.assertEqual(actual, expected)

    @patch('tgsver.github.os.getenv', return_value=None)
    def test__get_client_Should_RaiseException_When_Called(self, getenv_patch, *patches):
        with self.assertRaises(Exception):
            get_client()

    @patch('tgsver.github.time.strftime')
    def test__create_repo_Should_ReturnExpected_When_Called(self, *patches):
        client_mock = Mock()
        client_mock.post.return_value = 'user_name/test-git-semver-04-01-2022-17-39-15'
        expected = 'user_name/test-git-semver-04-01-2022-17-39-15'
        actual = create_repo(client_mock)
        self.assertEqual(actual, expected)

    def test__delete_repo_Should_NotCallDelete_When_Called(self, *patches):
        client_mock = Mock()
        delete_repo(client_mock, None)
        self.assertEqual(client_mock.delete.call_count, 0)

    def test__delete_repo_Should_CallDelete_When_Called(self, *patches):
        client_mock = Mock()
        delete_repo(client_mock, 'user_name/repo_name')
        client_mock.delete.assert_called_once_with('/repos/user_name/repo_name')

    def test__create_branch_Should_CallExpected_When_Called(self, *patches):
        client_mock = Mock()
        client_mock.get.return_value = [
            {
                'object': {
                    'sha': 'fe6c60ed88cf26d22c5aa9470adeaf94c41f6ac4',
                }
            }]
        create_branch(client_mock, 'user_name/repo_name', 'branch')
        client_mock.get.assert_called_once_with('/repos/user_name/repo_name/git/refs/heads')
        client_mock.post.assert_called_once_with(
            '/repos/user_name/repo_name/git/refs',
            json={
                'ref': 'refs/heads/branch',
                'sha': client_mock.get.return_value[-1]['object']['sha']
            })

    def test__remove_branch_Should_CallExpected_When_Called(self, *patches):
        client_mock = Mock()
        remove_branch(client_mock, 'user_name/repo_name', 'branch')
        client_mock.delete.assert_called_once_with('/repos/user_name/repo_name/git/refs/heads/branch')

    def test__branch_exists_Should_ReturnTrue_When_Called(self, *patches):
        client_mock = Mock()
        client_mock.get.return_value = [
            {
                'name': 'main'
            },
            {
                'name': 'branch'
            }]
        expected = True
        actual = branch_exists(client_mock, 'user_name/repo_name', 'branch')
        self.assertEqual(actual, expected)

    def test__branch_exists_Should_ReturnFalse_When_Called(self, *patches):
        client_mock = Mock()
        client_mock.get.return_value = [
            {
                'name': 'main'
            },
            {
                'name': 'branch1'
            }]
        expected = False
        actual = branch_exists(client_mock, 'user_name/repo_name', 'branch')
        self.assertEqual(actual, expected)

    @patch('tgsver.github.branch_exists', return_value=True)
    def test__get_file_url_Should_ReturnExpected_When_Called(self, *patches):
        client_mock = Mock()
        client_mock.get.return_value = {
            'tree': [
                {
                    'path': 'README.md',
                    'url': 'url'
                },
                {
                    'path': 'file',
                    'url': 'url1'
                }
            ]}
        expected = 'url1'
        actual = get_file_url(client_mock, 'user_name/repo_name', 'main', 'file')
        self.assertEqual(actual, expected)

    @patch('tgsver.github.branch_exists', return_value=False)
    def test__get_file_url_Should_ReturnNone_When_MissingBranch(self, *patches):
        client_mock = Mock()
        expected = None
        actual = get_file_url(client_mock, 'user_name/repo_name', 'main', 'file')
        self.assertEqual(actual, expected)

    @patch('tgsver.github.branch_exists', return_value=True)
    def test__get_file_url_Should_ReturnExpected_When_MissingFile(self, *patches):
        client_mock = Mock()
        client_mock.get.return_value = {
            'tree': [
                {
                    'path': 'README.md',
                    'url': 'url'
                },
                {
                    'path': 'file',
                    'url': 'url1'
                }
            ]}
        expected = None
        actual = get_file_url(client_mock, 'user_name/repo_name', 'main', 'file2')
        self.assertEqual(actual, expected)

    @patch('tgsver.github.get_file_url', return_value='file_url')
    @patch('tgsver.github.base64.b64decode')
    def test__read_file_Should_ReturnExpected_When_Called(self, b64decode_patch, *patches):
        client_mock = Mock()
        client_mock.get.return_value = {
            'content': 'encoded content',
            'encoding': 'base64'
        }
        b64decode_patch.return_value.decode.return_value = 'file content\n'
        expected = 'file content'
        actual = read_file(client_mock, 'user_name/repo_name', 'main', 'file')
        self.assertEqual(actual, expected)

    @patch('tgsver.github.get_file_url', return_value=None)
    def test__read_file_Should_ReturnNone_When_Called(self, *patches):
        client_mock = Mock()
        expected = None
        actual = read_file(client_mock, 'user_name/repo_name', 'main', 'file')
        self.assertEqual(actual, expected)

    def test__is_head_tagged_Should_ReturnTrue_When_Called(self, *patches):
        client_mock = Mock()
        client_mock.get.side_effect = [
            {'sha': 'sha_2'},
            [
                {
                    'commit': {
                        'sha': 'sha_1',
                    }
                },
                {
                    'commit': {
                        'sha': 'sha_2',
                    }
                }
            ]
        ]
        expected = True
        actual = is_head_tagged(client_mock, 'user_name/repo_name', 'main')
        self.assertEqual(actual, expected)

    def test__is_head_tagged_Should_ReturnFalse_When_Called(self, *patches):
        client_mock = Mock()
        client_mock.get.side_effect = [
            {'sha': 'sha_3'},
            [
                {
                    'commit': {
                        'sha': 'sha_1',
                    }
                },
                {
                    'commit': {
                        'sha': 'sha_2',
                    }
                }
            ]
        ]
        expected = False
        actual = is_head_tagged(client_mock, 'user_name/repo_name', 'main')
        self.assertEqual(actual, expected)

    def test__get_head_tag_Should_ReturnExpected_When_Called(self, *patches):
        client_mock = Mock()
        client_mock.get.side_effect = [
            {'sha': 'sha_1'},
            [
                {
                    'name': 'head_tag_1',
                    'commit': {
                        'sha': 'sha_1',
                    }
                },
                {
                    'name': 'head_tag_2',
                    'commit': {
                        'sha': 'sha_2',
                    }
                },
                {
                    'name': 'head_tag_3',
                    'commit': {
                        'sha': 'sha_1',
                    }
                }
            ]
        ]
        expected = ['head_tag_1', 'head_tag_3']
        actual = get_head_tag(client_mock, 'user_name/repo_name', 'main')
        self.assertEqual(actual, expected)

    def test__get_head_tag_Should_ReturnNone_When_Called(self, *patches):
        client_mock = Mock()
        client_mock.get.side_effect = [
            {'sha': 'sha_0'},
            [
                {
                    'name': 'head_tag_1',
                    'commit': {
                        'sha': 'sha_1',
                    }
                },
                {
                    'name': 'head_tag_2',
                    'commit': {
                        'sha': 'sha_2',
                    }
                },
                {
                    'name': 'head_tag_3',
                    'commit': {
                        'sha': 'sha_3',
                    }
                }
            ]
        ]
        expected = []
        actual = get_head_tag(client_mock, 'user_name/repo_name', 'main')
        self.assertEqual(actual, expected)

    @patch('tgsver.github.run.run_command')
    def test__clone_repo_Should_ReturnExpected_When_Called(self, *patches):
        actual = 'repo_name'
        expected = clone_repo('ssh_url', 'repo_name')
        self.assertEqual(actual, expected)
