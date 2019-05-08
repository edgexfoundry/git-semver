//
// Copyright (c) 2019 Intel Corporation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

loadGlobalLibrary()

pipeline {
    agent {
        label 'centos7-docker-2c-1g'
    }
    options {
        timestamps()
    }
    stages {
        stage('Prepare') {
            steps {
                edgeXSetupEnvironment()
                edgeXDockerLogin(settingsFile: env.MVN_SETTINGS)
            }
        }
        stage('Docker Build') {
            parallel {
                stage('build-amd64') {
                    agent {
                        label 'centos7-docker-4c-2g'
                    }
                    steps {
                        doBuild 'amd64'
                    }
                }
                stage('build-arm64') {
                    agent {
                        label 'ubuntu18.04-docker-arm64-4c-2g'
                    }
                    steps {
                        doBuild 'arm64'
                    }
                }
            }
        }
        stage('SemVer Init') {
            steps {
                doSemver('amd64', 'edgexfoundry/git-semver') {
                    sh 'git semver init'
                }
                stash name: 'semver', includes: '.semver/**', useDefaultExcludes: false
            }
        }
        stage('Docker Push') {
            when {
                expression {
                    edgex.isReleaseStream()
                }
            }
            parallel {
                stage('push-amd64') {
                    agent {
                        label 'centos7-docker-4c-2g'
                    }
                    steps {
                        doPush 'amd64'
                    }
                }
                stage('push-arm64') {
                    agent {
                        label 'ubuntu18.04-docker-arm64-4c-2g'
                    }
                    steps {
                        doPush 'arm64'
                    }
                }
            }
        }
        stage('SemVer Tag ➡️ Bump ➡️ Push') {
            when {
                expression {
                    edgex.isReleaseStream()
                }
            }
            steps {
                unstash 'semver'
                doSemver('amd64', 'edgexfoundry/git-semver') {
                    sh 'git semver tag'
                    sh 'git semver bump patch'
                    sh 'git semver push'
                }
            }
        }
    }

    post {
        always {
            edgeXInfraPublish()
        }
    }
}

def doBuild(arch, image='edgexfoundry/git-semver') {
    dockerBuild(arch, image)
    dockerSave(arch, image)
}

def doPush(arch, image='edgexfoundry/git-semver') {
    unstash 'semver'
    dockerLoad(arch, image)
    dockerPush(arch, image, "https://${env.DOCKER_REGISTRY}:10004")
    // dockerPush(arch, image, "https://${env.DOCKERHUB_REGISTRY}")
}

def doSemver(arch, image, body) {
    dockerLoad(arch, image)
    docker.image("${image}:${arch}").inside('--volume /etc/ssh:/etc/ssh') {
        withEnv(['SSH_KNOWN_HOSTS=/etc/ssh/ssh_known_hosts','SEMVER_DEBUG=on']) {
            sshagent (credentials: ['edgex-jenkins-ssh']) {
                body()
            }
        }
    }
}

def dockerBuild(arch, image) {
    docker.build("${image}:${arch}").inside() {
        sh 'uname -a'
        sh 'git version'
        sh 'git semver -h || true'
    }
}

def dockerSave(arch, image) {
    sh "docker image save --output ${arch}.tar ${image}:${arch}"
    sh "docker system info --format {{.Architecture}} > ${arch}.txt"
    stash name: arch, includes: "${arch}.tar,${arch}.txt"
}

def dockerLoad(arch, image) {
    unstash "${arch}"
    sh "docker image load --input ${arch}.tar"
}

def dockerPush(arch, image, registry) {
    sh 'env | sort'
    def img = docker.image("${image}:${arch}")
    def mach = readFile("${arch}.txt").trim()
    def versions = []
    docker.image("${image}:${arch}").inside('--env SEMVER_DEBUG=on') {
        def ver = sh script: 'git semver', returnStdout: true
        versions << ver.trim()
    }
    versions << 'latest'
    for (ver in versions) {
        docker.withRegistry(registry, 'git-semver') {
            img.push("${ver}-${arch}")
            img.push("${ver}-${mach}")
        }
    }
}

def loadGlobalLibrary(branch = '*/master') {
    library(identifier: 'edgex-global-pipelines@master',
        retriever: legacySCM([
            $class: 'GitSCM',
            userRemoteConfigs: [[url: 'https://github.com/edgexfoundry/edgex-global-pipelines.git']],
            branches: [[name: branch]],
            doGenerateSubmoduleConfigurations: false,
            extensions: [[
                $class: 'SubmoduleOption',
                recursiveSubmodules: true,
            ]]]
        )
    ) _
}