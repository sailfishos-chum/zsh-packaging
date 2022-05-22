Name:       zsh
Summary:    The Z shell
# define own version because sometimes OBS fiddles with %%{version}
%define upstream_version 5.9
Version:    %{upstream_version}
Release:    1%{?dist}
Group:      Applications/System
License:    MIT
URL:        https://zsh.sourceforge.io/
Source0:    %{name}-%{version}.tar.bz2
Patch0:     001-disable-failing-tests.patch

BuildRequires: pkgconfig(ncursesw)
BuildRequires: pkgconfig(libpcre)
BuildRequires: gcc
BuildRequires: make
BuildRequires: libcap-devel
BuildRequires: texinfo
BuildRequires: autoconf
# busybox's diff breaks some checks in test suite
BuildConflicts: busybox-symlinks-diffutils
BuildRequires: gnu-diffutils
Requires(post): grep
Requires(postun): coreutils

Provides: /bin/zsh

%define source_date_epoch_from_changelog 1
%define clamp_mtime_to_source_date_epoch 1
%define use_source_date_epoch_as_buildtime 1
%define _buildhost SailfishSDK

%description
Zsh is a UNIX command interpreter (shell) usable as an interactive login shell
and as a shell script command processor. Of the standard shells, zsh most
closely resembles the Korn shell (ksh), but includes many enhancements.  Among
these features are command line editing, built-in spelling correction,
programmable command completion, shell functions (with autoloading), and a
history mechanism.

%if "%{?vendor}" == "chum"
PackageName: Z Shell
Type: console-application
Custom:
  Repo: https://github.com/sailfishos-chum/zsh-packaging
Url:
  Homepage: https://zsh.sourceforge.io
Categories:
  - System
  - Utility
PackagerName: takimata
Icon: https://github.com/Zsh-art/logo/raw/main/png/color_vertical_icon.png
%endif

%prep
%autosetup -p1 -n %{name}-%{version}/zsh

%build
./Util/preconfig
export CPPFLAGS="$CPPFLAGS -O -D_FORTIFY_SOURCE=2"
export CFLAGS="$CFLAGS -fPIE -fstack-protector-strong -fstack-clash-protection"
export LIBLDFLAGS="-z lazy"
export EXELDFLAGS="-pie"
%configure \
  --with-tcsetpgrp \
  --enable-pcre \
  --enable-site-fndir=%{_datadir}/zsh/site-functions \
  --enable-ldflags="-g -Wl,-z,relro,-z,now -Wl,--as-needed"

# TODO doc fails to build because of missing dependency groff
%make_build all

%check
# Run the testsuite
make check

%install
rm -rf %{buildroot}
# broken due to broken doc build
# %%make_install
# do it manually instead:
make DESTDIR=%{buildroot} install.bin
rm %{buildroot}%{_bindir}/zsh-*
mkdir -p "%{buildroot}/bin/"
ln -s "%{_bindir}/%{name}" "%{buildroot}/bin/%{name}"

make DESTDIR=%{buildroot} install.modules
make DESTDIR=%{buildroot} install.fns

# avoid invalid Requires to be generated
for f in test-repo-git-rebase-{apply,merge}; do
    sed -i -e 's!/usr/local/bin/zsh!%{_bindir}/zsh!' $RPM_BUILD_ROOT%{_datadir}/zsh/%{version}/functions/$f
    chmod +x $RPM_BUILD_ROOT%{_datadir}/zsh/%{version}/functions/$f
done

%files
%defattr(-,root,root,-)
%{_bindir}/%{name}
/bin/%{name}
%{_libdir}/%{name}/
%{_datadir}/%{name}

%post
if [ "$1" -eq 1 ]; then
  if [ -f %{_sysconfdir}/shells ]; then
    grep -qxF "%{_bindir}/%{name}" %{_sysconfdir}/shells || echo "%{_bindir}/%{name}" >> %{_sysconfdir}/shells
    grep -qxF "/bin/%{name}" %{_sysconfdir}/shells || echo "/bin/%{name}" >> %{_sysconfdir}/shells
  else
    echo "%{_bindir}/%{name}" > %{_sysconfdir}/shells
    echo "/bin/%{name}" >> %{_sysconfdir}/shells
  fi
fi

%postun
if [ "$1" -eq 0 ] && [ -f %{_sysconfdir}/shells ]; then
  sed -i '\!^%{_bindir}/%{name}$!dq' %{_sysconfdir}/shells
  sed -i '\!^/bin/%{name}$!dq' %{_sysconfdir}/shells
fi

%changelog
* Thu May 19 2022 takimata <takimata@gmx.de> - 5.9-1
- Stable security release with many bug fixes and several new features
* Mon Feb 14 2022 takimata <takimata@gmx.de> - 5.8.1-2
- Security and bugfix release
- PROMPT_SUBST expansion is no longer performed on arguments to prompt expansion sequences such as %F
* Wed Aug 18 2021 takimata <takimata@gmx.de> - 5.8-1
- Initial packaging for Chum
