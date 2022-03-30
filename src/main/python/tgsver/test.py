
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
import time
import logging

from tgsver.utils import run_command
from tgsver.utils import get_head_tag
from tgsver.utils import read_file
from tgsver.utils import get_client
from tgsver.utils import create_repo
from tgsver.utils import delete_repo
from tgsver.utils import clone_repo
from progress1bar import ProgressBar


logger = logging.getLogger(__name__)


class Result:

    def __init__(self, stdout=None, stderr=None, exit_code=None, remote_tag=None, remote_version=None):
        logger.debug('Result constructor')
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code if exit_code else 0
        self.remote_tag = remote_tag
        self.remote_version = remote_version


class Test:

    def __init__(self, command=None, expected_result=None, envars=None, branch_name=None):
        self.command = command
        self.expected_result = expected_result
        self.envars = envars if envars else {}
        self.branch_name = branch_name if branch_name else 'main'
        self.actual_result = None
        self.passed = None

    def execute(self, client, repo_name, repo_dir):
        # execute the command and store the result
        run_command_kwargs = {
            'cwd': repo_dir,
            'noop': False
        }
        if self.envars:
            run_command_kwargs['env'] = self.envars
        process = run_command(self.command, **run_command_kwargs)
        remote_tag = None
        if self.expected_result.remote_tag:
            remote_tag = get_head_tag(client, repo_name, self.branch_name)
        remote_version = None
        if self.expected_result.remote_version:
            remote_version = read_file(client, repo_name, 'semver', self.branch_name)
        self.actual_result = Result(stdout=process.stdout, stderr=process.stderr, exit_code=process.returncode, remote_tag=remote_tag, remote_version=remote_version)
        self.check_result()

    def check_result(self):
        # check the result and compare to the expected_result
        self.passed = (
            Test.check(self.actual_result.exit_code, self.expected_result.exit_code, 'exit code')
            and Test.check(self.actual_result.stdout, self.expected_result.stdout, 'stdout')
            and Test.check(self.actual_result.stderr, self.expected_result.stderr, 'stderr')
            and Test.check(self.actual_result.remote_tag, self.expected_result.remote_tag, 'remote tag')
            and Test.check(self.actual_result.remote_version, self.expected_result.remote_version, 'remote version'))

    @staticmethod
    def check(actual, expected, label):
        if expected is None:
            return True
        if isinstance(expected, int):
            result = expected == actual
        else:
            # expected should be string
            if actual is None:
                return False
            result = re.match(expected, actual) is not None
        if not result:
            logger.debug(f'check failed for {label}')
        return result


class Suite:

    def __init__(self, path=None):
        logger.debug('Suite constructor')
        self.client = get_client()
        repo = create_repo(self.client)
        self.repo_name = repo['full_name']
        self.repo_dir = clone_repo(repo['ssh_url'], repo['name'])
        self.path = path
        self.tests = []
        if self.path:
            self.load_tests()

    def __del__(self):
        logger.debug('Suite destructor')
        delete_repo(self.client, self.repo_name)

    def load_tests(self):
        logger.debug(f'loading tests from file {self.path}')
        if not os.access(self.path, os.R_OK):
            raise ValueError(f'path {self.path} is not accessible')
        with open(self.path, 'r') as infile:
            tests = json.loads(infile.read())

        for test in tests:
            expected_result_kwargs = test.pop('expected_result')
            test.pop('actual_result', None)
            test.pop('passed', None)
            test_obj = Test(**test)
            test_obj.expected_result = Result(**expected_result_kwargs)
            self.tests.append(test_obj)

    def setup():
        run_command('eval `ssh-agent`', noop=False)
        run_command('ssh-add', noop=False)
        run_command('ssh -T git@github.com', noop=False)
        run_command(f'cd /{self.repo_name}')

    def execute(self):
        logger.debug(f'executing {len(self.tests)} tests')
        with ProgressBar() as pb:
            pb.total = len(self.tests)
            # setup()
            for index, test in enumerate(self.tests):
                pb.alias = f'test{index}'
                test.execute(self.client, self.repo_name, self.repo_dir)
                pb.count += 1
            pb.alias = ''

    def tear_down(self):
        pass

    def summary(self):
        passed = 0
        failed = 0
        for test in self.tests:
            if test.passed:
                passed += 1
            else:
                failed += 1
            # passed += 1 if test.passed else failed += 1
        print(f'total number of tests: {len(self.tests)}')
        print(f'passed: {passed}')
        print(f'failed: {failed}')

    def create_tests(self):
        self.tests.append(Test(command='git-semver', expected_result=Result(stdout='the semver branch does not exist', exit_code=1)))
        self.tests.append(Test(command='git-semver init', expected_result=Result(stdout='0.0.0')))
        self.tests.append(Test(command='git-semver init --version=1.0.0-dev.1 --force', expected_result=Result(stdout='1.0.0-dev.1')))
        self.tests.append(Test(command='git-semver', expected_result=Result(stdout='1.0.0-dev.1')))
        self.tests.append(Test(command='git-semver push', expected_result=Result(stdout='1.0.0-dev.1')))
        self.tests.append(Test(command='rm -rf .semver', expected_result=Result()))
        self.tests.append(Test(command='git-semver', expected_result=Result(stdout='the semver branch does not exist', exit_code=1)))
        self.tests.append(Test(command='git-semver init', expected_result=Result(stdout='1.0.0-dev.1')))
        self.tests.append(Test(command='git-semver', expected_result=Result(stdout='1.0.0-dev.1')))
        self.tests.append(Test(command='git-semver tag', expected_result=Result(stdout='1.0.0-dev.1', remote_tag='1.0.0-dev.1', remote_version='1.0.0-dev.1'), branch_name='main'))
        self.tests.append(Test(command='git-semver bump pre', expected_result=Result(stdout='1.0.0-dev.2'), envars={'SEMVER_PRE_PREFIX': 'dev'}))
        self.tests.append(Test(command='git-semver push', expected_result=Result(stdout='1.0.0-dev.2')))
        self.tests.append(Test(command='git-semver tag', expected_result=Result(stdout='is already tagged with', exit_code=1, remote_tag='1.0.0-dev.1', remote_version='1.0.0-dev.1'), branch_name='main'))
        self.tests.append(Test(command='git-semver tag --force', expected_result=Result(stdout='1.0.0-dev.2', remote_tag='1.0.0-dev.2', remote_version='1.0.0-dev.2'), branch_name='main'))
        self.tests.append(Test(command='git-semver bump pre', expected_result=Result(stdout='1.0.0-dev.3'), envars={'SEMVER_PRE_PREFIX': 'dev'}))
        self.tests.append(Test(command='git-semver push', expected_result=Result(stdout='1.0.0-dev.3')))
        self.tests.append(Test(command='rm -rf .semver', expected_result=Result()))
        self.tests.append(Test(command='git-semver', expected_result=Result(stdout='the semver branch does not exist', exit_code=1)))
        self.tests.append(Test(command='git-semver init', expected_result=Result(stdout='1.0.0-dev.3')))
        self.tests.append(Test(command='git-semver', expected_result=Result(stdout='1.0.0-dev.3')))
        self.tests.append(Test(command='git-semver bump pre', expected_result=Result(stdout='1.0.0-dev.4'), envars={'SEMVER_PRE_PREFIX': 'dev'}))
        self.tests.append(Test(command='git-semver bump pre --prefix=rc', expected_result=Result(stdout='mismatch between current prerelease dev and bump rc', exit_code=1)))
        self.tests.append(Test(command='git-semver bump patch', expected_result=Result(stdout='1.0.1')))
        self.tests.append(Test(command='git-semver bump minor', expected_result=Result(stdout='1.1.0')))
        self.tests.append(Test(command='git-semver bump major', expected_result=Result(stdout='2.0.0')))
        self.tests.append(Test(command='git-semver bump pre --prefix=tst', expected_result=Result(stdout='2.0.0-tst.1')))
        self.tests.append(Test(command='git-semver bump pre', expected_result=Result(stdout='mismatch between current prerelease tst and bump dev', exit_code=1), envars={'SEMVER_PRE_PREFIX': 'dev'}))
        self.tests.append(Test(command='git-semver bump pre', expected_result=Result(stdout='2.0.0-tst.2'), envars={'SEMVER_PRE_PREFIX': 'tst'}))
        self.tests.append(Test(command='git-semver bump final', expected_result=Result(stdout='2.0.0')))


class TestEncoder(json.JSONEncoder):

    def default(self, obj):
        return obj.__dict__
