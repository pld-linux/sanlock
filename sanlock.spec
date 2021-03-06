Summary:	Shared storage lock manager
Summary(pl.UTF-8):	Zarządca blokad dla współdzielonego składowania danych
Name:		sanlock
Version:	3.8.2
Release:	1
License:	LGPL v2+ (libsanlock_client, libwdmd), GPL v2 (libsanlock, utilities)
Group:		Networking
Source0:	https://releases.pagure.org/sanlock/%{name}-%{version}.tar.gz
# Source0-md5:	994d0587f21981d84a4af11a39617c45
Patch0:		%{name}-init-pld.patch
URL:		https://pagure.io/sanlock
BuildRequires:	gcc >= 5:3.4
BuildRequires:	libaio-devel
BuildRequires:	libblkid-devel
BuildRequires:	libuuid-devel
BuildRequires:	python-devel
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

# note (as of 3.3.0): python3 is not supported
cd python
%py_build
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
%py_install
cd ..

/sbin/ldconfig -n $RPM_BUILD_ROOT%{_libdir}

install -d $RPM_BUILD_ROOT{%{systemdunitdir},/etc/rc.d/init.d}
install init.d/fence_sanlockd $RPM_BUILD_ROOT/etc/rc.d/init.d
install init.d/sanlock $RPM_BUILD_ROOT/etc/rc.d/init.d
install init.d/wdmd $RPM_BUILD_ROOT/etc/rc.d/init.d
for serv in sanlock wdmd fence_sanlockd ; do
	sed -e "s,/lib/systemd/systemd-${serv},/etc/rc.d/init.d/${serv}," init.d/${serv}.service >$RPM_BUILD_ROOT%{systemdunitdir}/${serv}.service
done
cp -p init.d/sanlk-resetd.service $RPM_BUILD_ROOT%{systemdunitdir}

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

%files -n python-sanlock
%defattr(644,root,root,755)
%attr(755,root,root) %{py_sitedir}/sanlock.so
%{py_sitedir}/sanlock_python-%{version}_-py*.egg-info
