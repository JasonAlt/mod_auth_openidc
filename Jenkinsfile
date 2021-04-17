#! groovy

@Library('gcs-build-scripts@debian-cowbuilder-init') _

def CJOSE_PACKAGE_VERSION="0.5.1"
def CJOSE_SOURCE_TARBALL_NAME = "${CJOSE_PACKAGE_VERSION}.tar.gz"
def CJOSE_SOURCE_TARBALL_URL = "https://github.com/cisco/cjose/archive/${CJOSE_SOURCE_TARBALL_NAME}"
def CJOSE_EXCLUDE = []

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
                stage ("Prepare cjose Source") {
                    agent {label "create_source_package"}
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
                            def (mock_build_targets, _deb) = enumerateBuildTargets()
                            echo "mock_build_targets=${mock_build_targets}"
                            echo "_deb=${_deb}"
                            CJOSE_EXCLUDE = mock_build_targets.findAll {
                                it.startsWith("fedora-")
                            }
                            stash(name: env.CJOSE_SOURCE_STASH, includes: "${env.CJOSE_SOURCE_STASH}/**/*")
                        }
                    }
                }
                stage ("Build cjose") {
                    steps {
                        script {
                            echo "CJOSE_EXCLUDE = ${CJOSE_EXCLUDE}"
                            // we only need to build this for el-7 and el-8
                            env.CJOSE_RPM_ARTIFACTS_STASH = buildMock(
                                env.CJOSE_SOURCE_STASH,
                                CJOSE_SOURCE_TARBALL_NAME,
                                false,
                                getClubhouseEpic(),
                                CJOSE_EXCLUDE)
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
                            /*
                            publishResults(
                                stashname,
                                "cjose",
                                env.CJOSE_PACKAGE_VERSION,
                                false)
                            */
                        }
                    }
                }
            }
        }
        stage ("mod-auth-openidc") {
            when {
                anyOf {
                    equals expected: true, actual: params.MOD_AUTH_OPENIDC;
                    changeset "Makefile";
                    changeset "configure.ac";
                    changeset "src/**/*";
                    changeset "test/**/*";
                    changeset "packaging/fedora/mod_auth_openidc.spec";
                    changeset "packaging/debian/mod-auth-openidc/debian/**/*";
                }
            }
            stages {
                stage ("Prepare mod-auth-oidc Source") {
                    agent {label "create_source_package"}
                    steps {
                        checkout scm
                        script {
                            env.MOD_AUTH_OIDC_SOURCE_STASH = "${UUID.randomUUID()}"

                            dirs (path: env.MOD_AUTH_OIDC_SOURCE_STASH, clean: true) {
                                sh """#! /bin/sh
                                    set -e
                                    set -x
                                    ls -Ra
                                    autoreconf -i
                                    PKG_CONFIG=true ./configure --with-apxs2=/bin/true
                                    rm *.tar.gz
                                    make distfile
                                    cp ../packaging/fedora/mod_auth_openidc.spec .
                                    cp -R ../packaging/debian/mod-auth-openidc/debian debian
                                """
                                env.OIDC_TARBALL = sh(
                                    script: "ls -1 *.tar.gz",
                                    returnStdout: true).trim()
                                env.OIDC_VERSION = sh(
                                    script: "./configure --version | awk '{print \$1; exit}'",
                                    returnStdout: true).trim()
                            }
                            stash(
                                name: env.MOD_AUTH_OIDC_SOURCE_STASH,
                                includes: "${env.MOD_AUTH_OIDC_SOURCE_STASH}/*.tar.gz,${env.MOD_AUTH_OIDC_SOURCE_STASH}/*.spec,${env.MOD_AUTH_OIDC_SOURCE_STASH}/debian/**/*")
                        }
                    }
                }
                stage ("Build mod-auth-oidc") {
                    steps {
                        script {
                            parallel "debian": {
                                env.MOD_AUTH_OIDC_DEB_ARTIFACTS_STASH = buildDebian(
                                env.MOD_AUTH_OIDC_SOURCE_STASH,
                                env.OIDC_TARBALL,
                                false,
                                getClubhouseEpic(),
                                null)
                            }, "rpm": {
                                env.MOD_AUTH_OIDC_RPM_ARTIFACTS_STASH = buildMock(
                                    env.MOD_AUTH_OIDC_SOURCE_STASH,
                                    env.OIDC_TARBALL,
                                    false,
                                    getClubhouseEpic(),
                                    null)
                            }, "failFast": false
                        }
                    }
                }
                stage ("Publish mod-auth-oidc") {
                    agent { label "master" }
                    steps {
                        script {
                            def stashname = "${UUID.randomUUID()}"

                            dir("artifacts") {
                                if (env.MOD_AUTH_OIDC_RPM_ARTIFACTS_STASH) {
                                    unstash(name: env.MOD_AUTH_OIDC_RPM_ARTIFACTS_STASH)
                                }
                                if (env.MOD_AUTH_OIDC_DEB_ARTIFACTS_STASH) {
                                    unstash(name: env.MOD_AUTH_OIDC_DEB_ARTIFACTS_STASH)
                                }
                                stash(name: stashname, includes: "**/*")
                                deleteDir()
                            }
                            /*
                            publishResults(
                                stashname,
                                "mod_auth_openidc",
                                env.OIDC_VERSION,
                                false)
                            */
                        }
                    }
                }
            }
        }
    }
}
