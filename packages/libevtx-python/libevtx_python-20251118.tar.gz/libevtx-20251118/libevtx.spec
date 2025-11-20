Name: libevtx
Version: 20251118
Release: 1
Summary: Library to access the Windows XML Event Log (EVTX) format
Group: System Environment/Libraries
License: LGPL-3.0-or-later
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libevtx
                 
BuildRequires: gcc                 

%description -n libevtx
Library to access the Windows XML Event Log (EVTX) format

%package -n libevtx-static
Summary: Library to access the Windows XML Event Log (EVTX) format
Group: Development/Libraries
Requires: libevtx = %{version}-%{release}

%description -n libevtx-static
Static library version of libevtx.

%package -n libevtx-devel
Summary: Header files and libraries for developing applications for libevtx
Group: Development/Libraries
Requires: libevtx = %{version}-%{release}

%description -n libevtx-devel
Header files and libraries for developing applications for libevtx.

%package -n libevtx-python3
Summary: Python 3 bindings for libevtx
Group: System Environment/Libraries
Requires: libevtx = %{version}-%{release} python3
BuildRequires: python3-devel python3-setuptools

%description -n libevtx-python3
Python 3 bindings for libevtx

%package -n libevtx-tools
Summary: Several tools for reading Windows XML Event Log (EVTX) files
Group: Applications/System
Requires: libevtx = %{version}-%{release}    
    

%description -n libevtx-tools
Several tools for reading Windows XML Event Log (EVTX) files

%prep
%setup -q

%build
%configure --prefix=/usr --libdir=%{_libdir} --mandir=%{_mandir} --enable-python
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files -n libevtx
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so.*

%files -n libevtx-static
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.a

%files -n libevtx-devel
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so
%{_libdir}/pkgconfig/libevtx.pc
%{_includedir}/*
%{_mandir}/man3/*

%files -n libevtx-python3
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/python3*/site-packages/*.a
%{_libdir}/python3*/site-packages/*.so

%files -n libevtx-tools
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_bindir}/*
%{_mandir}/man1/*

%changelog
* Tue Nov 18 2025 Joachim Metz <joachim.metz@gmail.com> 20251118-1
- Auto-generated

