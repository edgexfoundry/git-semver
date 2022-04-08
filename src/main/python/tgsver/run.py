
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

import shlex
import subprocess
import logging

logger = logging.getLogger(__name__)


def run_command(command, expected_exit_codes=None, **kwargs):
    """ run the specified command using subprocess run
        any additional key word arguments provided will be passed along to the subprocess run method
        if expected_exit_codes are provided the return code of the process that is invoked will
        be checked and an Exception will be raised if the process return code is not in the
        expected_exit_codes
    """
    logger.debug(f"running command '{command}'")
    process = subprocess.run(shlex.split(command, posix=True), capture_output=True, text=True, **kwargs)
    logger.debug(f"return code: {process.returncode}")
    if process.stdout:
        logger.debug(f'stdout:\n{process.stdout}')
    if process.stderr:
        logger.debug(f'stderr:\n{process.stderr}')
    if expected_exit_codes and process.returncode not in expected_exit_codes:
        raise Exception(f"command '{command}' did not execute successfully")
    return process
