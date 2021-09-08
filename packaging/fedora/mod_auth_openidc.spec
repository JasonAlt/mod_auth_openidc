Name:		mod_auth_openidc
Version:	2.4.9.4g
Release:	1%{?dist}
Summary:	OpenID Connect auth module for Apache HTTP Server
Vendor:         %{?GLOBUS_VENDOR}%{!?GLOBUS_VENDOR:undefined}
Epoch:          1
Group:		System Environment/Daemons
License:	ASL 2.0
URL:		https://github.com/pingidentity/mod_auth_openidc
Source0:	https://github.com/pingidentity/mod_auth_openidc/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:	gcc
BuildRequires:	httpd-devel
BuildRequires:	openssl-devel
BuildRequires:	curl-devel
BuildRequires:	jansson-devel
BuildRequires:	cjose-devel
BuildRequires:	jq-devel
BuildRequires:	hiredis-devel
BuildRequires:	pcre-devel
BuildRequires:	autoconf
BuildRequires:	automake
Requires:	httpd-mmn
Provides:       mod_auth_openidc_globus_extension

%description
This module enables an Apache 2.x web server to operate as
an OpenID Connect Relying Party and/or OAuth 2.0 Resource Server.

%prep
%setup -q

%build
# workaround rpm-buildroot-usage
export APXS2_OPTS='-S LIBEXECDIR=${MODULES_DIR}'
%if %{?_httpd_moddir:1}%{!?__httpd_moddir:0} == 0
%global _httpd_moddir %{_sysconfdir}/httpd/modules
%endif
%if %{?_httpd_modconfdir:1}%{!?_httpd_modconfdir:0} == 0
%global _httpd_modconfdir %{_sysconfdir}/httpd/conf.d
%endif
export MODULES_DIR=%{_httpd_moddir}
autoreconf
%configure
autoreconf -if
make %{?_smp_mflags}

%install
mkdir -p $RPM_BUILD_ROOT%{_httpd_moddir}
make install MODULES_DIR=$RPM_BUILD_ROOT%{_httpd_moddir}

install -m 755 -d $RPM_BUILD_ROOT%{_httpd_modconfdir}
echo 'LoadModule auth_openidc_module modules/mod_auth_openidc.so' > \
	$RPM_BUILD_ROOT%{_httpd_modconfdir}/10-auth_openidc.conf

%files
%license LICENSE.txt
%doc ChangeLog
%{_httpd_moddir}/mod_auth_openidc.so
%config(noreplace) %{_httpd_modconfdir}/10-auth_openidc.conf

%changelog
* Wed Sep 08 2021 Globus Toolkit <support@globus.org> 2.4.9.4g
- Merged zmartzone 2.4.9.4
* Wed May 05 2021 Globus Toolkit <support@globus.org> 2.3.2k
- Rebuild for new ubuntu and fedora targets
* Wed Jun 09 2020 Globus Toolkit <support@globus.org> 2.3.2j
- Pass list of objects through as claims

* Thu Jun 04 2020 Globus Toolkit <support@globus.org> 2.3.2i
- Fix bounds issue

* Wed Jun 13 2018 Globus Toolkit <support@globus.org> 2.3.2h
- Add inter-module request-specific OIDCAuthRequestParams

* Tue Oct 03 2017 Globus Toolkit <support@globus.org> 2.3.2
- Update to new upstream release

* Thu Jul 27 2017 Globus Toolkit <support@globus.org> 2.3.1
- Update to new upstream release
- Add Provides: mod_auth_openidc_globus_extension

* Tue Jun 27 2017 Globus Toolkit <support@globus.org> 2.3.1rc4
- Adds GT6 modifications for Globus Auth
- Based on packaging for Fedora 23.
