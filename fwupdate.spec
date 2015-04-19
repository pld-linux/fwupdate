#
# Conditional build:
%bcond_with	pesign		# EFI apps signing with pesign
#
Summary:	Tools to manage UEFI firmware updates
Summary(pl.UTF-8):	Narzędzia do zarządzania aktualizacjami firmware'u przez UEFI
Name:		fwupdate
Version:	0.2
Release:	1
License:	GPL v2
Group:		Libraries
Source0:	https://github.com/rhinstaller/fwupdate/archive/10def9bb08c85761ed7fe22bc458cbc760b99d42/%{name}-%{version}.tar.gz
# Source0-md5:	d610a0f98dc262eaa71fb2891ba46ad9
Patch0:		%{name}-open.patch
URL:		https://github.com/rhinstaller/fwupdate
BuildRequires:	efivar-devel >= 0.16
BuildRequires:	gnu-efi
%{?with_pesign:BuildRequires:	pesign}
BuildRequires:	popt-devel
BuildRequires:	sed >= 4.0
Requires:	%{name}-libs = %{version}-%{release}
#Requires(post):	efibootmgr >= 0.11.0
ExclusiveArch:	%{ix86} %{x8664} x32 arm aarch64 ia64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		efidir		pld

%description
fwupdate provides a simple command line interface to the UEFI firmware
updates.

%description -l pl.UTF-8
fwupdate zapewnia prosty interfejs linii poleceń do aktualizacji
firmware'u przez UEFI.

%package libs
Summary:	Library to manage UEFI firmware updates
Summary(pl.UTF-8):	Biblioteka do zarządzania aktualizacjami firmware'u przez UEFI
Group:		Libraries
Requires:	efivar-libs >= 0.16

%description libs
Library to manage UEFI firmware updates.

%description libs -l pl.UTF-8
Biblioteka do zarządzania aktualizacjami firmware'u przez UEFI.

%package devel
Summary:	Header files for libfwup library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki libfwup
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	efivar-devel >= 0.16

%description devel
Header files for libfwup library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki libfwup.

%prep
%setup -q -n fwupdate-10def9bb08c85761ed7fe22bc458cbc760b99d42
%patch0 -p1

%{__sed} -i -e 's,/usr/lib64\(/gnuefi\)\?,%{_libdir},g' efi/Makefile
%if %{without pesign}
%{__sed} -i -e 's/pesign/cp $< $@ \&\& : &/' efi/Makefile
%endif

%build
%{__make} \
%ifarch x32
	ARCH=x86_64 \
%endif
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags}" \
	EFIDIR=%{efidir} \
	libdir=%{_libdir}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
%ifarch x32
	ARCH=x86_64 \
%endif
	DESTDIR=$RPM_BUILD_ROOT \
	EFIDIR=%{efidir} \
	libdir=$RPM_BUILD_ROOT%{_libdir}

# empty
%{__rm} $RPM_BUILD_ROOT%{_localedir}/en/*.po

%clean
rm -rf $RPM_BUILD_ROOT

%if 0
# Fedora script below - but we don't want to hardcode /dev/sda
%post
efibootmgr -b 1337 -B >/dev/null || :
efibootmgr -C -b 1337 -d /dev/sda -p 1 -l /EFI/%{efidir}/fwupdate.efi -L "Firmware Update" >/dev/null || :
%endif

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/fwupdate
%dir /boot/efi/EFI/%{efidir}
/boot/efi/EFI/%{efidir}/fwupdate.efi
%dir /boot/efi/EFI/%{efidir}/fw

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfwup.so.0.2

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfwup.so
%{_includedir}/fwup.h
%{_pkgconfigdir}/fwup.pc
