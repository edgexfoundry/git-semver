
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
import argparse
import logging
from git import Repo
from pygsver.init import run_init
from pygsver.tag import run_tag
from pygsver.bump import run_bump
from pygsver.push import run_push
from pygsver.utils import read_version


logger = logging.getLogger(__name__)


def get_parser():
    """ return argument parser
    """
    parser = argparse.ArgumentParser(
        description='A Python script that manages semantic versioning of a git repository')
    subparser = parser.add_subparsers(dest='command')

    init = subparser.add_parser(
        'init',
        help='set the initial semantic version')
    init.set_defaults(subcmd=run_init)
    init.add_argument(
        '--version',
        dest='version',
        default='0.0.0',
        type=str,
        help='a specific semantic version to set as the initial')
    init.add_argument(
        '--force',
        dest='force',
        action='store_true',
        help='force set the semantic version - required if a semantic version is already set')

    tag = subparser.add_parser(
        'tag',
        help="create tag at HEAD of the current branch with the current semantic version prefixed with 'v'")
    tag.set_defaults(subcmd=run_tag)
    tag.add_argument(
        '--force',
        dest='force',
        action='store_true',
        help='force set the tag - required if HEAD on the current branch is already tagged')

    bump = subparser.add_parser(
        'bump',
        help='increment the current semantic version')
    bump.set_defaults(subcmd=run_bump)
    bump_subparser = bump.add_subparsers(
        dest='axis',
        required=True)

    major = bump_subparser.add_parser(
        'major',
        help='increment the MAJOR version')

    minor = bump_subparser.add_parser(
        'minor',
        help='increment the MINOR version')

    patch = bump_subparser.add_parser(
        'patch',
        help='increment the PATCH version')

    final = bump_subparser.add_parser(
        'final',
        help='increment the FINAL version')

    pre = bump_subparser.add_parser(
        'pre',
        help='increment the PRERELEASE version')
    pre.add_argument(
        '--prefix',
        dest='prefix',
        type=str,
        default=os.getenv('SEMVER_PRE_PREFIX', 'pre'),
        help='specify the PRERELEASE prefix')

    push = subparser.add_parser(
        'push',
        help='push the semver branch commits and all version tags set on the current branch to the remote')
    push.set_defaults(subcmd=run_push)
    return parser


def configure_logging():
    """ configure logging and logfile
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    name = os.path.basename(sys.argv[0])
    file_handler = logging.FileHandler(f"{os.getenv('HOME')}/{name}.log")
    file_formatter = logging.Formatter("%(asctime)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    if is_true(os.getenv('SEMVER_DEBUG', '')):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(file_formatter)
        root_logger.addHandler(stream_handler)


def is_true(value):
    """ return True if value is truey otherwise return False
    """
    return value.lower() in ['true', '1', 'yes', 'on']


def get_settings():
    """ return git semver settings
    """
    return {
        'semver_branch': os.getenv('SEMVER_BRANCH', os.getenv('GIT_BRANCH', os.getenv('BRANCH_NAME'))),
        'semver_remote_name': os.getenv('SEMVER_REMOTE_NAME'),
        'semver_user_name': os.getenv('SEMVER_USER_NAME', os.getenv('GIT_AUTHOR_NAME', os.getenv('GIT_COMMITTER_NAME', 'semver'))),
        'semver_user_email': os.getenv('SEMVER_USER_EMAIL', os.getenv('GIT_AUTHOR_EMAIL', os.getenv('GIT_COMMITTER_EMAIL', 'semver@semver.org'))),
        'semver_path': f'{os.getcwd()}/.semver',
    }


def update_settings(repo, settings):
    """ update settings from repo properties
    """
    if not settings['semver_branch']:
        settings['semver_branch'] = repo.active_branch.name
    if not settings['semver_remote_name']:
        settings['semver_remote_name'] = repo.remote().name


def run_command(options, settings):
    """ run git-semver command
    """
    repo = Repo(os.getcwd())
    repo.config_writer().set_value('user', 'name', settings['semver_user_name']).release()
    repo.config_writer().set_value('user', 'email', settings['semver_user_email']).release()
    update_settings(repo, settings)

    command = options.pop('command', None)
    if command:
        subcmd = options.pop('subcmd', None)
        options['settings'] = settings
        subcmd(repo, **options)

    version = read_version(settings)
    print(version)


def main():
    """ main function
    """
    args = get_parser().parse_args()
    configure_logging()

    try:
        settings = get_settings()
        run_command(vars(args), settings)

    except Exception as exception:
        logger.error(exception)
        print(f'ERROR: {exception}')
        sys.exit(1)


if __name__ == '__main__':  # pragma: no cover

    main()
