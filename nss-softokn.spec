%global nspr_version 4.8.7
%global nss_name nss
%global nss_util_version 3.12.9
%global unsupported_tools_directory %{_libdir}/nss/unsupported-tools
%global saved_files_dir %{_libdir}/nss/saved

# Produce .chk files for the final stripped binaries
%define __spec_install_post \
    %{?__debug_package:%{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
    $RPM_BUILD_ROOT/%{unsupported_tools_directory}/shlibsign -i $RPM_BUILD_ROOT/%{_libdir}/libsoftokn3.so \
    $RPM_BUILD_ROOT/%{unsupported_tools_directory}/shlibsign -i $RPM_BUILD_ROOT/%{_lib}/libfreebl3.so \
    $RPM_BUILD_ROOT/%{unsupported_tools_directory}/shlibsign -i $RPM_BUILD_ROOT/%{_libdir}/libnssdbm3.so \
%{nil}

Summary:          Network Security Services Softoken Module
Name:             nss-softokn
Version:          3.12.9
Release:          11%{?dist}
License:          MPLv1.1 or GPLv2+ or LGPLv2+
URL:              http://www.mozilla.org/projects/security/pki/nss/
Group:            System Environment/Libraries
Requires:         nspr >= %{nspr_version}
Requires:         nss-util >= %{nss_util_version}
Requires:         nss-softokn-freebl%{_isa} >= %{version}
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:    nspr-devel >= %{nspr_version}
BuildRequires:    nss-util-devel >= %{nss_util_version}
BuildRequires:    sqlite-devel
BuildRequires:    zlib-devel
BuildRequires:    pkgconfig
BuildRequires:    gawk
BuildRequires:    psmisc
BuildRequires:    perl

Source0:          %{name}-%{version}-stripped.tar.bz2
# The nss-softokn tar ball is a subset of nss-{version}-stripped.tar.bz2, 
# Therefore we use the nss-split-softokn.sh script to keep only what we need.
# Download the nss tarball via CVS from the nss project and follow these
# steps to make the tarball for nss-softokn out of the one for nss:
# cvs co nss
# cvs nss-softokn
# cp ../../nss/devel/${version}-stripped.tar.bz2  .
# sh ./nss-split-softokn.sh ${version}
# A file named {name}-{version}-stripped.tar.bz2 should appear
Source1:          nss-split-softokn.sh
Source2:          nss-softokn.pc.in
Source3:          nss-softokn-config.in

Patch1:           add-relro-linker-option.patch
Patch2:           nss-softokn-3.12.4-prelink.patch
Patch3:           nss-softokn-3.12.4-fips-fix.patch
Patch4:           nss-softokn-710298.patch
# Add drbg tests for FIPS validation, patch from upstream
# see: https://bugzilla.mozilla.org/show_bug.cgi?id=695571
# Remove this patch when we rebase to nss 3.13.2
Patch5:           drbg.patch
# Backported from upstream nss 3.13
# See: https://bugzilla.mozilla.org/show_bug.cgi?id=641052
# Remove this patch when we rebase to nss 3.13.2
Patch6:           nss-softokn-748524.patch

%description
Network Security Services Softoken Cryptographic Module

%package freebl
Summary:          Freebl library for the Network Security Services
Group:            System Environment/Base
Conflicts:        nss < 3.12.2.99.3-5
Conflicts:        prelink < 0.4.3

%description freebl
NSS Softoken Cryptographic Module Freelb Library

Install the nss-softokn-freebl package if you need the freebl 
library.

%package freebl-devel
Summary:          Header and Library files for doing development with the Freebl library for NSS
Group:            System Environment/Base
Provides:         nss-softokn-freebl-static = %{version}-%{release}
Requires:         nss-softokn-freebl%{?_isa} = %{version}-%{release}

%description freebl-devel
NSS Softoken Cryptographic Module Freelb Library Development Tools
This package supports special needs of some PKCS #11 module developers and
is otherwise considered private to NSS. As such, the programming interfaces
may change and the usual NSS binary compatibility commitments do not apply.
Developers should rely only on the officially supported NSS public API.

%package devel
Summary:          Development libraries for Network Security Services
Group:            Development/Libraries
Requires:         nss-softokn%{?_isa} = %{version}-%{release}
Requires:         nss-softokn-freebl-devel%{?_isa} = %{version}-%{release}
Requires:         nspr-devel >= %{nspr_version}
Requires:         nss-util-devel >= %{nss_util_version}
Requires:         pkgconfig
BuildRequires:    nspr-devel >= %{nspr_version}
BuildRequires:    nss-util-devel >= %{nss_util_version}

%description devel
Header and Library files for doing development with Network Security Services.


%prep
%setup -q

%patch1 -p0 -b .relro
%patch2 -p0 -b .prelink
%patch3 -p0 -b .fipsfix
%patch4 -p0 -b .710298
%patch5 -p0 -b .747053
%patch6 -p0 -b .748524

%build

FREEBL_NO_DEPEND=1
export FREEBL_NO_DEPEND

FREEBL_USE_PRELINK=1
export FREEBL_USE_PRELINK

# Enable compiler optimizations and disable debugging code
BUILD_OPT=1
export BUILD_OPT

# Uncomment to disable optimizations
#RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed -e 's/-O2/-O0/g'`
#export RPM_OPT_FLAGS

# Generate symbolic info for debuggers
XCFLAGS=$RPM_OPT_FLAGS
export XCFLAGS

PKG_CONFIG_ALLOW_SYSTEM_LIBS=1
PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1

export PKG_CONFIG_ALLOW_SYSTEM_LIBS
export PKG_CONFIG_ALLOW_SYSTEM_CFLAGS

NSPR_INCLUDE_DIR=`/usr/bin/pkg-config --cflags-only-I nspr | sed 's/-I//'`
NSPR_LIB_DIR=`/usr/bin/pkg-config --libs-only-L nspr | sed 's/-L//'`

export NSPR_INCLUDE_DIR
export NSPR_LIB_DIR

NSS_INCLUDE_DIR=`/usr/bin/pkg-config --cflags-only-I nss-util | sed 's/-I//'`
NSS_LIB_DIR=`/usr/bin/pkg-config --libs-only-L nss-util | sed 's/-L//'`

export NSS_INCLUDE_DIR
export NSS_LIB_DIR

NSS_USE_SYSTEM_SQLITE=1
export NSS_USE_SYSTEM_SQLITE

%ifarch x86_64 ppc64 ia64 s390x sparc64
USE_64=1
export USE_64
%endif

# Compile softokn plus needed support
%{__make} -C ./mozilla/security/coreconf
%{__make} -C ./mozilla/security/dbm
%{__make} -C ./mozilla/security/nss

# Set up our package file
# The nspr_version and nss_util_version globals used here
# must match the ones nss-softokn has for its Requires. 
%{__mkdir_p} ./mozilla/dist/pkgconfig
%{__cat} %{SOURCE2} | sed -e "s,%%libdir%%,%{_libdir},g" \
                          -e "s,%%prefix%%,%{_prefix},g" \
                          -e "s,%%exec_prefix%%,%{_prefix},g" \
                          -e "s,%%includedir%%,%{_includedir}/nss3,g" \
                          -e "s,%%NSPR_VERSION%%,%{nspr_version},g" \
                          -e "s,%%NSSUTIL_VERSION%%,%{nss_util_version},g" \
                          -e "s,%%SOFTOKEN_VERSION%%,%{version},g" > \
                          ./mozilla/dist/pkgconfig/nss-softokn.pc

SOFTOKEN_VMAJOR=`cat mozilla/security/nss/lib/softoken/softkver.h | grep "#define.*SOFTOKEN_VMAJOR" | awk '{print $3}'`
SOFTOKEN_VMINOR=`cat mozilla/security/nss/lib/softoken/softkver.h | grep "#define.*SOFTOKEN_VMINOR" | awk '{print $3}'`
SOFTOKEN_VPATCH=`cat mozilla/security/nss/lib/softoken/softkver.h | grep "#define.*SOFTOKEN_VPATCH" | awk '{print $3}'`

export SOFTOKEN_VMAJOR 
export SOFTOKEN_VMINOR 
export SOFTOKEN_VPATCH

%{__cat} %{SOURCE3} | sed -e "s,@libdir@,%{_libdir},g" \
                          -e "s,@prefix@,%{_prefix},g" \
                          -e "s,@exec_prefix@,%{_prefix},g" \
                          -e "s,@includedir@,%{_includedir}/nss3,g" \
                          -e "s,@MOD_MAJOR_VERSION@,$SOFTOKEN_VMAJOR,g" \
                          -e "s,@MOD_MINOR_VERSION@,$SOFTOKEN_VMINOR,g" \
                          -e "s,@MOD_PATCH_VERSION@,$SOFTOKEN_VPATCH,g" \
                          > ./mozilla/dist/pkgconfig/nss-softokn-config

chmod 755 ./mozilla/dist/pkgconfig/nss-softokn-config


# enable the following line to force a test failure
# find ./mozilla -name \*.chk | xargs rm -f

#
# We can't run a subset of the tests because the tools have
# dependencies on nss libraries outside of softokn. 
# Let's leave this as a place holder.
#


%install

%{__rm} -rf $RPM_BUILD_ROOT

# There is no make install target so we'll do it ourselves.

%{__mkdir_p} $RPM_BUILD_ROOT/%{_includedir}/nss3
%{__mkdir_p} $RPM_BUILD_ROOT/%{_bindir}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_lib}
%{__mkdir_p} $RPM_BUILD_ROOT/%{unsupported_tools_directory}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}/pkgconfig
%{__mkdir_p} $RPM_BUILD_ROOT/%{saved_files_dir}

# Copy the binary libraries we want
for file in libsoftokn3.so libnssdbm3.so
do
  %{__install} -p -m 755 mozilla/dist/*.OBJ/lib/$file $RPM_BUILD_ROOT/%{_libdir}
done

# Because libcrypt depends on libfreebl3.so, it is special
# so we install it in /lib{64}, keeping a symbolic link to it
# back in /usr/lib{64} to keep everyone else working
for file in libfreebl3.so
do
  %{__install} -p -m 755 mozilla/dist/*.OBJ/lib/$file $RPM_BUILD_ROOT/%{_lib}
  ln -sf ../../%{_lib}/libfreebl3.so $RPM_BUILD_ROOT/%{_libdir}/libfreebl3.so
done

# Make sure chk files can be found in both places
for file in libfreebl3.chk
do
  ln -s ../../%{_lib}/$file $RPM_BUILD_ROOT/%{_libdir}/$file
done

# Copy the binaries we ship as unsupported
for file in shlibsign
do
  %{__install} -p -m 755 mozilla/dist/*.OBJ/bin/$file $RPM_BUILD_ROOT/%{unsupported_tools_directory}
done

# Copy the include files we want
for file in mozilla/dist/public/nss/*.h
do
  %{__install} -p -m 644 $file $RPM_BUILD_ROOT/%{_includedir}/nss3
done

# Copy some freebl include files we also want
for file in blapi.h alghmac.h
do
  %{__install} -p -m 644 mozilla/dist/private/nss/$file $RPM_BUILD_ROOT/%{_includedir}/nss3
done

# Copy the static freebl library
for file in libfreebl.a
do
%{__install} -p -m 644 mozilla/dist/*.OBJ/lib/$file $RPM_BUILD_ROOT/%{_libdir}
done

# Copy the package configuration files
%{__install} -p -m 644 ./mozilla/dist/pkgconfig/nss-softokn.pc $RPM_BUILD_ROOT/%{_libdir}/pkgconfig/nss-softokn.pc
%{__install} -p -m 755 ./mozilla/dist/pkgconfig/nss-softokn-config $RPM_BUILD_ROOT/%{_bindir}/nss-softokn-config

%clean
%{__rm} -rf $RPM_BUILD_ROOT


%post
/sbin/ldconfig >/dev/null 2>/dev/null

%postun
/sbin/ldconfig >/dev/null 2>/dev/null

%files
%defattr(-,root,root)
%{_libdir}/libnssdbm3.so
%{_libdir}/libnssdbm3.chk
%{_libdir}/libsoftokn3.so
%{_libdir}/libsoftokn3.chk
# shared with nss-tools
%dir %{_libdir}/nss
%dir %{saved_files_dir}
%dir %{unsupported_tools_directory}
%{unsupported_tools_directory}/shlibsign

%files freebl
%defattr(-,root,root)
/%{_lib}/libfreebl3.so
/%{_lib}/libfreebl3.chk
# and these symbolic links
%{_libdir}/libfreebl3.so
%{_libdir}/libfreebl3.chk

%files freebl-devel
%defattr(-,root,root)
%{_libdir}/libfreebl.a
%{_includedir}/nss3/blapi.h
%{_includedir}/nss3/blapit.h
%{_includedir}/nss3/alghmac.h

%files devel
%defattr(-,root,root)
%{_libdir}/pkgconfig/nss-softokn.pc
%{_bindir}/nss-softokn-config

# co-owned with nss
%dir %{_includedir}/nss3
#
# The following headers are those exported public in
# mozilla/security/nss/lib/freebl/manifest.mn and
# mozilla/security/nss/lib/softoken/manifest.mn
#
# The following list is short because many headers, such as
# the pkcs #11 ones, have been provided by nss-util-devel
# which installed them before us.
#
%{_includedir}/nss3/ecl-exp.h
%{_includedir}/nss3/hasht.h
%{_includedir}/nss3/sechash.h
%{_includedir}/nss3/nsslowhash.h
%{_includedir}/nss3/secmodt.h
%{_includedir}/nss3/shsign.h

%changelog
* Thu Oct 27 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-11
- Bug 748524 - On NSS_NoDB_Init don't try to open pkcs11.txt or secmod.db

* Mon Oct 24 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-10
- Bug 747053 - FIPS changes for NSS, more DRBG tests

* Tue Sep 27 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-9
- Add relro support for executables and shared libraries

* Mon Jul 25 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-8
- Include the patch

* Mon Jul 25 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-7
- Fix the tag

* Fri Jul 22 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-5
- Add partial RELRO support as a security enhancement

* Thu Jun 23 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-5
- Retagging to pick up latest patch - Resolves: rhbz#710298

* Thu Jun 23 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-4
- Resolves: rhbz#710298 - fix intel optimized aes code to handle case where input and ouput are in the same buffer

* Sun Feb 27 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-3
- Add requires nss-softokn-freebl-devel to devel

* Fri Feb 04 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-2
- Add headers for nss-softokn-freebl-devel and expand the description

* Mon Jan 17 2011 Elio Maldonado <emaldona@redhat.com> - 3.12.9-1
- Update to 3.12.9
- Enable Intel AES Hardware optimizations

* Fri Oct 01 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.8-1
- Update to 3.12.8

* Thu Aug 26 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.7-1.1
- Retagging to remove an obsolete file

* Thu Aug 26 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.7-1
- Update to 3.12.7

* Thu Aug 05 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-19
- Turn off Intel AES optimizations

* Mon Jun 08 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.6-2.1
- Don't enable FIPS when CONFIG_CRYPTO_FIPS=n
- Fix typo in the package description
- Fix capitalization error in prelink conflict statement
- Require nspr 4.8.4

* Wed Apr 21 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-17
- Updated prelink patch

* Thu Apr 15 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-16
- allow prelink of softoken and freebl. Change the verify code to use
  prelink -u if prelink is installed. Fix by Robert Relyea

* Mon Jan 18 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-11
- Move libfreebl3.so and its .chk file to /lib{64} keeping
- symbolic links to them in /usr/lib{64} so as not break others

* Mon Jan 18 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-10.3
- fix broken global

* Sun Jan 17 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-10.2
- rebuilt for RHEL-6-test-build

* Fri Jan 15 2010 Elio Maldonado <emaldona@redhat.com> - 3.12.4-10.1
- Update to 3.12.4, reenable installing and pick up fixes from F-12
* Thu Aug 19 2009 Elio Maldonado <emaldona@redhat.com> 3.12.3.99.3-8.1
- Disable installing until conflicts are relsoved
* Thu Aug 19 2009 Elio Maldonado <emaldona@redhat.com> 3.12.3.99.3-8
- Initial build
