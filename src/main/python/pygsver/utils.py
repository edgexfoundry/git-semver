
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
import logging
from git import Repo
from git import Actor
from pygsver.errors import BranchDoesNotExistError
from pygsver.errors import EmptyVersionError

logger = logging.getLogger(__name__)


def read_file(file_path):
    """ return contents of file read from file_path
    """
    with open(file_path, 'r') as infile:
        return infile.read()


def read_version(settings):
    """ read version
    """
    semver_path = settings['semver_path']
    filename = settings['semver_branch']
    path = os.path.join(semver_path, filename)
    if not os.path.exists(path):
        raise BranchDoesNotExistError('the semver branch does not exist')
    logger.debug(f'read version from {path}')
    version = read_file(path)
    if not version:
        raise EmptyVersionError(f'the version file {filename} in the semver branch is empty')
    return version.strip()


def write_file(file_path, contents):
    """ create file at file_path with contents
    """
    logger.debug(f'write to file:{file_path}')
    with open(file_path, 'w') as outfile:
        outfile.write(contents)


def write_version(settings, version, force=False):
    """ write version
            if version file does not exist then write version to version file
            if force is set then write version to version file
    """
    semver_path = settings['semver_path']
    filename = settings['semver_branch']
    path = os.path.join(semver_path, filename)
    logger.debug(f'write version:{version} to path:{path} with force:{force}')

    path_exists = os.path.exists(path)
    if path_exists:
        current_version = read_version(settings)
        if current_version == version:
            logger.debug(f'version is same as current version {current_version}')
            return

    if not path_exists or force:
        write_file(path, version)
        semver_repo = Repo(semver_path)
        index = semver_repo.index
        index.add([filename])
        semver_user_name = settings['semver_user_name']
        semver_user_email = settings['semver_user_email']
        author = Actor(semver_user_name, semver_user_email)
        index.commit(f'semver({filename}): {version}', author=author, committer=author, parent_commits=None)


def append_file(file_path, contents):
    """ append contents to file located at file_path
    """
    logger.debug(f'append to file:{file_path}')
    with open(file_path, 'r+') as outfile:
        for line in outfile:
            if contents.strip() in line:
                break
        else:
            outfile.write(contents)
