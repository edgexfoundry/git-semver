
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

import sys
import logging
import tgsver.logs as logs
import tgsver.test as test
from argparse import ArgumentParser

logger = logging.getLogger(__name__)


def get_parser():
    """ setup parser and return parsed command line arguments
    """
    parser = ArgumentParser(
        description='A CLI to execute tests for git semver functionality.')
    parser.add_argument(
        '--keep_repo',
        dest='keep_repo',
        action='store_true',
        help='does not delete test repo from GitHub after testing')
    return parser


def main():
    """ main function
    """
    logs.setup_logging()
    parser = get_parser()
    suite = None
    try:
        args = parser.parse_args()
        suite = test.Suite(path='tests.json', keep_repo=args.keep_repo)
        suite.execute()
        suite.summary()

    except Exception as exception:
        logger.error(exception)
        sys.exit(1)

    finally:
        if suite is not None:
            del suite


if __name__ == '__main__':
    main()
