Name:       zsh
Summary:    The Z shell
Version:    5.8
Release:    1%{?dist}
Group:      Applications/System
License:    MIT
URL:        https://git.code.sf.net/p/zsh/code
Source0:    %{name}-%{version}.tar.bz2
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

%description
Zsh is a UNIX command interpreter (shell) usable as an interactive login shell
and as a shell script command processor. Of the standard shells, zsh most
closely resembles the Korn shell (ksh), but includes many enhancements.  Among
these features are command line editing, built-in spelling correction, 
programmable command completion, shell functions (with autoloading), and a 
history mechanism.

%define source_date_epoch_from_changelog 1
%define clamp_mtime_to_source_date_epoch 1
%define use_source_date_epoch_as_buildtime 1
%define _buildhost SailfishSDK

%prep
%autosetup -n %{name}-%{version}/zsh

%build
./Util/preconfig

%configure \
  --with-tcsetpgrp \
  --enable-pcre

# TODO doc fails to build because of missing dependency groff
%make_build all

%check
# Run the testsuite
# fails on aarch64 but not on x86 due to different build env(?) could be a local issue
make check

%install
rm -rf %{buildroot}
# broken due to broken doc build
# %%make_install
# do it manually instead:
make DESTDIR=%{buildroot} install.bin
rm %{buildroot}%{_bindir}/zsh-%{version}
mkdir -p %{buildroot}/bin/
ln -s %{_bindir}/%{name} %{buildroot}/bin/%{name}

make DESTDIR=%{buildroot} install.modules
make DESTDIR=%{buildroot} install.fns

%files
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{_libdir}/%{name}/
%{_datadir}/%{name}/%{version}/*
/bin/%{name}

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
