
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
import semver
from pygsver.utils import read_version
from pygsver.errors import HeadTaggedError

logger = logging.getLogger(__name__)


def get_head_tags(repo):
    """ return names of head tags
    """
    return [tag.name for tag in repo.tags if tag.commit == repo.head.commit]


def check_head_tag(repo, force):
    """ raise exception if head is tagged with a semver version
    """
    logger.debug('check head tag')
    if force:
        return
    head_tags = get_head_tags(repo)
    for head_tag in head_tags:
        head_tag_name = head_tag[1:]
        logger.debug(f'checking if {head_tag_name} is a valid semver version')
        if semver.VersionInfo.isvalid(head_tag_name):
            raise HeadTaggedError(f'head {repo.head.commit} is already tagged with {head_tag_name}')


def run_tag(repo, force=None, settings=None):
    """ git semver tag
    """
    logger.debug(f'tag force:{force}')
    check_head_tag(repo, force)
    version = read_version(settings)
    tag = f'v{version}'
    tag_args = ['-a', tag, '-m', tag]
    if force:
        tag_args.append('-f')
    repo.git.tag(*tag_args)
