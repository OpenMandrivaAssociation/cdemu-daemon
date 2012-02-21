
%define version 1.4.0
%define rel	2

Name:		cdemu-daemon
Version:	%version
Summary:	Userspace daemon part of the CDemu suite
Release:	%mkrel %rel
Source:		http://downloads.sourceforge.net/cdemu/%name-%version.tar.gz
Source1:	cdemud-dbus-service
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
# kcdemu works only with old cdemu:
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

install -d -m755 %{buildroot}%{_libdir}
install -d -m755 %{buildroot}%{_sysconfdir}/sysconfig
install -d -m755 %{buildroot}%{_sysconfdir}/modprobe.preload.d
install -d -m755 %{buildroot}%{_datadir}/dbus-1/services
install -d -m755 %{buildroot}/lib/udev/rules.d

install -m755 %SOURCE1 %{buildroot}%{_libdir}/cdemud-dbus-service
install -m644 %SOURCE2 %{buildroot}%{_sysconfdir}/sysconfig/cdemud

echo "vhba" > %{buildroot}%{_sysconfdir}/modprobe.preload.d/cdemud

cat > %{buildroot}%{_datadir}/dbus-1/services/net.sf.cdemu.CDEMUD_Daemon.service <<EOF
[D-BUS Service]
Name=net.sf.cdemu.CDEMUD_Daemon
Exec=%{_libdir}/cdemud-dbus-service
EOF

# TODO: handle this in udev; udev-acl tag is private
cat > %{buildroot}/lib/udev/rules.d/50-cdemud.rules <<EOF
KERNEL=="vhba_ctl", ACTION=="add|change", TAG+="udev-acl"
EOF

%clean
rm -rf %{buildroot}

%post
# remove old system-wide service
if [ -e %{_initrddir}/cdemud ]; then
	chkconfig --del cdemud
fi
# apply new udev rule if module already present
/sbin/modprobe --first-time vhba 2>/dev/null || /sbin/udevadm trigger --sysname-match=vhba_ctl

%files
%defattr(-,root,root)
%doc README AUTHORS
%config(noreplace) %{_sysconfdir}/sysconfig/cdemud
# not normally used, but provided in case the user wants to run cdemud
# manually on system bus:
%config %{_sysconfdir}/dbus-1/system.d/cdemud-dbus.conf
%{_sysconfdir}/modprobe.preload.d/cdemud
/lib/udev/rules.d/50-cdemud.rules
%{_bindir}/cdemud
%{_bindir}/cdemu-daemon-session.sh
%{_bindir}/cdemu-daemon-system.sh
%{_libdir}/cdemud-dbus-service
%{_datadir}/dbus-1/system-services/net.sf.cdemu.CDEMUD_Daemon.service
%{_datadir}/dbus-1/services/net.sf.cdemu.CDEMUD_Daemon.service
%{_mandir}/man8/cdemud.8*
