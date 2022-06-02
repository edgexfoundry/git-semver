
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

import logging
from git import Repo

logger = logging.getLogger(__name__)


def run_push(repo, settings=None):
    """ git semver push
    """
    logger.debug('push')
    semver_path = settings['semver_path']
    semver_repo = Repo(semver_path)
    semver_remote_name = settings['semver_remote_name']

    # pull remote if it has changed
    local_commits = [commit.hexsha for commit in list(semver_repo.iter_commits())]
    latest_remote_commit = semver_repo.remotes[semver_remote_name].fetch()[0].commit.hexsha
    if latest_remote_commit not in local_commits:
        logger.debug('remote changes detected')
        logger.debug(f'latest remote commit {latest_remote_commit} is not in local commits')
        logger.debug('integrating remote changes with a git pull')
        semver_repo.git.pull(semver_remote_name, 'semver')
    else:
        logger.debug('no remote changes detected')

    semver_repo.git.push(semver_remote_name, 'semver')

    logger.debug('push all version tags')
    repo.git.push(semver_remote_name, 'refs/tags/v*:refs/tags/v*')
