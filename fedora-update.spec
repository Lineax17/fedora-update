Name:           fedora-update
Version:        1.2.1
Release:        1%{?dist}
Summary:        Simple Fedora system update script

License:        MIT
URL:            https://github.com/Lineax17/fedora-update
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       bash

%description
This package provides the "fedora-update" command, a small Bash script that
runs a full system upgrade on Fedora with a single command. Supports both
silent mode (default with spinner) and verbose mode (-l flag) for detailed output.

%prep
%setup -q

%build
# Nothing to build - this is just a shell script

%install
# Install script to /usr/bin (using RPM macro %{_bindir})
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/licenses/%{name}
mkdir -p %{buildroot}%{_datadir}/doc/%{name}

install -m 0755 fedora-update.sh %{buildroot}%{_bindir}/fedora-update
install -m 0644 LICENSE %{buildroot}%{_datadir}/licenses/%{name}/LICENSE
install -m 0644 README.md %{buildroot}%{_datadir}/doc/%{name}/README.md


%files
%license LICENSE
%doc README.md
%{_bindir}/fedora-update

%changelog
* Sun Nov 10 2025 Lineax17 <lineax17@gmail.com> - 1.2.1-1
- Merged silent and verbose scripts into single unified script
- Improved code maintainability and reduced duplication
- Add documentation
- Add --help flag
