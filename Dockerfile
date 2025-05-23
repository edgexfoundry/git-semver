#
# Copyright (c) 2022 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
FROM python:3.13-slim AS build-image
ENV PYTHONDONTWRITEBYTECODE 1
ENV GIT_PYTHON_TRACE 1
WORKDIR /code
COPY . /code/
RUN apt-get update && apt-get install -y ssh netcat-traditional git
RUN pip install pybuilder
RUN pyb install

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV GIT_PYTHON_TRACE 1
WORKDIR /opt/pygsver
RUN apt-get update && apt-get install -y \
    ssh netcat-traditional curl gosu ca-certificates \
    libcurl4-gnutls-dev libexpat1-dev gettext \
    libz-dev libssl-dev make gcc

# Build Git 2.31.1 from source
RUN curl -LO https://mirrors.edge.kernel.org/pub/software/scm/git/git-2.31.1.tar.gz && \
    tar -xzf git-2.31.1.tar.gz && \
    cd git-2.31.1 && \
    make prefix=/usr/local all && \
    make prefix=/usr/local install && \
    cd .. && rm -rf git-2.31.1 git-2.31.1.tar.gz

COPY --from=build-image /code/target/dist/pygsver-*/dist/pygsver-*.tar.gz /opt/pygsver/
RUN pip install pygsver-*.tar.gz
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]