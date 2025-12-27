Name:           fedora-update
Version:        2.0.1
Release:        1%{?dist}
Summary:        Automated system upgrade script for Fedora Linux

License:        MIT
URL:            https://github.com/Lineax17/fedora-update
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       python3 >= 3.10
Requires:       dnf5
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
Automated system upgrade script for Fedora Linux with support for DNF5,
Flatpak, Snap, Homebrew and NVIDIA akmods. Provides both silent mode
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
%{_bindir}/fedora-update
%{_bindir}/fedora-upgrade
%{_bindir}/fuck

%changelog
* Sat Dec 28 2025 Lineax17 <lineax17@gmail.com> - 2.0.1-1
- Fix import paths for proper package installation
- Change relative imports to absolute imports

* Sat Dec 27 2025 Lineax17 <lineax17@gmail.com> - 2.0.0-1
- Complete Python rewrite for better maintainability
- Improved error handling and modular architecture
