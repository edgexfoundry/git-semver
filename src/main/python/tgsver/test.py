
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
from colorama import Style
from colorama import Fore
import tgsver.github as github
import tgsver.run as run
import tgsver.log as log
from progress1bar import ProgressBar

logger = logging.getLogger(__name__)


class Result:
    """  represents a Test Result object
    """
    def __init__(self, stdout=None, stderr=None, exit_code=None, remote_tag=None, remote_version=None):
        """ Result constructor
        """
        logger.debug('executing Result constructor')
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code if exit_code else 0
        self.remote_tag = remote_tag
        self.remote_version = remote_version

    def __eq__(self, other):
        """ allows equality comparisons between two Result objects
        """
        return (
            Result.check(self.exit_code, other.exit_code, 'exit_code')
            and Result.check(self.remote_tag, other.remote_tag, 'remote_tag')
            and Result.check(self.remote_version, other.remote_version, 'remote_version')
            and Result.check(self.stdout, other.stdout, 'stdout')
            and Result.check(self.stderr, other.stderr, 'stderr'))

    @staticmethod
    def check(value1, value2, attr):
        """ custom comparison method to check if the provided two values are equal
        """
        if not value1:
            result = True
        elif not value2:
            result = False
        elif isinstance(value1, int):
            result = value1 == value2
        else:
            result = value1 in value2
        if not result:
            logger.error(f"check values for attribute '{attr}' failed - value1:{value1} - value2:{value2}")
        return result

    def __str__(self):
        """ represent Result object as a string
        """
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
    """  represents a Test object
    """
    def __init__(self, command=None, expected_result=None, envars=None, branch_name=None):
        """ Test constructor
        """
        logger.debug('executing Test constructor')
        self.command = command
        self.expected_result = expected_result
        self.envars = envars if envars else {}
        # assumes main is the default branch
        self.branch_name = branch_name if branch_name else 'main'
        self.actual_result = None
        self.passed = None

    def get_run_command_kwargs(self, repo_dir):
        run_command_kwargs = {
            'cwd': repo_dir
        }
        if self.envars:
            # update not replace current environment variables
            os_environ = dict(os.environ)
            os_environ.update(self.envars)
            run_command_kwargs['env'] = os_environ
        return run_command_kwargs

    def execute(self, client, repo_name, repo_dir):
        """ execute the test
        """
        logger.debug(f"executing test for command '{self.command}'")
        run_command_kwargs = self.get_run_command_kwargs(repo_dir)

        # ensure the correct branch is checked out
        run.run_command(f'git checkout {self.branch_name}', **run_command_kwargs)
        if self.command == 'create-a-commit':
            # special test directive to create an empty commit
            run.run_command("git commit --allow-empty -m 'empty commit'", cwd=repo_dir)
            process = run.run_command(f'git push origin {self.branch_name}', cwd=repo_dir)
        else:
            process = run.run_command(self.command, **run_command_kwargs)

        actual_result_kwargs = {
            'stdout': process.stdout,
            'stderr': process.stderr,
            'exit_code': process.returncode
        }
        if self.expected_result.remote_tag:
            actual_result_kwargs['remote_tag'] = github.get_head_tag(client, repo_name, self.branch_name)
        if self.expected_result.remote_version:
            actual_result_kwargs['remote_version'] = github.read_file(client, repo_name, 'semver', self.branch_name)
        self.actual_result = Result(**actual_result_kwargs)

        self.passed = self.expected_result == self.actual_result
        if not self.passed:
            logger.error(f"Failed for command '{self.command}'")
            logger.debug(f"Actual:\n{self.actual_result}")
            logger.debug(f"Expected:\n{self.expected_result}")


class Suite:
    """  represents a Test Suite object
    """
    def __init__(self, path=None, keep_repo=False, setup_ssh=True, clone_repo=True):
        """ Suite constructor
        """
        logger.debug('executing Suite constructor')

        self.keep_repo = keep_repo
        self.stream_handler = log.add_stream_handler()

        if setup_ssh:
            self.ssh_setup()

        self.client = github.get_client()
        repo = github.create_repo(self.client)
        self.repo_name = repo['full_name']

        self.tests = []
        if path:
            self.tests = Suite.load_tests(path)
            # create all branches in repo required by tests
            branch_names = self.get_branch_names()
            for branch_name in branch_names:
                github.create_branch(self.client, self.repo_name, branch_name)

        self.repo_dir = None
        if clone_repo:
            # clone repo after test branches have been created in test repo
            self.repo_dir = github.clone_repo(repo['ssh_url'], repo['name'])

    def get_branch_names(self):
        """ find and return all branch names found in tests
            remove 'main' from the returned list
        """
        branch_names = []
        for test in self.tests:
            if test.branch_name not in branch_names:
                branch_names.append(test.branch_name)
        # todo: instead of main should be default branch
        if 'main' in branch_names:
            branch_names.remove('main')
        return branch_names

    def __del__(self):
        """ Suite destructor method
            delete the GitHub repo
        """
        logger.debug('executing Suite destructor')
        if not self.keep_repo and hasattr(self, 'client') and hasattr(self, 'repo_name'):
            github.delete_repo(self.client, self.repo_name)

    @staticmethod
    def load_tests(path):
        """ convert data read in from path into list of Test objects and return list
        """
        logger.info(f"Loading tests from path '{path}'")
        if not os.access(path, os.R_OK):
            raise ValueError(f"path '{path}' is not accessible")

        with open(path, 'r') as infile:
            data = json.loads(infile.read())

        tests = []
        for item in data:
            expected_result_kwargs = item.pop('expected_result', {})
            item.pop('actual_result', None)
            item.pop('passed', None)
            test = Test(**item)
            test.expected_result = Result(**expected_result_kwargs)
            tests.append(test)
        return tests

    def ssh_setup(self):
        """ setup ssh
        """
        logger.info('Setting up SSH')
        run.run_command('eval `ssh-agent` && ssh-add', expected_exit_codes=[0], shell=True)
        run.run_command('ssh -T git@github.com')

    def execute(self):
        """ execute Suite tests
        """
        logger.info(f'Executing {len(self.tests)} tests')
        log.remove_stream_handler(self.stream_handler)
        with ProgressBar(total=len(self.tests), completed_message="Test execution complete", clear_alias=True) as pb:
            for index, test in enumerate(self.tests):
                test_number = index + 1
                pb.alias = f"Test{test_number}: {test.command}"
                test.execute(self.client, self.repo_name, self.repo_dir)
                pb.count += 1
        log.add_stream_handler(stream_handler=self.stream_handler)

    def summary(self):
        """ determine and print test summary to screen and write test results to JSON file
        """
        passed = 0
        failed = 0
        for test in self.tests:
            if test.passed:
                passed += 1
            else:
                failed += 1
        # print summary to screen
        if failed:
            print(f"{Style.BRIGHT + Fore.RED}Some Git Semver Tests FAILED{Style.RESET_ALL}")
        else:
            print(f"{Style.BRIGHT + Fore.GREEN}All Git Semver Tests PASSED{Style.RESET_ALL}")
        print(f'Total:{len(self.tests)} Passed:{passed} Failed:{failed}')
        # write results to json file
        with open('test-git-semver-results.json', 'w') as out_file:
            json.dump(self.tests, out_file, cls=TestEncoder, indent=4)


class TestEncoder(json.JSONEncoder):
    """ JSONEncoder class that enables test data to be serialized
    """
    def default(self, obj):
        return obj.__dict__  # pragma: no cover
