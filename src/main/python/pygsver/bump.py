
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
from pygsver.utils import write_version
from pygsver.errors import PrereleaseMismatchError

logger = logging.getLogger(__name__)


def check_prerelease(semver_prerelease, prefix):
    """ raise exception if semver_prerelease prefix is different than prefix
    """
    if semver_prerelease and prefix:
        semver_prefix = semver_prerelease.split('.')[0]
        if semver_prefix.lower() != prefix.lower():
            raise PrereleaseMismatchError(f'mismatch between current prerelease {semver_prefix} and bump {prefix} - use init to set version with different prerelease')


def run_bump(repo, axis=None, prefix=None, settings=None):
    """ git semver bump
    """
    logger.debug(f'bump axis:{axis} prefix:{prefix}')
    version = read_version(settings)
    semver_version = semver.VersionInfo.parse(version)
    if axis == 'pre' and prefix:
        check_prerelease(semver_version.prerelease, prefix)
        semver_version = semver_version.bump_prerelease(token=prefix)
    elif axis == 'final':
        semver_version = semver_version.finalize_version()
    else:
        semver_version = getattr(semver_version, f'bump_{axis}')()
    write_version(settings, str(semver_version), force=True)
