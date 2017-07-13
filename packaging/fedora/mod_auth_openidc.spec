Name:		mod_auth_openidc
Version:	2.3.1rc4
Release:	1%{?dist}
Summary:	OpenID Connect auth module for Apache HTTP Server
Vendor:         %{?GLOBUS_VENDOR}%{!?GLOBUS_VENDOR:undefined}
Epoch:          1
Group:		System Environment/Daemons
License:	ASL 2.0
URL:		https://github.com/pingidentity/mod_auth_openidc
Source0:	https://github.com/pingidentity/mod_auth_openidc/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:	httpd-devel
BuildRequires:	openssl-devel
BuildRequires:	curl-devel
BuildRequires:	jansson-devel
BuildRequires:	cjose-devel
BuildRequires:	jq-devel
%if %{?rhel}%{!?rhel:0} != 6
BuildRequires:	hiredis-devel
%endif
BuildRequires:	pcre-devel
BuildRequires:	autoconf
BuildRequires:	automake
Requires:	httpd-mmn

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
* Tue Jun 27 2017 Globus Toolkit <support@globus.org> 2.3.1rc4
- Adds GT6 modifications for Globus Auth
- Based on packaging for Fedora 23.
