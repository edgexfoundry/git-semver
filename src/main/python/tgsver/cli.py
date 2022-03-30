
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
import logging

from tgsver.test import Suite

logger = logging.getLogger(__name__)


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


def setup_logging():
    """ configure logging and create logfile if specified
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    name = os.path.basename(sys.argv[0])
    file_handler = logging.FileHandler(f'{name}.log')
    file_formatter = logging.Formatter("%(asctime)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)


def main():
    """ main function
    """
    setup_logging()
    suite = None
    try:
        suite = Suite(path='tests.json')
        suite.execute()
        suite.summary()

    except Exception as exception:
        logger.error(exception)
        print(f'ERROR: {exception}')
        sys.exit(1)

    finally:
        if suite is not None:
            del suite


if __name__ == '__main__':
    main()
