
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

import os
import sys
import time
import json
import base64
import secrets
import logging
import requests
import subprocess

from github3api import GitHubAPI

logger = logging.getLogger(__name__)


class GitSemverTest():

    def __init__(self, command, branch_name=None, stdout=None, stderr=None, exit_code=None, remote_tag=None, remote_version=None, envars=None):
        self.command = command
        self.branch_name = 'main' if not branch_name else branch_name
        self.envars = {} if not envars else envars
        # self.expected = Result(stdout, stderr, exit_code, remote_tag, remote_version)

    def execute(self):
        # execute the command and store the result
        process = run_command(self.command, env=self.envars)
        # remote_tag = get_remote_tag(self.branch_name)
        # remote_version = get_remote_version(self.branch_name)
        # self.actual = Result(process.stdout, process.stderr, process.exit_code, remote_tag, remote_version)
        # check the result
        self.check_result()

    def check_result(self):
        # check the result and compare to the expected_result
        # compare_results(self.actual.exit_code, self.expected.exit_code, 'exit code')
        pass

    def compare_results(actual, expected, test):
        if actual != expected:
            raise Exception(f'{test} did not macth')


def get_client():
    """ return instance of RESTclient for Github API
    """
    token = os.getenv('GH_TOKEN_PSW')
    if not token:
        raise Exception('GH_TOKEN_PSW environment variable must be set')
    return GitHubAPI(
        bearer_token=token)


def create_repo(client):
    repo_name = 'tgsver-' + time.strftime('%m-%d-%Y-%H-%M-%S')
    response = client.post('/user/repos', json={'name': repo_name, 'auto_init': True})
    return response['full_name']


def delete_repo(client, repo_name):
    if client and repo_name:
        client.delete(f'/repos/{repo_name}')


def create_branch(client, repo_name):
    branches = client.get(f'/repos/{repo_name}/git/refs/heads')
    client.post(
        f'/repos/{repo_name}/git/refs',
        json={
            'ref': 'refs/heads/branch1',
            'sha': branches[-1]['object']['sha']
        })


def remove_branch(client, repo_name, branch_name):
    client.delete(f'/repos/{repo_name}/git/refs/heads/{branch_name}')


def branch_exists(client, repo_name, branch_name):
    branches = client.get(f'/repos/{repo_name}/branches')
    for branch in branches:
        if branch['name'] == branch_name:
            return True
    return False


def get_file_url(client, repo_name, branch_name, file_name):
    results = client.get(f'/repos/{repo_name}/git/trees/{branch_name}?recursive=1')
    for result in results['tree']:
        if result['path'] == file_name:
            return result['url']


def read_file(client, repo_name, branch_name, file_name):
    file_url = get_file_url(client, repo_name, branch_name, file_name)
    results = client.get(file_url)
    content = results['content']
    content_encoding = results.get('encoding')
    if content_encoding == 'base64':
        content = base64.b64decode(content).decode()
    return content


def is_head_tagged(client, repo_name, branch_name):
    latest_commit_sha = client.get(f'/repos/{repo_name}/commits/{branch_name}')['sha']
    tags = client.get(f'/repos/{repo_name}/tags')
    for tag in tags:
        if tag['commit']['sha'] == latest_commit_sha:
            return True
    return False


def get_head_tag(client, repo_name, branch_name):
    latest_commit_sha = client.get(f'/repos/{repo_name}/commits/{branch_name}')['sha']
    tags = client.get(f'/repos/{repo_name}/tags')
    for tag in tags:
        if tag['commit']['sha'] == latest_commit_sha:
            return tag['name']


def setup(repo_name):
    # run_command(f'git clone {repo_name}')
    # run_command('chown root:root /root/.ssh/config'
    # run_command('eval `ssh-agent`')
    # run_command('ssh-add')
    # run_command('ssh -T git@github.com')
    # run_command(f'cd {repo_name}')
    pass


def load_tests():
    pass


def execute_tests(tests):
    pass


def write_summary(results):
    pass


def run_command(command, noop=True, **kwargs):
    """ run command
    """
    logger.debug(f'run command: {command}')
    if not noop:
        process = subprocess.run(command.split(' '))
        logger.debug(f"return code: {process.returncode}")
        if process.stdout:
            logger.debug(f'stdout:\n{process.stdout}')
        if process.stderr:
            logger.debug(f'stderr:\n{process.stderr}')
        return process
    else:
        time.sleep(get_random())
        logger.debug("return code: 0")


def get_random():
    """ return random float
    """
    choices = [round(number * .05, 2) for number in range(20) if number > 0]
    return secrets.choice(choices)


def setup_logging():
    """ configure logging and create logfile if specified
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    name = os.path.basename(sys.argv[0])
    file_handler = logging.FileHandler(f'{name}.log')
    file_formatter = logging.Formatter("%(asctime)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)


def main():
    """ main function
    """
    setup_logging()
    client = None
    repo_name = None
    try:
        client = get_client()
        repo_name = create_repo(client)
        create_branch(client, repo_name)
        setup(repo_name)
        tests = load_tests()
        results = execute_tests(tests)
        write_summary(results)

    except Exception as exception:
        logger.error(exception)
        print(f'ERROR: {exception}')
        sys.exit(1)

    finally:
        # delete_repo(client, repo_name)
        pass


if __name__ == '__main__':
    main()
