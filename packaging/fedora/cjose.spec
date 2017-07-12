Name:           cjose
Version:        0.5.1
Release:        1%{?dist}
Summary:        C library implementing the Javascript Object Signing and Encryption (JOSE)
Group:          System Environment/Libraries
License:        MIT
URL:            https://github.com/cisco/cjose
Source0:        https://github.com/cisco/cjose/archive/%{version}.tar.gz
Vendor:         %{VENDOR}
Epoch:          1

BuildRoot:      %{_tmppath}/cjose-%{version}-%{release}-build
Requires:       openssl, jansson
BuildRequires:  openssl-devel, jansson-devel, check-devel, doxygen

%description
Implementation of JOSE for C/C++

%package devel
Summary:        Development files for CJOSE
Group:          System Environment/Libraries
Provides:       cjose-devel

%description devel
This package contains the necessary header files to develop applications using CJOSE.

%package doc
Summary:        Documentation files for CJOSE
Group:          System Environment/Libraries
%if %{?fedora}%{!?fedora:0} >= 10 || %{?rhel}%{!?rhel:0} >= 6
BuildArch:      noarch
%endif

%description doc
This package contains the documentation to develop applications using CJOSE.

%prep
%setup -q

%build

%configure
make test
make doxygen

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

%files doc
%{_docdir}/cjose/html/*
