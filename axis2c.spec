%define	major 0
%define libname	%mklibname axis2c %{major}

Summary:	Axis2/C is an effort to implement Axis2 architecture, in C
Name:		axis2c
Version:	0.91
Release:	%mkrel 2
Group:		System/Libraries
License:	Apache License
URL:		http://ws.apache.org/axis2/c/
Source0:	http://www.apache.org/dist/ws/axis2/c/0_91/axis2c-src-%{version}.tar.gz
Source1:	http://www.apache.org/dist/ws/axis2/c/0_91/axis2c-src-%{version}.tar.gz.asc
Source2:	A64_mod_axis2.conf
Patch0:		axis2c-src-0.91-missing_headers.diff
Patch1:		axis2c-src-0.91-prglibdir.diff
Patch2:		axis2c-src-0.91-mdv_conf.diff
Patch3:		axis2c-src-0.91-mod_axis2.diff
Patch4:		axis2c-src-0.91-mod_addr.diff
BuildRequires:	apache-devel >= 2.0.54
BuildRequires:	apr-devel
BuildRequires:	openssl-devel
BuildRequires:	libxml2-devel
BuildRequires:	file
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
Axis2/C is an effort to implement Axis2 architecture, in C. Axis2/C can be used
to provide and consume Web Services.

%package -n	%{libname}
Summary:	Axis2/C is an effort to implement Axis2 architecture, in C
Group:          System/Libraries

%description -n	%{libname}
Axis2/C is an effort to implement Axis2 architecture, in C. Axis2/C can be used
to provide and consume Web Services.

%package -n	%{libname}-devel
Summary:	Static library and header files for the axis2 library
Group:		Development/C
Provides:	lib%{name}-devel = %{version}
Provides:	%{name}-devel = %{version}
Requires:	%{libname} = %{version}-%{release}

%description -n	%{libname}-devel
Axis2/C is an effort to implement Axis2 architecture, in C. Axis2/C can be used
to provide and consume Web Services.

This package contains the static libevent library and its header files
needed to compile applications such as stegdetect, etc.


%package -n	apache-mod_axis2
Summary:	Apache module that filter ActiveX on a proxy
Group:		System/Servers
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.0.54
Requires(pre):	apache >= 2.0.54
Requires:	apache-conf >= 2.0.54
Requires:	apache >= 2.0.54
Requires:	%{libname} = %{version}-%{release}

%description -n	apache-mod_axis2
Axis2/C is an effort to implement Axis2 architecture, in C. Axis2/C can be used
to provide and consume Web Services.

This package contains the Axis2/C apache module.

%prep

%setup -q -n axis2c-src-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p0
%patch3 -p0
%patch4 -p0

cp %{SOURCE2} A64_mod_axis2.conf

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

libtoolize --copy --force
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

# cleanup
rm -rf %{buildroot}%{_prefix}/logs
rm -f %{buildroot}%{_prefix}/AUTHORS
rm -f %{buildroot}%{_prefix}/COPYING
rm -f %{buildroot}%{_prefix}/CREDITS
rm -f %{buildroot}%{_prefix}/INSTALL
rm -f %{buildroot}%{_prefix}/LICENSE
rm -f %{buildroot}%{_prefix}/NEWS
rm -f %{buildroot}%{_prefix}/README

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
%doc COPYING CREDITS LICENSE
%dir %{_sysconfdir}/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/axis2.xml
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/axiscpp.conf
%dir %{_libdir}/%{name}/modules
%dir %{_libdir}/%{name}/modules/addressing
%{_libdir}/%{name}/modules/addressing/module.xml
%{_libdir}/%{name}/modules/addressing/*.so
%{_libdir}/*.so.*
%attr(0755,root,root) %{_sbindir}/axis2_http_server
%dir /var/log/%{name}

%files -n %{libname}-devel
%defattr(-,root,root)
%dir %{_includedir}/platforms
%dir %{_includedir}/platforms/unix
%dir %{_includedir}/platforms/windows
%{_includedir}/platforms/*.h
%{_includedir}/platforms/unix/*.h
%{_includedir}/platforms/windows/*.h
%{_includedir}/*.h
%{_libdir}/%{name}/modules/addressing/*.a
%{_libdir}/%{name}/modules/addressing/*.la
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la

%files -n apache-mod_axis2
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/A64_mod_axis2.conf
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_axis2.so


