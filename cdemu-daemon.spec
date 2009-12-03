
%define version 1.2.0
%define rel	1

Name:		cdemu-daemon
Version:	%version
Summary:	Userspace daemon part of the userspace-cdemu suite
Release:	%mkrel %rel
Source:		http://downloads.sourceforge.net/cdemu/%name-%version.tar.bz2
Source1:	cdemud.init
Source2:	cdemud.sysconfig
Patch1:		cdemu-daemon-1.2.0-mdv-format-security.patch
Group:		Emulators
License:	GPLv2+
URL:		http://cdemu.sourceforge.net/
BuildRoot:	%{_tmppath}/%{name}-root
BuildRequires:	mirage-devel >= %version
BuildRequires:	glib2-devel
BuildRequires:	dbus-glib-devel
BuildRequires:	daemon-devel
BuildRequires:	libao-devel
BuildRequires:	libsysfs-devel
Obsoletes:	dkms-cdemu < 0.9
Requires:	rpm-helper
Requires:	kmod(vhba)
# No actual conflict, but kcdemu works only with old cdemu:
Conflicts:	kcdemu < 0.4.0-5

%description
The daemon receives SCSI commands from kernel module and processes
them, passing the requested data back to the kernel.

Daemon implements the actual virtual device; one instance per each
device registered by kernel module. It uses libMirage, an image
access library that is part of userspace-cdemu suite, for the image
access (e.g. sector reading).

Daemon is controlled through methods that are exposed via D-BUS. It
is written in C and based on GLib (and thus GObjects), but being
controlled over D-BUS, it allows for different clients written in
different languages.

%prep
%setup -q
%patch1 -p1

%build
%configure2_5x
%make

%install
rm -rf %buildroot
%makeinstall_std

install -d -m755 %{buildroot}%{_initrddir}
install -d -m755 %{buildroot}%{_sysconfdir}/sysconfig

install -m755 %SOURCE1 %{buildroot}%{_initrddir}/cdemud
install -m644 %SOURCE2 %{buildroot}%{_sysconfdir}/sysconfig/cdemud

%clean
rm -rf %{buildroot}

%post
%_post_service cdemud

%preun
%_preun_service cdemud

%files
%defattr(-,root,root)
%doc README AUTHORS
%config(noreplace) %{_sysconfdir}/sysconfig/cdemud
%config %{_sysconfdir}/dbus-1/system.d/cdemud-dbus.conf
%{_initrddir}/cdemud
%{_bindir}/cdemud
%{_mandir}/man8/cdemud.8*
