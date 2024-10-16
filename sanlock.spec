#
# Conditional build:
%bcond_without	python2	# CPython 2.x module
%bcond_without	python3	# CPython 3.x module

Summary:	Shared storage lock manager
Summary(pl.UTF-8):	Zarządca blokad dla współdzielonego składowania danych
Name:		sanlock
Version:	3.9.5
Release:	1
License:	LGPL v2+ (libsanlock_client, libwdmd), GPL v2 (libsanlock, utilities)
Group:		Networking
Source0:	https://releases.pagure.org/sanlock/%{name}-%{version}.tar.gz
# Source0-md5:	5cbcaf46f27ceea92c4efded6a4ad00e
Patch0:		%{name}-restore-sysv.patch
Patch1:		%{name}-init-pld.patch
URL:		https://pagure.io/sanlock
BuildRequires:	gcc >= 5:3.4
BuildRequires:	libaio-devel
BuildRequires:	libblkid-devel
BuildRequires:	libuuid-devel
%if %{with python2}
BuildRequires:	python-devel >= 1:2.5
BuildRequires:	python-setuptools
%endif
%if %{with python3}
BuildRequires:	python3-devel >= 1:3.2
BuildRequires:	python3-setuptools
%endif
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
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

%package reset
Summary:	Host reset daemon and client using sanlock
Summary(pl.UTF-8):	Demon resetujący hosta oraz klient wykorzystujący sanlocka
Group:		Daemons
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name} = %{version}-%{release}

%description reset
This package contains the reset daemon and client. A cooperating host
running the daemon can be reset by a host running the client, so long
as both maintain access to a common sanlock lockspace.

%description reset -l pl.UTF-8
Ten pakiet zawiera demona oraz klienta resetującego. Współpracujący
host z działającym demonem może być zresetowany przez host z
działającym klientem tak długo, jak oba mają dostęp do wspólnej
przestrzeni blokad sanlock.

%package -n fence-sanlock
Summary:	Fence agent using sanlock and wdmd
Summary(pl.UTF-8):	Agent barier wykorzystujący sanlocka oraz wdmd
Group:		Daemons
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name} = %{version}-%{release}

%description -n fence-sanlock
This package contains the fence agent and daemon for using sanlock and
wdmd as a cluster fence agent.

%description -n fence-sanlock -l pl.UTF-8
Ten pakiet zawiera agenta oraz demona barier do użytku z sanlockiem
oraz wdmd jako agent barier w klastrze.

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
# for libsanlock
Requires:	libaio-devel
Requires:	libblkid-devel
Requires:	libuuid-devel

%description devel
Header files for sanlock libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe bibliotek sanlock.

%package -n python-sanlock
Summary:	Python 2 binding for sanlock library
Summary(pl.UTF-8):	Wiązanie Pythona 2 do biblioteki sanlock
Group:		Libraries/Python
Requires:	%{name}-libs = %{version}-%{release}

%description -n python-sanlock
Python 2 binding for sanlock library.

%description -n python-sanlock -l pl.UTF-8
Wiązanie Pythona 2 do biblioteki sanlock.

%package -n python3-sanlock
Summary:	Python 3 binding for sanlock library
Summary(pl.UTF-8):	Wiązanie Pythona 3 do biblioteki sanlock
Group:		Libraries/Python
Requires:	%{name}-libs = %{version}-%{release}

%description -n python3-sanlock
Python 3 binding for sanlock library.

%description -n python3-sanlock -l pl.UTF-8
Wiązanie Pythona 3 do biblioteki sanlock.

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

CFLAGS= \
%{__make} -C fence_sanlock \
	CC="%{__cc}" \
	OPTIMIZE_FLAG="%{rpmcflags}"

CFLAGS= \
%{__make} -C reset \
	CC="%{__cc}" \
	LDFLAGS="%{rpmldflags}" \
	OPTIMIZE_FLAG="%{rpmcflags}"

cd python
%if %{with python2}
%py_build
%endif

%if %{with python3}
%py3_build
%endif
cd ..

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C wdmd install \
	DESTDIR=$RPM_BUILD_ROOT \
	LIBDIR=%{_libdir}

%{__make} -C src install \
	DESTDIR=$RPM_BUILD_ROOT \
	LIBDIR=%{_libdir}

%{__make} -C fence_sanlock install \
	DESTDIR=$RPM_BUILD_ROOT \
	LIBDIR=%{_libdir}

%{__make} -C reset install \
	DESTDIR=$RPM_BUILD_ROOT

cd python
%if %{with python2}
%py_install
%endif

%if %{with python3}
%py3_install
%endif
cd ..

/sbin/ldconfig -n $RPM_BUILD_ROOT%{_libdir}

install -d $RPM_BUILD_ROOT{%{systemdunitdir},/etc/rc.d/init.d}
install init.d/fence_sanlockd $RPM_BUILD_ROOT/etc/rc.d/init.d
install init.d/sanlock-sysv $RPM_BUILD_ROOT/etc/rc.d/init.d/sanlock
install init.d/wdmd-sysv $RPM_BUILD_ROOT/etc/rc.d/init.d/wdmd
sed -e "s,/lib/systemd/systemd-fence_sanlockd,/etc/rc.d/init.d/fence_sanlockd," init.d/fence_sanlockd.service >$RPM_BUILD_ROOT%{systemdunitdir}/fence_sanlockd.service
cp -p init.d/sanlk-resetd.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p init.d/sanlock.service.native $RPM_BUILD_ROOT%{systemdunitdir}/sanlock.service
cp -p init.d/wdmd.service $RPM_BUILD_ROOT%{systemdunitdir}
install init.d/systemd-wdmd $RPM_BUILD_ROOT/lib/systemd

install -d $RPM_BUILD_ROOT/var/run/{sanlock,wdmd,fence_sanlock,fence_sanlockd}
install -d $RPM_BUILD_ROOT%{systemdtmpfilesdir}
cat >$RPM_BUILD_ROOT%{systemdtmpfilesdir}/sanlock.conf <<EOF
d /var/run/sanlock 0775 sanlock sanlock -
d /var/run/wdmd 0775 root sanlock -
EOF
cat >$RPM_BUILD_ROOT%{systemdtmpfilesdir}/fence_sanlock.conf <<EOF
d /var/run/fence_sanlock 0755 root root -
d /var/run/fence_sanlockd 0755 root root -
EOF

# fix hardcoded libdir=${prefix}/lib64
%{__sed} -i -e 's,^libdir=.*,libdir=%{_libdir},' $RPM_BUILD_ROOT%{_pkgconfigdir}/*.pc

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

%post -n fence-sanlock
/sbin/chkconfig --add fence_sanlock
%service fence_sanlock restart
if [ "$1" = "1" ]; then
	ccs_update_schema >/dev/null 2>&1 || :
fi

%preun -n fence-sanlock
if [ "$1" = "0" ]; then
	%service -q fence_sanlock stop
	/sbin/chkconfig --del fence_sanlock
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
%attr(755,root,root) /lib/systemd/systemd-wdmd
%{systemdunitdir}/sanlock.service
%{systemdunitdir}/wdmd.service
%{systemdtmpfilesdir}/sanlock.conf
%attr(775,sanlock,sanlock) %dir /var/run/sanlock
%attr(775,root,sanlock) %dir /var/run/wdmd
%{_mandir}/man8/sanlock.8*
%{_mandir}/man8/wdmd.8*

%files reset
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/sanlk-reset
%attr(755,root,root) %{_sbindir}/sanlk-resetd
%{systemdunitdir}/sanlk-resetd.service
%{_mandir}/man8/sanlk-reset.8*
%{_mandir}/man8/sanlk-resetd.8*

%files -n fence-sanlock
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/fence_sanlock
%attr(755,root,root) %{_sbindir}/fence_sanlockd
%attr(754,root,root) /etc/rc.d/init.d/fence_sanlockd
%{systemdunitdir}/fence_sanlockd.service
%{systemdtmpfilesdir}/fence_sanlock.conf
%dir /var/run/fence_sanlock
%dir /var/run/fence_sanlockd
%{_mandir}/man8/fence_sanlock.8*
%{_mandir}/man8/fence_sanlockd.8*

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
%{_pkgconfigdir}/libsanlock.pc
%{_pkgconfigdir}/libsanlock_client.pc

%if %{with python2}
%files -n python-sanlock
%defattr(644,root,root,755)
%attr(755,root,root) %{py_sitedir}/sanlock.so
%{py_sitedir}/sanlock_python-%{version}-py*.egg-info
%endif

%if %{with python3}
%files -n python3-sanlock
%defattr(644,root,root,755)
%attr(755,root,root) %{py3_sitedir}/sanlock.cpython-*.so
%{py3_sitedir}/sanlock_python-%{version}-py*.egg-info
%endif
