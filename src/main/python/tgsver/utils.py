
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
import time
import base64
import secrets
import subprocess
import logging

from github3api import GitHubAPI

logger = logging.getLogger(__name__)


def get_client():
    """ return instance of RESTclient for Github API
    """
    logger.debug('getting github API client')
    token = os.getenv('GH_TOKEN_PSW')
    if not token:
        raise Exception('GH_TOKEN_PSW environment variable must be set')
    return GitHubAPI(bearer_token=token)


def create_repo(client):
    repo_name = 'test-git-semver-' + time.strftime('%m-%d-%Y-%H-%M-%S')
    logger.info(f"Creating GitHub repository '{repo_name}'")
    response = client.post('/user/repos', json={'name': repo_name, 'auto_init': True})
    return response


def delete_repo(client, repo_name):
    logger.info(f"Deleting GitHub repository '{repo_name}'")
    if client and repo_name:
        client.delete(f'/repos/{repo_name}')


def create_branch(client, repo_name):
    logger.debug(f"creating branch 'branch1' in repository '{repo_name}'")
    branches = client.get(f'/repos/{repo_name}/git/refs/heads')
    client.post(
        f'/repos/{repo_name}/git/refs',
        json={
            'ref': 'refs/heads/branch1',
            'sha': branches[-1]['object']['sha']
        })


def remove_branch(client, repo_name, branch_name):
    """ removes branch from github repository
    """
    logger.debug(f"removing branch '{branch_name}' from repository '{repo_name}'")
    client.delete(f'/repos/{repo_name}/git/refs/heads/{branch_name}')


def branch_exists(client, repo_name, branch_name):
    logger.debug(f"checking if branch '{branch_name} 'exists in repository '{repo_name}'")
    branches = client.get(f'/repos/{repo_name}/branches')
    for branch in branches:
        if branch['name'] == branch_name:
            return True
    return False


def get_file_url(client, repo_name, branch_name, file_name):
    logger.debug(f"retrieving '{file_name}' url from repository '{repo_name}' branch '{branch_name}'")
    if branch_exists(client, repo_name, branch_name):
        results = client.get(f'/repos/{repo_name}/git/trees/{branch_name}?recursive=1')
        for result in results['tree']:
            if result['path'] == file_name:
                return result['url']
        logger.debug(f"the file '{file_name}' does not exist in branch '{branch_name}' in repo '{repo_name}'")
    else:
        logger.debug(f"the branch '{branch_name}' does not exist in repo '{repo_name}'")


def read_file(client, repo_name, branch_name, file_name):
    logger.debug(f"reading content from file '{file_name}' in repository '{repo_name}' branch '{branch_name}'")
    file_url = get_file_url(client, repo_name, branch_name, file_name)
    if file_url:
        results = client.get(file_url)
        content = results['content']
        content_encoding = results.get('encoding')
        if content_encoding == 'base64':
            content = base64.b64decode(content).decode()
            return content.strip()


def is_head_tagged(client, repo_name, branch_name):
    logger.debug(f"checking if head in repository '{repo_name}' branch '{branch_name}' is tagged")
    latest_commit_sha = client.get(f'/repos/{repo_name}/commits/{branch_name}')['sha']
    tags = client.get(f'/repos/{repo_name}/tags')
    for tag in tags:
        if tag['commit']['sha'] == latest_commit_sha:
            return True
    return False


def get_head_tag(client, repo_name, branch_name):
    logger.debug(f"retrieving head tag from repository '{repo_name}' branch '{branch_name}'")
    latest_commit_sha = client.get(f'/repos/{repo_name}/commits/{branch_name}')['sha']
    tags = client.get(f'/repos/{repo_name}/tags')
    for tag in tags:
        if tag['commit']['sha'] == latest_commit_sha:
            return tag['name']


def run_command(command, raise_if_error=False, **kwargs):
    """ run command
    """
    logger.debug(f"running command '{command}'")
    process = subprocess.run(command.split(' '), capture_output=True, text=True, **kwargs)
    logger.debug(f"return code: {process.returncode}")
    if process.stdout:
        logger.debug(f'stdout:\n{process.stdout}')
    if process.stderr:
        logger.debug(f'stderr:\n{process.stderr}')
    if raise_if_error and process.returncode != 0:
        raise Exception(f"command '{command}' did not execute successfully")
    return process


def clone_repo(ssh_url, repo_name):
    logger.info(f"Cloning repo '{ssh_url}' to directory '{repo_name}'")
    run_command(f'git clone {ssh_url} {repo_name}', raise_if_error=True)
    return repo_name
