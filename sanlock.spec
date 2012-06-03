# TODO: systemd support (there are init.d/*.service, but they refer to unknown /lib/systemd/systemd-sanlock)
Summary:	Shared storage lock manager
Summary(pl.UTF-8):	Zarządca blokad dla współdzielonego składowania danych
Name:		sanlock
Version:	2.3
Release:	1
License:	LGPL v2+ (libsanlock_client, libwdmd), GPL v2 (libsanlock, utilities)
Group:		Networking
Source0:	https://fedorahosted.org/releases/s/a/sanlock/%{name}-%{version}.tar.gz
# Source0-md5:	17ddc7c7b9dfab30e82890b6d14cda57
Patch0:		%{name}-link.patch
Patch1:		%{name}-init-pld.patch
URL:		https://fedorahosted.org/sanlock/
BuildRequires:	gcc >= 5:3.4
BuildRequires:	libaio-devel
BuildRequires:	libblkid-devel
BuildRequires:	libuuid-devel
BuildRequires:	python-devel
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	%{name}-libs = %{version}-%{release}
Provides:	group(sanlock)
Provides:	user(sanlock)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Shared storage lock manager.

%description -l pl.UTF-8
Zarządca blokad dla współdzielonego składowania danych.

%package libs
Summary:	Sanlock libraries
Summary(pl.UTF-8):	Biblioteki sanlock
Group:		Libraries

%description libs
Sanlock libraries.

%description libs -l pl.UTF-8
Biblioteki sanlock.

%package devel
Summary:	Header files for sanlock libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek sanlock
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for sanlock libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe bibliotek sanlock.

%package -n python-sanlock
Summary:	Python binding for sanlock library
Summary(pl.UTF-8):	Wiązanie Pythona do biblioteki sanlock
Group:		Libraries/Python
Requires:	%{name}-libs = %{version}-%{release}

%description -n python-sanlock
Python binding for sanlock library.

%description -n python-sanlock -l pl.UTF-8
Wiązanie Pythona do biblioteki sanlock.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
export CFLAGS="%{rpmcflags}"

CMD_LDFLAGS="%{rpmldflags}" \
LIB_LDFLAGS="%{rpmldflags}" \
%{__make} -C wdmd \
	CC="%{__cc}"

CMD_LDFLAGS="%{rpmldflags}" \
LIB_CLIENT_LDFLAGS="%{rpmldflags}" \
LIB_ENTIRE_LDFLAGS="%{rpmldflags}" \
%{__make} -C src \
	CC="%{__cc}"

%{__make} -C python

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C wdmd install \
	DESTDIR=$RPM_BUILD_ROOT \
	LIBDIR=%{_libdir}

%{__make} -C src install \
	DESTDIR=$RPM_BUILD_ROOT \
	LIBDIR=%{_libdir}

%{__make} -C python install \
	DESTDIR=$RPM_BUILD_ROOT

/sbin/ldconfig -n $RPM_BUILD_ROOT%{_libdir}

install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/var/run/{sanlock,wdmd}}
install init.d/sanlock $RPM_BUILD_ROOT/etc/rc.d/init.d
install init.d/wdmd $RPM_BUILD_ROOT/etc/rc.d/init.d

install -d $RPM_BUILD_ROOT/usr/lib/tmpfiles.d
cat >$RPM_BUILD_ROOT/usr/lib/tmpfiles.d/sanlock.conf <<EOF
d /var/run/sanlock 0775 root root -
d /var/run/wdmd 0755 root root -
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 279 sanlock
%useradd -u 279 -g 279 -d /usr/share/empty -s /bin/false -c 'SANlock user' sanlock

%post
/sbin/chkconfig --add sanlock
/sbin/chkconfig --add wdmd
%service sanlock restart
%service wdmd restart

%preun
if [ "$1" = "0" ]; then
	%service -q sanlock stop
	%service -q wdmd stop
	/sbin/chkconfig --del sanlock
	/sbin/chkconfig --del wdmd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove sanlock
	%groupremove sanlock
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.license
%attr(755,root,root) %{_sbindir}/sanlock
%attr(755,root,root) %{_sbindir}/wdmd
%attr(754,root,root) /etc/rc.d/init.d/sanlock
%attr(754,root,root) /etc/rc.d/init.d/wdmd
/usr/lib/tmpfiles.d/sanlock.conf
%attr(775,sanlock,sanlock) %dir /var/run/sanlock
%dir /var/run/wdmd
%{_mandir}/man8/sanlock.8*
%{_mandir}/man8/wdmd.8*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libsanlock.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libsanlock.so.1
%attr(755,root,root) %{_libdir}/libsanlock_client.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libsanlock_client.so.1
%attr(755,root,root) %{_libdir}/libwdmd.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libwdmd.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libsanlock.so
%attr(755,root,root) %{_libdir}/libsanlock_client.so
%attr(755,root,root) %{_libdir}/libwdmd.so
%{_includedir}/sanlock*.h
%{_includedir}/wdmd.h

%files -n python-sanlock
%defattr(644,root,root,755)
%attr(755,root,root) %{py_sitedir}/sanlock.so
%{py_sitedir}/Sanlock-1.0-py*.egg-info
