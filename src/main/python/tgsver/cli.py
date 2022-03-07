
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
import logging
from github3api import GitHubAPI

logger = logging.getLogger(__name__)

def get_client():
    """ return instance of RESTclient for Github API
    """
    token = getenv('GH_TOKEN')
    return GitHubAPI(bearer_token=token)

def create_test_repo(client):
    client.post('/jaron-bauers/repos', json={'name': 'test-repo1'})['SWAAAAAAAAAAAG']

def main():
    """ main function
    """
    try:
        client = get_client()
        create_test_repo(client)

    except Exception as exception:
        logger.error(exception)
        print(f'ERROR: {exception}')
        sys.exit(1)

if __name__ == '__main__':  # pragma: no cover

    main()