#! groovy

@Library('gcs-build-scripts@debian-cowbuilder-init') _

def CJOSE_PACKAGE_VERSION="0.5.1"
def CJOSE_SOURCE_TARBALL_NAME = "${CJOSE_PACKAGE_VERSION}.tar.gz"
def CJOSE_SOURCE_TARBALL_URL = "https://github.com/cisco/cjose/archive/${CJOSE_SOURCE_TARBALL_NAME}"

// not really an epic, but used to test the build sys
env.EPIC = "2729"


pipeline {
    agent none
    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timeout(time: 3, unit: 'HOURS')
    }
    parameters {
        booleanParam(
            name: 'CJOSE',
            defaultValue: false,
            description: "Set to true to rebuild cjose, otherwise only when changed"
        )
        booleanParam(
            name: 'MOD_AUTH_OPENIDC',
            defaultValue: false,
            description: "Set to true to rebuild mod-auth-openidc, otherwise only when changed"
        )
    }
    stages {
        stage ("cjose") {
            when {
                anyOf {
                    equals expected: true, actual: params.CJOSE;
                    changeset "packaging/debian/cjose/debian/**/*";
                    changeset "packaging/fedora/cjose.spec";
                }
            }
            stages {
                stage ("Prepare Source") {
                    agent any
                    steps {
                        checkout scm
                        script {
                            env.CJOSE_SOURCE_STASH = "${UUID.randomUUID()}"

                            dirs (path: env.CJOSE_SOURCE_STASH, clean: true) {
                                sh """#! /bin/sh
                                    set -e
                                    curl -LOs "${CJOSE_SOURCE_TARBALL_URL}"
                                    cp ../packaging/fedora/cjose.spec .
                                    cp -R ../packaging/debian/cjose/debian debian
                                """
                            }
                            def mock_build_targets, _deb = enumerateBuildTargets()
                            env. exclude_mock = mock_build_targets.findAll {
                                it.startsWith("fedora-")
                            }
                            stash(name: env.CJOSE_SOURCE_STASH, includes: "${env.CJOSE_SOURCE_STASH}/**/*")
                        }
                    }
                }
                stage ("Build cjose") {
                    steps {
                        script {
                            // we only need to build this for el-7 and el-8
                            env.CJOSE_RPM_ARTIFACTS_STASH = buildMock(
                                env.CJOSE_SOURCE_STASH,
                                CJOSE_SOURCE_TARBALL_NAME,
                                false,
                                getClubhouseEpic(),
                                env.exclude_mock)
                        }
                    }
                }
                stage ("Publish cjose") {
                    agent { label "master" }
                    steps {
                        script {
                            def stashname = "${UUID.randomUUID()}"

                            dir("artifacts") {
                                if (env.CJOSE_RPM_ARTIFACTS_STASH) {
                                    unstash(name: env.CJOSE_RPM_ARTIFACTS_STASH)
                                }
                                stash(name: stashname, includes: "**/*")
                                deleteDir()
                            }
                            publishResults(
                                stashname,
                                "cjose",
                                env.CJOSE_PACKAGE_VERSION,
                                false)
                        }
                    }
                }
            }
        }
        stage ("mod-auth-openidc") {
            when {
                anyOf {
                    equals expected: true, actual: params.MOD_AUTH_OPENIDC;
                    changeset "*";
                    changeset "src/**/*";
                    changeset "test/**/*";
                    changeset "packaging/fedora/mod_auth_openidc.spec";
                    changeset "packaging/debian/mod-auth-openidc/debian/**/*";
                }
            }
            steps {
                checkout scm
                script {
                    automakePipeline(
                        source_dir: ".",
                        debian_dir: "packaging/debian/mod-auth-openidc/debian",
                        spec_file: "packaging/fedora/mod_auth_openidc.spec"
                    )
                }
            }
        }
    }
}
