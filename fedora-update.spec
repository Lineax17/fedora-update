Name:           fedora-update
Version:        1.1
Release:        4%{?dist}
Summary:        Simple Fedora system update script

License:        MIT
URL:            https://github.com/Lineax17/fedora-update
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       bash

%description
This package provides the "fedora-update" command, a small Bash script that
runs a full system upgrade on Fedora with a single command.

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
install -m 0755 fedora-update-silent.sh %{buildroot}%{_bindir}/fedora-update-silent.sh
install -m 0755 fedora-update-verbose.sh %{buildroot}%{_bindir}/fedora-update-verbose.sh
install -m 0644 LICENSE %{buildroot}%{_datadir}/licenses/%{name}/LICENSE
install -m 0644 README.md %{buildroot}%{_datadir}/doc/%{name}/README.md


%files
%license LICENSE
%doc README.md
%{_bindir}/fedora-update
%{_bindir}/fedora-update-silent.sh
%{_bindir}/fedora-update-verbose.sh

%changelog
* Tue Oct 18 2025 Lineax17 <lineax17@gmail.com> - 1.1-4
- Adding storage cleanup
