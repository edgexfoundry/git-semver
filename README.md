## py-git-semver
[![coverage](https://img.shields.io/badge/coverage-100.0%25-brightgreen)](https://pybuilder.io/)
[![complexity](https://img.shields.io/badge/complexity-Simple:%205-brightgreen)](https://radon.readthedocs.io/en/latest/api.html#module-radon.complexity)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![python](https://img.shields.io/badge/python-3.9-teal)](https://www.python.org/downloads/)

A Python script that manages semantic versioning of a git repository. This is a port of [git-semver](https://github.com/edgexfoundry/git-semver) to Python.

The script leverages the following Python modules/libraries:
* [GitPython](https://pypi.org/project/GitPython/) A Python library used to interact with Git repositories.
* [semver](https://pypi.org/project/semver/) A Python module for semantic versioning.

#### Motivation
* conform to a scripting language that aligns better with current DevOps skillset
* because `git semver` is a key DevOps capability it **must** be implemented using best-known software development practices:
  * ensure a high-degree of unit test coverage
  * ensure code complexity is low to facilitate quick rampup of new DevOps team members
  * ensure it is free from common security issues
  * maintain a thoroughly documented API
  * include a robust build pipeline to continuously ensure code quality standards are maintained on every commit
  * maintain a high-degree of developer confidence to facilitate future development or code refactoring
* provide opportunity to migrate complexities from current `edgeXSemver` Jenkins Shared Library

#### Remaining Effort
* ensure 100% backwards compatability with:
  * current Golang-based git-semver command line arguments
  * current environment variable API
* execute extensive functional testing
  * build pipelines
  * release pipelines

## Execution
The primary way that `git-semver` is consumed within a EdgeXFoundry Jenkins Pipeline is via the [edgex-global-pipelines](https://github.com/edgexfoundry/edgex-global-pipelines) `edgeXSemver` function.  The steps to execute locally are described here for testing purposes only.

Clone the repository you wish to version into your current working directory and cd into it; in the example below it is bind mounted to `repo` in the container.

Run container from `py-git-semver` Nexus image - requires host to have a valid github ssh key - if behind a proxy, ensure the specified proxies are provided:
```
docker container run \
  --rm \
  -it \
  -e ALL_PROXY=[SOCKS_PROXY]  \
  -e http_proxy \
  -e https_proxy \
  -e LOCAL_UID=$(id -u $USER) \
  -e LOCAL_GID=$(id -g $USER) \
  -v $PWD:/repo \
  -v $HOME/.ssh:/home/user/.ssh \
  nexus3.edgexfoundry.org:10003/edgex-devops/py-git-semver:latest \
  bash
```

Verify SSH inside the container:
```
eval `ssh-agent`
ssh-add
ssh -T git@github.com
```

Typical execution flow:
```
export SEMVER_PRE_PREFIX=dev
git semver init --version=0.1.0-dev.1
git semver tag
git semver bump pre
git semver push
git semver
```

## Installation
For those wishing to install the Python package directly may do so via:
```
pip install git+https://github.com/edgexfoundry/git-semver.git@python
```

## CLI Usage

### `git semver`
```
usage: git-semver [-h] {init,tag,bump,push} ...

A Python script that manages semantic versioning of a git repository

positional arguments:
  {init,tag,bump,push}
    init                set the initial semantic version
    tag                 create tag at HEAD of the current branch with the current semantic version prefixed with 'v'
    bump                increment the current semantic version
    push                push the semver branch commits and all version tags set on the current branch to the remote

optional arguments:
  -h, --help            show this help message and exit
```

### `git semver init`
```
usage: git-semver init [-h] [--version VERSION] [--force]
  set the initial semantic version

optional arguments:
  -h, --help         show this help message and exit
  --version VERSION  a specific semantic version to set as the initial
  --force            force set the semantic version - required if a semantic version is already set
```

### `git semver tag`
```
usage: git-semver tag [-h] [--force]
  create tag at HEAD of the current branch with the current semantic version prefixed with 'v'

optional arguments:
  -h, --help  show this help message and exit
  --force     force set the tag - required if HEAD on the current branch is already tagged
```

### `git semver bump`
```
usage: git-semver bump [-h] {major,minor,patch,final,pre} ...
  increment the current semantic version

positional arguments:
  {major,minor,patch,final,pre}
    major               increment the MAJOR version
    minor               increment the MINOR version
    patch               increment the PATCH version
    final               increment the FINAL version
    pre                 increment the PRERELEASE version

optional arguments:
  -h, --help            show this help message and exit
```

### `git semver bump pre`
```
usage: git-semver bump pre [-h] [--prefix PREFIX]
  increment the PRERELEASE version

optional arguments:
  -h, --help       show this help message and exit
  --prefix PREFIX  specify the PRERELEASE prefix
```

### `git semver push`
```
usage: git-semver push [-h]
  push the semver branch commits and all version tags set on the current branch to the remote

optional arguments:
  -h, --help  show this help message and exit
```

## Development

Build image:
```
docker image build \
  --target build-image \
  --build-arg http_proxy \
  --build-arg https_proxy \
  -t \
  py-git-semver:latest .
```

Run container:
```
docker container run \
  --rm \
  -it \
  -e http_proxy \
  -e https_proxy \
  -v $PWD:/code \
  py-git-semver:latest \
  /bin/bash
```

Execute build:
```
pyb -X
```