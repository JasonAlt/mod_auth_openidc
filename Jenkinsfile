#! groovy
@Library('gcs-build-scripts') _

def CJOSE_PACKAGE_VERSION="0.5.1"
def CJOSE_SOURCE_TARBALL_NAME = "${CJOSE_PACKAGE_VERSION}.tar.gz"
def CJOSE_SOURCE_TARBALL_URL = "https://github.com/cisco/cjose/archive/${CJOSE_SOURCE_TARBALL_NAME}"
def CJOSE_EXCLUDE = []

def JQ_PACKAGE_VERSION="1.5"
def JQ_SOURCE_TARBALL_NAME = "jq-${JQ_PACKAGE_VERSION}.tar.gz"
def JQ_SRPM_NAME = "jq-${JQ_PACKAGE_VERSION}-12.el8.src.rpm"
def JQ_SRPM_URL = "http://vault.centos.org/8.3.2011/AppStream/Source/SPackages/${JQ_SRPM_NAME}"
def JQ_EXCLUDE = []

env.DEFAULT_BRANCH = "globus"
env.STABLE_TAG = '${PACKAGE_NAME}-${PACKAGE_VERSION}'

pipeline {
    agent none
    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timeout(time: 3, unit: 'HOURS')
    }
    parameters {
        booleanParam(
            name: 'JQ',
            defaultValue: false,
            description: "Set to true to rebuild jq, otherwise only when changed"
        )
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
                            publishResults(
                                stashname,
                                "cjose",
                                CJOSE_PACKAGE_VERSION,
                                false)
                        }
                    }
                }
            }
        }
        stage ("jq") {
            when {
                anyOf {
                    equals expected: true, actual: params.JQ;
                    changeset "Jenkinsfile"
                }
            }
            stages {
                stage ("Prepare jq Source") {
                    agent {label "create_source_package"}
                    steps {
                        checkout scm
                        script {
                            env.JQ_SOURCE_STASH = "${UUID.randomUUID()}"

                            dirs (path: env.JQ_SOURCE_STASH, clean: true) {
                                sh """#! /bin/sh
                                    set -e
                                    curl -LOs "${JQ_SRPM_URL}"
                                    rpm2cpio "${JQ_SRPM_NAME}" | cpio -id
                                """
                            }
                            def (mbt, dbt) = enumerateBuildTargets()
                            JQ_EXCLUDE = mbt.findAll {
                                ! it.startsWith("el-8")
                            }
                            stash(name: env.JQ_SOURCE_STASH, includes: "${env.JQ_SOURCE_STASH}/**/*")
                        }
                    }
                }
                stage ("Build jq") {
                    steps {
                        script {
                            echo "JQ_EXCLUDE = ${JQ_EXCLUDE}"
                            // we only need to build this for el-8
                            env.JQ_RPM_ARTIFACTS_STASH = buildMock(
                                env.JQ_SOURCE_STASH,
                                JQ_SOURCE_TARBALL_NAME,
                                false,
                                getClubhouseEpic(),
                                JQ_EXCLUDE)
                        }
                    }
                }
                stage ("Publish jq") {
                    agent { label "master" }
                    steps {
                        script {
                            def stashname = "${UUID.randomUUID()}"

                            dir("artifacts") {
                                if (env.JQ_RPM_ARTIFACTS_STASH) {
                                    unstash(name: env.JQ_RPM_ARTIFACTS_STASH)
                                }
                                stash(name: stashname, includes: "**/*")
                                deleteDir()
                            }
                            publishResults(
                                stashname,
                                "jq",
                                JQ_PACKAGE_VERSION,
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
                                    git clean -dfx
                                    (cd ..;
                                    autoreconf -i
                                    ac_cv_header_apr_memcache_h=yes PKG_CONFIG=true HAVE_MEMCACHE=1 HAVE_LIBHIREDIS=1 ./configure --with-apxs2=/bin/true
                                    rm -f mod_auth_openidc-*.tar.gz
                                    make distfile
                                    )
                                    cp ../*.tar.gz .
                                    cp ../packaging/fedora/mod_auth_openidc.spec .
                                    cp -R ../packaging/debian/mod-auth-openidc/debian debian
                                """
                                env.OIDC_TARBALL = sh(
                                    script: "basename *.tar.gz",
                                    returnStdout: true).trim()
                                env.OIDC_VERSION = sh(
                                    script: "../configure --version | awk '{print \$3; exit}'",
                                    returnStdout: true).trim()
                            }
                            stash(
                                name: env.MOD_AUTH_OIDC_SOURCE_STASH,
                                includes: "${env.MOD_AUTH_OIDC_SOURCE_STASH}/**/*")
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
                                true,
                                getClubhouseEpic(),
                                null)
                            }, "rpm": {
                                env.MOD_AUTH_OIDC_RPM_ARTIFACTS_STASH = buildMock(
                                    env.MOD_AUTH_OIDC_SOURCE_STASH,
                                    env.OIDC_TARBALL,
                                    true,
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
                            // Explicitly set release version in the tag
                            env.STABLE_TAG = '${PACKAGE_NAME}-${PACKAGE_VERSION}-2'
                            publishResults(
                                stashname,
                                "mod_auth_openidc",
                                env.OIDC_VERSION,
                                false)
                        }
                    }
                }
            }
        }
    }
}
