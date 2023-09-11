Name:           cjose
Version:        0.6.2.2
Release:        1%{?dist}
Summary:        C library implementing the Javascript Object Signing and Encryption (JOSE)
Group:          System Environment/Libraries
License:        MIT
URL:            https://github.com/OpenIDC/cjose
Source0:        https://github.com/OpenIDC/cjose/releases/download/v%{version}/cjose-%{version}.tar.gz
Vendor:         %{VENDOR}
Epoch:          1

BuildRoot:      %{_tmppath}/cjose-%{version}-%{release}-build
BuildRequires:  openssl-devel
%if %{?suse_version}%{!?suse_version:0} == 0
BuildRequires:  jansson-devel
%else
BuildRequires:  libjansson-devel
%endif
BuildRequires:  check-devel

%description
Implementation of JOSE for C/C++

%package devel
Summary:        Development files for CJOSE
Group:          System Environment/Libraries
Provides:       cjose-devel

%description devel
This package contains the necessary header files to develop applications using CJOSE.

%prep
%setup -q

%build

%configure
make test

%install
%make_install
rm $RPM_BUILD_ROOT/%{_libdir}/libcjose.a $RPM_BUILD_ROOT/%{_libdir}/libcjose.la

%clean
rm -rf $PRM_BUILD_ROOT

%files
%{_libdir}/libcjose.so.*

%files devel
%{_libdir}/libcjose.so
%{_includedir}/cjose/*.h
%{_libdir}/pkgconfig/cjose.pc
