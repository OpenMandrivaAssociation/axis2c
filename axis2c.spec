%define	major 0
%define libname %mklibname axis2c %{major}
%define develname %mklibname axis2c -d

Summary:	Axis2/C is an effort to implement Axis2 architecture, in C
Name:		axis2c
Version:	1.1.0
Release:	%mkrel 1
Group:		System/Libraries
License:	Apache License
URL:		http://ws.apache.org/axis2/c/
Source0:	http://www.apache.org/dist/ws/axis2/c/0_91/axis2c-src-%{version}.tar.gz
Source1:	http://www.apache.org/dist/ws/axis2/c/0_91/axis2c-src-%{version}.tar.gz.asc
Source2:	A64_mod_axis2.conf
Source3:	autogen.sh
Patch0:		axis2c-src-0.91-missing_headers.diff
Patch1:		axis2c-prglibdir.diff
Patch2:		axis2c-correct_mod_names.diff
Patch3:		axis2c-mdv_conf.diff
Patch4:		axis2c-no_werror.diff
Patch5:		axis2c-prgbindir.diff
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	apr-devel
BuildRequires:	openssl-devel
BuildRequires:	libxml2-devel
BuildRequires:	file

%description
Axis2/C is an effort to implement Axis2 architecture, in C. Axis2/C can be used
to provide and consume Web Services.

%package -n	%{libname}
Summary:	Axis2/C is an effort to implement Axis2 architecture, in C
Group:          System/Libraries

%description -n	%{libname}
Axis2/C is an effort to implement Axis2 architecture, in C. Axis2/C can be used
to provide and consume Web Services.

%package -n	%{develname}
Summary:	Static library and header files for the axis2 library
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname axis2c 0 -d}

%description -n	%{develname}
Axis2/C is an effort to implement Axis2 architecture, in C. Axis2/C can be used
to provide and consume Web Services.

This package contains the static libevent library and its header files
needed to compile applications such as stegdetect, etc.

%package -n	apache-mod_axis2
Summary:	Apache module that filter ActiveX on a proxy
Group:		System/Servers
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
Requires:	%{libname} = %{version}-%{release}

%description -n	apache-mod_axis2
Axis2/C is an effort to implement Axis2 architecture, in C. Axis2/C can be used
to provide and consume Web Services.

This package contains the Axis2/C apache module.

%package	docs
Summary:	Documentation for Axis2/C
Group:		System/Servers

%description	docs
Axis2/C is an effort to implement Axis2 architecture, in C. Axis2/C can be used
to provide and consume Web Services.

This package contains the documentation for Axis2/C.

%package	tools
Summary:	Axis2/C tools
Group:		System/Servers
Requires:	%{libname} = %{version}-%{release}

%description	tools
Axis2/C is an effort to implement Axis2 architecture, in C. Axis2/C can be used
to provide and consume Web Services.

This package contains various tools for Axis2/C.

%prep

%setup -q -n axis2c-src-%{version}

#for i in `find -type f -name "Makefile.am"`; do
#    perl -pi -e "s|^prglibdir=\\\$\(prefix\)/modules/|prglibdir=\\\$\(libdir\)/axis2c/modules/|g" $i
#    perl -pi -e "s|^prglibdir=\\\$\(prefix\)/services/|prglibdir=\\\$\(libdir\)/axis2c/services/|g" $i
#done

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p0
%patch4 -p1
%patch5 -p0

cp %{SOURCE2} A64_mod_axis2.conf

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

libtoolize --copy --force
cp %{SOURCE3} ./autogen.sh
chmod 755 ./autogen.sh
sh ./autogen.sh

chmod 644 COPYING CREDITS LICENSE

%build
if [ -x %{_bindir}/apr-config ]; then
    APR_CONFIG="%{_bindir}/apr-config"
else
    APR_CONFIG="%{_bindir}/apr-1-config"
fi

APACHE_INCLUDES="`%{_sbindir}/apxs -q INCLUDEDIR`"
APR_INCLUDES="`$APR_CONFIG --includedir`"

%configure2_5x \
    --enable-libxml2 \
    --enable-multi-thread \
    --enable-openssl \
    --with-apache2=$APACHE_INCLUDES \
    --with-apr=$APR_INCLUDES

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%makeinstall_std

install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}/var/log/%{name}
install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_sbindir}

mv %{buildroot}%{_bindir}/axis2_http_server %{buildroot}%{_sbindir}/
mv %{buildroot}%{_prefix}/axis2.xml %{buildroot}%{_sysconfdir}/%{name}/

echo "# put something here..." > axiscpp.conf
install -m0644 axiscpp.conf %{buildroot}%{_sysconfdir}/%{name}/

# move the apache module in place
mv %{buildroot}%{_libdir}/mod_axis2.* %{buildroot}%{_libdir}/apache-extramodules/
rm -f %{buildroot}%{_libdir}/apache-extramodules/*.a
rm -f %{buildroot}%{_libdir}/apache-extramodules/*.la

install -m0644 A64_mod_axis2.conf %{buildroot}%{_sysconfdir}/httpd/modules.d/A64_mod_axis2.conf

# fix docs
cp axiom/ChangeLog ChangeLog.axiom
cp axiom/NEWS NEWS.axiom
cp axiom/README README.axiom
cp guththila/README README.guththila

# cleanup
rm -rf %{buildroot}%{_prefix}/logs
rm -rf %{buildroot}%{_prefix}/docs
rm -f %{buildroot}%{_prefix}/AUTHORS
rm -f %{buildroot}%{_prefix}/COPYING
rm -f %{buildroot}%{_prefix}/CREDITS
rm -f %{buildroot}%{_prefix}/INSTALL
rm -f %{buildroot}%{_prefix}/LICENSE
rm -f %{buildroot}%{_prefix}/NEWS
rm -f %{buildroot}%{_prefix}/README
rm -f %{buildroot}%{_prefix}/config.guess
rm -f %{buildroot}%{_prefix}/config.sub
rm -f %{buildroot}%{_prefix}/depcomp
rm -f %{buildroot}%{_prefix}/install-sh
rm -f %{buildroot}%{_prefix}/ltmain.sh
rm -f %{buildroot}%{_prefix}/missing
rm -f %{buildroot}%{_prefix}/NOTICE
rm -f %{buildroot}%{_datadir}/AUTHORS
rm -f %{buildroot}%{_datadir}/COPYING
rm -f %{buildroot}%{_datadir}/INSTALL
rm -f %{buildroot}%{_datadir}/LICENSE
rm -f %{buildroot}%{_datadir}/NEWS
rm -f %{buildroot}%{_datadir}/README

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%post -n apache-mod_axis2
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun -n apache-mod_axis2
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files -n %{libname}
%defattr(-,root,root)
%doc COPYING CREDITS LICENSE *.axiom *.guththila
%dir %{_sysconfdir}/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/axis2.xml
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/axiscpp.conf
%dir %{_libdir}/%{name}/modules
%dir %{_libdir}/%{name}/modules/addressing
%dir %{_libdir}/%{name}/modules/logging
%{_libdir}/%{name}/modules/addressing/module.xml
%{_libdir}/%{name}/modules/addressing/*.so
%{_libdir}/%{name}/modules/logging/*.so
%{_libdir}/%{name}/modules/logging/module.xml
%{_libdir}/*.so.*
%attr(0755,root,root) %{_sbindir}/axis2_http_server
%dir /var/log/%{name}

%files -n %{develname}
%defattr(-,root,root)
%dir %{_includedir}/axis2-1.1
%dir %{_includedir}/axis2-1.1/platforms
%dir %{_includedir}/axis2-1.1/platforms/unix
%dir %{_includedir}/axis2-1.1/platforms/windows
%{_includedir}/axis2-1.1/platforms/*.h
%{_includedir}/axis2-1.1/platforms/unix/*.h
%{_includedir}/axis2-1.1/platforms/windows/*.h
%{_includedir}/axis2-1.1/*.h
%{_libdir}/%{name}/modules/addressing/*.a
%{_libdir}/%{name}/modules/addressing/*.la
%{_libdir}/%{name}/modules/logging/*.a
%{_libdir}/%{name}/modules/logging/*.la
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/pkgconfig/axis2c.pc

%files -n apache-mod_axis2
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/A64_mod_axis2.conf
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_axis2.so

%files tools
%defattr(-,root,root)
%doc tools/tcpmon/README
%attr(0755,root,root) %{_bindir}/tcpmon

%files docs
%defattr(-,root,root)
%doc docs/*
