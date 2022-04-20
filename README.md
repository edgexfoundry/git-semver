# test-git-semver
[![coverage](https://img.shields.io/badge/coverage-100.0%25-brightgreen)](https://pybuilder.io/)
[![complexity](https://img.shields.io/badge/complexity-Simple:%205-brightgreen)](https://radon.readthedocs.io/en/latest/api.html#module-radon.complexity)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![python](https://img.shields.io/badge/python-3.9-teal)](https://www.python.org/downloads/)

A Python script to execute git-semver functional tests.

## Installation
The easiest way to consume this module is through Docker by building and running the Docker image as described below.

## `test-git-semver`
```
 | |          | |             (_) |                                          
 | |_ ___  ___| |_ ______ __ _ _| |_ ______ ___  ___ _ __ _____   _____ _ __ 
 | __/ _ \/ __| __|______/ _` | | __|______/ __|/ _ \ '_ ` _ \ \ / / _ \ '__|
 | ||  __/\__ \ |_      | (_| | | |_       \__ \  __/ | | | | \ V /  __/ |   
  \__\___||___/\__|      \__, |_|\__|      |___/\___|_| |_| |_|\_/ \___|_|   
                          __/ |                                              
                         |___/       

usage: test-git-semver [-h] [--keep-repo]

A CLI to execute tests for git semver functionality.

optional arguments:
  -h, --help   show this help message and exit
  --keep-repo  do not delete test repo from GitHub after testing
```  

### Environment Variables

* `GH_TOKEN_PSW` - User GitHub authentication token

**Note**: the `http[s]_proxy` and `ALL_PROXY` environment variables referenced in the Docker commands below are only required if executing behind a proxy server

## Execution

Set the required environment variables:
```bash
export GH_TOKEN_PSW='--token--'
```

Build the Docker image:
```sh
docker image build \
--build-arg http_proxy \
--build-arg https_proxy \
-t \
test-git-semver:latest .
```

Execute the Docker container:
```bash
docker container run \
--rm \
-it \
-e ALL_PROXY=socks5://proxy-us.intel.com:1080 \
-e http_proxy \
-e https_proxy \
-e GH_TOKEN_PSW \
--entrypoint='' \
-v $HOME/.ssh:/root/.ssh \
test-git-semver:latest bash
```

## Development

Clone the repository and ensure the latest version of Docker is installed on your development server.

Build the Docker image:
```sh
docker image build \
--target build-image \
--build-arg http_proxy \
--build-arg https_proxy \
-t \
test-git-semver:latest .
```

Run the Docker container:
```sh
docker container run \
--rm \
-it \
-e http_proxy \
-e https_proxy \
-e GH_TOKEN_PSW \
-v $PWD:/code \
test-git-semver:latest bash
```

Execute the build:
```sh
pyb -X
```
