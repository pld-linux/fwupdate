#
# Conditional build:
%bcond_with	pesign		# EFI apps signing with pesign
#
Summary:	Tools to manage UEFI firmware updates
Summary(pl.UTF-8):	Narzędzia do zarządzania aktualizacjami firmware'u przez UEFI
Name:		fwupdate
Version:	11
Release:	1
License:	GPL v2
Group:		Libraries
#Source0Download: https://github.com/rhboot/fwupdate/releases
Source0:	https://github.com/rhboot/fwupdate/releases/download/%{version}/%{name}-%{version}.tar.bz2
# Source0-md5:	ec833aea7a59c17128f1bdf521a9ac9f
URL:		https://github.com/rhinstaller/fwupdate
BuildRequires:	efivar-devel >= 0.33
BuildRequires:	gnu-efi >= 3.0.5
BuildRequires:	libsmbios-devel
%{?with_pesign:BuildRequires:	pesign}
BuildRequires:	popt-devel
BuildRequires:	sed >= 4.0
Requires:	%{name}-libs = %{version}-%{release}
#Requires(post):	efibootmgr >= 0.13
ExclusiveArch:	%{ix86} %{x8664} x32 %{arm} aarch64 ia64
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
Requires:	efivar-libs >= 0.33

%description libs
Library to manage UEFI firmware updates.

%description libs -l pl.UTF-8
Biblioteka do zarządzania aktualizacjami firmware'u przez UEFI.

%package devel
Summary:	Header files for libfwup library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki libfwup
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	efivar-devel >= 0.33

%description devel
Header files for libfwup library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki libfwup.

%package -n bash-completion-fwupdate
Summary:	Bash completion for fwupdate command
Summary(pl.UTF-8):	Bashowe uzupełnianie parametrów polecenia fwupdate
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion >= 2.0

%description -n bash-completion-fwupdate
Bash completion for fwupdate command.

%description -n bash-completion-fwupdate -l pl.UTF-8
Bashowe uzupełnianie parametrów polecenia fwupdate.

%prep
%setup -q

%if %{without pesign}
%{__sed} -i -e 's/pesign/cp $< $@ \&\& : &/' efi/Makefile
%endif

%ifarch x32
%{__sed} -i -e '/^BUILDFLAGS\s*:= /s/:= /:= -m64 /' efi/Makefile
%endif

%build
%{__make} -j1 \
%ifarch x32
	ARCH=x86_64 \
%endif
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags}" \
	EFIDIR=%{efidir} \
	GNUEFIDIR=%{_libdir} \
	libdir=%{_libdir} \
	libexecdir=%{_libexecdir}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -j1 install \
%ifarch x32
	ARCH=x86_64 \
%endif
	DESTDIR=$RPM_BUILD_ROOT \
	EFIDIR=%{efidir} \
	libdir=%{_libdir} \
	libexecdir=%{_libexecdir}

# fix location
install -d $RPM_BUILD_ROOT%{systemdunitdir}
%{__mv} $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system/*.service $RPM_BUILD_ROOT%{systemdunitdir}

# empty
%{__rm} $RPM_BUILD_ROOT%{_localedir}/en/*.po

# debuginfo installed by make install?
%{__rm} -r $RPM_BUILD_ROOT{%{_prefix}/lib/debug,%{_prefix}/src/debug}

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
%doc TODO
%attr(755,root,root) %{_bindir}/fwupdate
%dir %{_libexecdir}/fwupdate
%attr(755,root,root) %{_libexecdir}/fwupdate/cleanup
%{systemdunitdir}/fwupdate-cleanup.service
%{_mandir}/man1/fwupdate.1*
%dir /boot/efi/EFI/%{efidir}
%ifarch %{ix86}
/boot/efi/EFI/%{efidir}/fwupia32.efi
%endif
%ifarch %{x8664} x32
/boot/efi/EFI/%{efidir}/fwupx64.efi
%endif
%ifarch %{arm}
/boot/efi/EFI/%{efidir}/fwuparm.efi
%endif
%ifarch aarch64
/boot/efi/EFI/%{efidir}/fwupaa64.efi
%endif
%ifnarch %{ix86} %{x8664} x32 %{arm} aarch64
/boot/efi/EFI/%{efidir}/fwupdate.efi
%endif
%dir /boot/efi/EFI/%{efidir}/fw

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfwup.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libfwup.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfwup.so
%{_includedir}/fwup.h
%{_includedir}/fwup-version.h
%{_pkgconfigdir}/fwup.pc
%{_mandir}/man3/fwup_*.3*
%{_mandir}/man3/libfwup.3*
%{_mandir}/man3/libfwup.h.3*

%files -n bash-completion-fwupdate
%defattr(644,root,root,755)
%{_datadir}/bash-completion/completions/fwupdate
