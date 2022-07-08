
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
import shutil
import logging
import semver
from git import Repo
from git import Head
from git import Actor
from git.exc import InvalidGitRepositoryError
from pygsver.utils import write_file
from pygsver.utils import write_version
from pygsver.utils import append_file
from pygsver.errors import InvalidPathError
from pygsver.errors import InvalidBranchError
from pygsver.errors import InvalidRepoError

logger = logging.getLogger(__name__)


def remove_entries(index, keep):
    """ removes all entries in index except those specified in keep
    """
    to_remove = []
    for key, value in index.entries.items():
        name = key[0]
        if name not in keep:
            if name not in to_remove:
                to_remove.append(name)
    if to_remove:
        logger.debug(f'removing {to_remove}')
        index.remove(to_remove)


def remove_semver_folder(semver_path):
    """ remove semver folder only if folder is associated with semver branch
    """
    if not os.path.exists(semver_path):
        return
    if os.path.isfile(semver_path):
        raise InvalidPathError(f'the path {semver_path} is a file')
    try:
        semver_repo = Repo(semver_path)
        if 'semver' not in semver_repo.remote().refs:
            raise InvalidBranchError(f'the path {semver_path} is not a valid semver branch')
    except InvalidGitRepositoryError:
        raise InvalidRepoError(f'the path {semver_path} is not a valid repo')
    # if existing .semver folder represents a valid semver repo/branch then we
    # can safely remove it so it can be cloned from remote anew
    logger.debug(f'remove {semver_path} directory and its contents')
    shutil.rmtree(semver_path, ignore_errors=True)


def clone_semver_branch(repo, semver_path, semver_remote_name):
    """ clone semver path
    """
    logger.debug(f'clone semver branch to:{semver_path}')
    repo_url = repo.config_reader().get_value(f'remote "{semver_remote_name}"', 'url')
    repo.git.clone('-b', 'semver', repo_url, semver_path)
    # exclude .semver directory
    append_file(os.path.join(repo.git_dir, 'info', 'exclude'), '\n.semver\n')


def create_semver_branch(repo, version, settings):
    """ create semver branch
    """
    logger.debug('create semver branch')
    # using GitPython object model to facilitate creation of semver orphan branch
    # allows specification of an author and committer at the commit level
    repo.head.reference = Head(repo, 'refs/heads/semver')
    index = repo.index
    remove_entries(index, [])
    semver_branch = settings['semver_branch']
    write_file(semver_branch, version)
    index.add([semver_branch])
    semver_user_name = settings['semver_user_name']
    semver_user_email = settings['semver_user_email']
    author = Actor(semver_user_name, semver_user_email)
    index.commit(f'semver({semver_branch}): {version}', author=author, committer=author, parent_commits=None)
    origin = repo.remotes.origin
    origin.push('semver')
    # reverting back to using git commands to go back to the main branch and remove the semver branch
    # removing the local semver branch allows it to be cloned to the .semver folder later
    repo.git.checkout(semver_branch, '-f')
    repo.git.branch('-D', 'semver')

    # exclude .semver directory
    append_file(os.path.join(repo.git_dir, 'info', 'exclude'), '\n.semver\n')


def run_init(repo, version=None, force=None, settings=None):
    """ git semver init
    """
    logger.debug(f'init version:{version} force:{force}')
    # verify version is valid
    semver.VersionInfo.parse(version)

    semver_path = settings['semver_path']
    remove_semver_folder(semver_path)

    if 'semver' not in repo.remote().refs:
        create_semver_branch(repo, version, settings)

    semver_remote_name = settings['semver_remote_name']
    clone_semver_branch(repo, semver_path, semver_remote_name)

    write_version(settings, version, force=force)
