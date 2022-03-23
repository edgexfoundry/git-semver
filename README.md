[![complexity](https://img.shields.io/badge/complexity-Simple:%205-brightgreen)](https://radon.readthedocs.io/en/latest/api.html#module-radon.complexity)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![coverage](https://img.shields.io/badge/coverage-100.0%25-brightgreen)](https://pybuilder.io/)
[![complexity](https://img.shields.io/badge/complexity-Simple:%204-brightgreen)](https://radon.readthedocs.io/en/latest/api.html#module-radon.complexity)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-Low-yellow)](https://pypi.org/project/bandit/)
[![python](https://img.shields.io/badge/python-3.9-teal)](https://www.python.org/downloads/)
# test-git-semver

docker image build \
--build-arg http_proxy \
--build-arg https_proxy \
-t \
tgsver:latest .

docker container run \
--rm \
-it \
-e ALL_PROXY=socks5://proxy-us.intel.com:1080 \
-v $HOME/.ssh:/root/.ssh \
tgsver:latest bash

docker container run \
--rm \
-it \
-e http_proxy \
-e https_proxy \
-e GH_TOKEN_PSW \
-v $PWD:/code \
tgsver:latest bash