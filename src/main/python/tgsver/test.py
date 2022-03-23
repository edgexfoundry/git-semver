
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

import re
import os
import json
import logging

from tgsver.utils import run_command
from tgsver.utils import get_head_tag
from tgsver.utils import read_file
from tgsver.utils import get_client


logger = logging.getLogger(__name__)


class Result:

    def __init__(self, stdout=None, stderr=None, exit_code=None, remote_tag=None, remote_version=None):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.remote_tag = remote_tag
        self.remote_version = remote_version


class Test:

    def __init__(self, command, expected_result, envars=None, branch_name=None):
        self.command = command
        self.expected_result = expected_result
        self.envars = {} if not envars else envars
        self.branch_name = 'main' if not branch_name else branch_name
        self.expected_result = expected_result
        self.actual_result = None
        self.passed = False

    def execute(self, client, repo_name):
        # execute the command and store the result
        process = run_command(self.command, env=self.envars)
        remote_tag = get_head_tag(client, repo_name, self.branch_name)
        remote_version = read_file(client, repo_name, 'semver', self.branch_name)
        self.actual_result = Result(process.stdout, process.stderr, process.exit_code, remote_tag, remote_version)
        # check the result
        self.passed = self.check_result()

    def check_result(self):
        # check the result and compare to the expected_result
        self.passed = Test.check(self.actual_result.exit_code, self.expected_result.exit_code, 'exit code') and Test.check(self.actual_result.stdout, self.expected_result.stdout, 'stdout') and Test.check(self.actual_result.stderr, self.expected_result.stderr, 'stderr') and Test.check(self.actual.remote_tag, self.expected_result.remote_tag, 'remote tag') and Test.check(self.actual_result.remote_version, self.expected_result.remote_version, 'remote version')

    @staticmethod
    def check(actual, expected, label):
        if expected is None:
            return True
        if isinstance(expected, int):
            result = expected == actual
        else:
            # expected should be string
            result = re.match(expected, actual) is not None
        if not result:
            logger.debug(f'check failed for {label}')
        return result


class Suite:

    def __init__(self, repo_name, path=None):
        self.repo_name = repo_name
        self.client = get_client()
        self.path = path
        self.tests = []
        if self.path:
            self.load_tests()

    def load_tests(self):
        if not os.access(self.path, os.R_OK):
            raise ValueError(f'{self.path} is not accessible')
        # load tests from self.path
        with open(self.path, 'r') as infile:
            for line in infile:
                self.tests.append(json.loads(line))

    def execute(self):
        pass

    def setup(self):
        pass

    def tear_down(self):
        pass

    def create_summary(self):
        pass

    def create_tests(self):
        self.tests.append(Test('git semver', Result(stdout='the semver branch does not exist', exit_code=1)))
        self.tests.append(Test('git semver init', Result(stdout='0.0.0', exit_code=0)))
        self.tests.append(Test('git semver init --version=1.0.0-dev.1 --force', Result(stdout='1.0.0-dev.1', exit_code=0)))
        self.tests.append(Test('git semver', Result(stdout='1.0.0-dev.1', exit_code=0)))
        self.tests.append(Test('git semver push', Result(stdout='1.0.0-dev.1', exit_code=0)))


class TestEncoder(json.JSONEncoder):

    def default(self, obj):
        return obj.__dict__
