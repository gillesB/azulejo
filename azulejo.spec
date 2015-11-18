%define name azulejo
%define git_commit 77e73f9
%define version 0.0~git%{git_commit}
%define release 1

Summary: Window resizing and tiling utility
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{git_commit}.tar.gz
License: UNKNOWN
Group: User Interface/X
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Gilles Baatz <baatzgilles@gmail.com>

%description
Azulejo was originally a port (an attempt to) of winsplit revolution's
functionality to *nix desktop environments. This fork also adds Compiz's Put
feature to the functionality. Short: it moves, with or without resizing, windows
using keyboard shortcuts.

It has been tested on GNOME 2, XFCE and Openbox, but it should work on many
other desktop environments.

%prep
%setup -n %{name}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
