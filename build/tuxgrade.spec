Name:           tuxgrade
Version:        3.0.0
Release:        1%{?dist}
Summary:        Automated system upgrade script for several Linux distributions

License:        MIT
URL:            https://github.com/Lineax17/tuxgrade
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       python3 >= 3.10
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
Automated system upgrade script for several Linux distributions with support 
for APT, DNF, Flatpak, Snap, Homebrew and NVIDIA akmods. Provides both silent mode
(default with ASCII animation) and verbose mode (--verbose flag) for
detailed output.

Alternative commands: fedora-upgrade, fuck

%prep
%setup -q

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files '*'

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/*
%{_bindir}/tuxgrade
%{_bindir}/fedora-update
%{_bindir}/fedora-upgrade
%{_bindir}/fuck

%changelog
* Sat Feb 07 2026 Lineax17 <lineax17@gmail.com> - 3.0.0-1
- change branding to tuxgrade
- add multidistro-support including following distros:
    - debian
    - linuxmint
    - ubuntu
    - pop 
    - zorin
    - fedora
    - rhel
    - rocky 
    - almalinux

* Sat Jan 03 2026 Lineax17 <lineax17@gmail.com> - 2.0.1-1
- fix minor visual issues
- remove dnf5 hardlock to enable dnf4 support (tested with dnf 4.19 on Fedora 40)

* Sat Dec 27 2025 Lineax17 <lineax17@gmail.com> - 2.0.0-1
- Complete Python rewrite for better maintainability
- Improved error handling and modular architecture
