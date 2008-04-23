
%define version 1.0.0
%define snapshot 292
%define rel	1

%if 0
# Update commands:
REV=$(svn info https://cdemu.svn.sourceforge.net/svnroot/cdemu/trunk/cdemu-daemon | sed -ne 's/^Last Changed Rev: //p')
svn export -r $REV https://cdemu.svn.sourceforge.net/svnroot/cdemu/trunk/cdemu-daemon cdemu-daemon-$REV
tar -cjf cdemu-daemon-$REV.tar.bz2 cdemu-daemon-$REV
%endif

Name:		cdemu-daemon
Version:	%version
Summary:	Userspace daemon part of the userspace-cdemu suite
%if %snapshot
Release:	%mkrel 1.svn%snapshot.%rel
Source:		%name-%snapshot.tar.bz2
%else
Release:	%mkrel %rel
Source:		http://downloads.sourceforge.net/cdemu/%name-%version.tar.bz2
%endif
Source1:	cdemud.init
Source2:	cdemud.sysconfig
Group:		Emulators
License:	GPLv2+
URL:		http://cdemu.sourceforge.net/
BuildRoot:	%{_tmppath}/%{name}-root
BuildRequires:	mirage-devel
BuildRequires:	glib2-devel
BuildRequires:	dbus-devel
BuildRequires:	daemon-devel
BuildRequires:	libalsa-devel
Obsoletes:	dkms-cdemu < 0.9
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

%prep
%if %snapshot
%setup -q -n %name-%snapshot
%else
%setup -q
%endif

%build
%if %snapshot
./autogen.sh
%endif
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
