
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
from tgsver.test import Result


class TestResult(unittest.TestCase):

    def test__check_Should_ReturnExpected_When_Called(self, *patches):
        self.assertTrue(Result.check(None, None, 'a1'))
        self.assertFalse(Result.check('v1', None, 'a1'))
        self.assertTrue(Result.check(1, 1, 'a1'))
        self.assertFalse(Result.check(1, 2, 'a1'))
        self.assertTrue(Result.check('test1', ['test1', 'test2'], 'a1'))
        self.assertTrue(Result.check('test', 'test1', 'a1'))
        self.assertFalse(Result.check('test3', ['test1', 'test2'], 'a1'))
        self.assertFalse(Result.check('test3', 'test1', 'a1'))

    def test__equality_Should_ReturnExpected_When_ObjectsAreNotEqual(self, *patches):
        result1 = Result(stdout='stdout', stderr='stderr', exit_code=0, remote_tag='v3', remote_version='v2')
        result2 = Result(stdout='stdout', stderr='stderr', exit_code=0, remote_tag='v1', remote_version='v2')
        self.assertTrue(result1 != result2)

    def test__equality_Should_ReturnExpected_When_ObjectsAreEqual(self, *patches):
        result1 = Result(stdout='stdout', stderr='stderr', exit_code=0, remote_tag='v1', remote_version='v2')
        result2 = Result(stdout='stdout', stderr='stderr', exit_code=0, remote_tag='v1', remote_version='v2')
        self.assertTrue(result1 == result2)
        str(result1)
