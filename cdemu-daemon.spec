Summary:	Userspace daemon part of the CDemu suite
Name:		cdemu-daemon
Version:	2.1.1
Release:	3
Group:		Emulators
License:	GPLv2+
Url:		http://cdemu.sourceforge.net/
Source0:	http://downloads.sourceforge.net/cdemu/%{name}-%{version}.tar.bz2
Source1:	50-cdemud.rules
# (Anssi 12/2011) change default configuration to
# - no logging into $HOME to reduce homedir pollution
Patch0:		0001-daemon-set-Mageia-default-configuration.patch
BuildRequires:	cmake
BuildRequires:	sysfsutils-devel
BuildRequires:	pkgconfig(libmirage) >= %{version}
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(dbus-glib-1)
BuildRequires:	pkgconfig(ao)
Requires:	kmod(vhba)

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

%files
%doc README AUTHORS
%{_sysconfdir}/modprobe.preload.d/cdemud.conf
/lib/udev/rules.d/50-cdemud.rules
%{_bindir}/cdemu-daemon
%{_libexecdir}/cdemu-daemon-session.sh
%{_datadir}/dbus-1/services/net.sf.cdemu.CDEmuDaemon.service
%{_mandir}/man8/cdemu-daemon.8*

%post
# apply the new udev rule if module already present
/sbin/modprobe --first-time vhba 2>/dev/null || /sbin/udevadm trigger --sysname-match=vhba_ctl

#----------------------------------------------------------------------------

%prep
%setup -q
%apply_patches

%build
%cmake
%make

%install
%makeinstall_std -C build

install -d -m755 %{buildroot}%{_libexecdir}
install -d -m755 %{buildroot}%{_sysconfdir}/modprobe.preload.d
install -d -m755 %{buildroot}/lib/udev/rules.d

echo "vhba" > %{buildroot}%{_sysconfdir}/modprobe.preload.d/cdemud.conf

install %{SOURCE1} %{buildroot}/lib/udev/rules.d/50-cdemud.rules

%if "%{_prefix}/libexec" != "%{_libexecdir}"
mv %{buildroot}%{_prefix}/libexec/cdemu-daemon-session.sh %{buildroot}%{_libexecdir}/cdemu-daemon-session.sh
sed -i s,"%{_prefix}/libexec/","%{_libexecdir}/",g %{buildroot}%{_datadir}/dbus-1/services/net.sf.cdemu.CDEmuDaemon.service
%endif
