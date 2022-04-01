
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
from functools import wraps
from colorama import Style
from colorama import Fore

import tgsver.utils as utils
import tgsver.logs as logs
from progress1bar import ProgressBar


logger = logging.getLogger(__name__)


class Result:

    def __init__(self, stdout=None, stderr=None, exit_code=None, remote_tag=None, remote_version=None):
        logger.debug('executing Result constructor')
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code if exit_code else 0
        self.remote_tag = remote_tag
        self.remote_version = remote_version

    def __eq__(self, other):
        return (
            Result.check(self.exit_code, other.exit_code, 'exit_code')
            and Result.check(self.remote_tag, other.remote_tag, 'remote_tag')
            and Result.check(self.remote_version, other.remote_version, 'remote_version')
            and Result.check(self.stdout, other.stdout, 'stdout')
            and Result.check(self.stderr, other.stderr, 'stderr'))

    @staticmethod
    def check(value1, value2, attr):
        # logger.debug(f"checking values of attribute '{attr}'")
        if not value1:
            result = True
        elif not value2:
            result = False
        elif isinstance(value1, int):
            result = value1 == value2
        else:
            result = value1 in value2
        if not result:
            logger.error(f"check values for attribute '{attr}' failed")
        return result

    # def __hash__(self):
    #     # required if modelling an immutable type
    #     return hash((self.stdout, self.stderr, self.exit_code, self.remote_tag, self.remote_version))

    def __str__(self):
        string = f"""
            ------------------------
            exit_code: {self.exit_code}
            remote_tag: {self.remote_tag}
            remote_version: {self.remote_version}
            stdout: {self.stdout}
            stderr: {self.stderr}
            ------------------------"""
        return '\n'.join([line.strip() for line in string.split('\n') if line])


class Test:

    def __init__(self, command=None, expected_result=None, envars=None, branch_name=None):
        logger.debug('executing Test constructor')
        self.command = command
        self.expected_result = expected_result
        self.envars = envars if envars else {}
        self.branch_name = branch_name if branch_name else 'main'
        self.actual_result = None
        self.passed = None

    def execute(self, client, repo_name, repo_dir):
        logger.debug(f"executing test for command '{self.command}'")
        run_command_kwargs = {
            'cwd': repo_dir
        }
        if self.envars:
            # update not replace current environment variables
            os_environ = dict(os.environ)
            os_environ.update(self.envars)
            run_command_kwargs['env'] = os_environ

        utils.run_command(f'git checkout {self.branch_name}', **run_command_kwargs)
        process = utils.run_command(self.command, **run_command_kwargs)

        remote_tag = None
        if self.expected_result.remote_tag:
            remote_tag = utils.get_head_tag(client, repo_name, self.branch_name)

        remote_version = None
        if self.expected_result.remote_version:
            remote_version = utils.read_file(client, repo_name, 'semver', self.branch_name)

        self.actual_result = Result(
            stdout=process.stdout,
            stderr=process.stderr,
            exit_code=process.returncode,
            remote_tag=remote_tag,
            remote_version=remote_version)

        self.passed = self.expected_result == self.actual_result
        if not self.passed:
            logger.error(f"test FAILED for command '{self.command}'")
            logger.debug(f"Actual:\n{self.actual_result}")
            logger.debug(f"Expected:\n{self.expected_result}")


class Suite:

    def __init__(self, path=None, keep_repo=None, setup_ssh=True, clone_repo=True):
        logger.debug('executing Suite constructor')

        self.keep_repo = keep_repo
        self.stream_handler = logs.add_stream_handler()

        if setup_ssh:
            self.ssh_setup()

        self.client = utils.get_client()
        repo = utils.create_repo(self.client)
        self.repo_name = repo['full_name']

        self.tests = []
        if path:
            self.tests = Suite.load_tests(path)
            branch_names = self.get_branch_names()
            for branch_name in branch_names:
                utils.create_branch(self.client, self.repo_name, branch_name)

        self.repo_dir = None
        if clone_repo:
            # clone repo after test branches have been created in test repo
            self.repo_dir = utils.clone_repo(repo['ssh_url'], repo['name'])

    def get_branch_names(self):
        branch_names = []
        for test in self.tests:
            if test.branch_name not in branch_names:
                branch_names.append(test.branch_name)
        if 'main' in branch_names:
            branch_names.remove('main')
        return branch_names

    def __del__(self):
        logger.debug('executing Suite destructor')
        if not self.keep_repo and hasattr(self, 'client') and hasattr(self, 'repo_name'):
            utils.delete_repo(self.client, self.repo_name)

    @staticmethod
    def load_tests(path):
        logger.info(f"Loading tests from path '{path}'")
        if not os.access(path, os.R_OK):
            raise ValueError(f"path '{path}' is not accessible")

        with open(path, 'r') as infile:
            json_data = json.loads(infile.read())

        tests = []
        for item in json_data:
            expected_result_kwargs = item.pop('expected_result')
            item.pop('actual_result', None)
            item.pop('passed', None)
            test = Test(**item)
            test.expected_result = Result(**expected_result_kwargs)
            tests.append(test)
        return tests

    def ssh_setup(self):
        logger.info('Setting up SSH')
        utils.run_command('eval `ssh-agent` && ssh-add', expected_exit_codes=[0], shell=True)
        utils.run_command('ssh -T git@github.com')

    def execute(self):
        logger.info(f'Executing {len(self.tests)} tests')
        logs.remove_stream_handler(self.stream_handler)
        with ProgressBar(total=len(self.tests), completed_message="Test execution complete", clear_alias=True) as pb:
            for index, test in enumerate(self.tests):
                test_number = index + 1
                pb.alias = f"Test{test_number}: {test.command}"
                test.execute(self.client, self.repo_name, self.repo_dir)
                pb.count += 1
        logs.add_stream_handler(stream_handler=self.stream_handler)

    def summary(self):
        passed = 0
        failed = 0
        for test in self.tests:
            if test.passed:
                passed += 1
            else:
                failed += 1
            # passed += 1 if test.passed else failed += 1
        if any(not test.passed for test in self.tests):
            print(f"{Style.BRIGHT + Fore.RED}Some Git Semver Tests FAILED{Style.RESET_ALL}")
        else:
            print(f"{Style.BRIGHT + Fore.GREEN}All Git Semver Tests PASSED{Style.RESET_ALL}")
        print(f'Total:{len(self.tests)} Passed:{passed} Failed:{failed}')
        with open('test-git-semver-results.json', 'w') as out_file:
            json.dump(self.tests, out_file, cls=TestEncoder, indent=4)

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
