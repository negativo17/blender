%global debug_package %{nil}
%global __strip /bin/true

%global blender_api 4.0
%global org org.blender.Blender

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%global macrosdir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)

# Bundled libraries:
%global __requires_exclude ^(libsycl\\.so.*|libncursesw\\.so.*|libpanelw\\.so.*|libtinfo\\.so.*|libcycles_kernel_oneapi_aot\\.so.*|libI.*\\.so.*|libOpen.*\\.so.*|libboost_.*\\.so.*|libembree.*\\.so.*|libopenvdb.*\\.so.*|libosd.*\\.so.*|libtbb\\.so.*|libusd.*\\.so.*)$
%global __provides_exclude ^(libsycl\\.so.*|libncursesw\\.so.*|libpanelw\\.so.*|libtinfo\\.so.*|libcycles_kernel_oneapi_aot\\.so.*|libI.*\\.so.*|libOpen.*\\.so.*|libboost_.*\\.so.*|libembree.*\\.so.*|libopenvdb.*\\.so.*|libosd.*\\.so.*|libtbb\\.so.*|libusd.*\\.so.*)$

Name:       blender
Epoch:      2
Version:    %{blender_api}.2
Release:    1%{?dist}
Summary:    3D modeling, animation, rendering and post-production
License:    GPLv2
URL:        http://www.blender.org

ExclusiveArch:  x86_64

Source0:    http://download.%{name}.org/release/Blender%{blender_api}/%{name}-%{version}-linux-x64.tar.xz
Source1:    %{name}.thumbnailer
Source2:    https://raw.githubusercontent.com/blender/blender/v%{version}/release/freedesktop/org.blender.Blender.metainfo.xml
Source3:    %{name}.xml
Source4:    macros.%{name}

BuildRequires:  chrpath
BuildRequires:  desktop-file-utils
%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires:  libappstream-glib
%endif
BuildRequires:  python3-devel

Requires:       hicolor-icon-theme
Provides:       blender(ABI) = %{blender_api}

# Obsolete the standalone Blender player retired by upstream
Obsoletes:      blenderplayer < %{epoch}:%{version}-%{release}
Provides:       blenderplayer = %{epoch}:%{version}-%{release}
Obsoletes:      blender-rpm-macros < %{epoch}:%{version}-%{release}
Provides:       blender-rpm-macros = %{epoch}:%{version}-%{release}
Obsoletes:      blender-fonts < %{epoch}:%{version}-%{release}
Provides:       blender-fonts = %{epoch}:%{version}-%{release}

%description
Blender is the essential software solution you need for 3D, from modeling,
animation, rendering and post-production to interactive creation and playback.

Professionals and novices can easily and inexpensively publish stand-alone,
secure, multi-platform content to the web, CD-ROMs, and other media.

%package rpm-macros
Summary:        RPM macros to build third-party blender addons packages
BuildArch:      noarch

%description rpm-macros
This package provides rpm macros to support the creation of third-party addon
packages to extend Blender.

%package cuda
Summary:       CUDA support for Blender
Requires:      %{name} = %{epoch}:%{version}-%{release}
# It dynamically opens libcuda.so.1
Requires:      nvidia-driver-cuda-libs%{?_isa}
# Required to enable autocompilation of kernels
# Requires:    cuda-nvrtc-devel

%description cuda
This package contains CUDA support for Blender, to enable rendering on supported
Nvidia GPUs.

%prep
%autosetup -p1 -n %{name}-%{version}-linux-x64

# Fix all Python shebangs recursively in .
%if 0%{?fedora}
%{__python3} %{_rpmconfigdir}/redhat/pathfix.py -pni "%{__python3} %{py3_shbang_opts}" .
%else
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" .
%endif

%if 0%{?rhel} == 7 || 0%{?rhel} == 8
sed -i -e '/PrefersNonDefaultGPU/d' %{name}.desktop
%endif

%install
# Main program
mkdir -p %{buildroot}%{_libdir}/%{name}
cp -fra %{blender_api} %{name} lib \
    blender-symbolic.svg \
    %{buildroot}%{_libdir}/%{name}
rm -fr %{buildroot}%{_libdir}/%{name}/lib/mesa
mkdir -p %{buildroot}%{_bindir}
ln -sf ../%{_lib}/%{name}/%{name} %{buildroot}%{_bindir}/%{name}

# Desktop file
install -p -D -m 644 %{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
install -p -D -m 644 %{name}.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

# Thumbnailer
install -p -D -m 755 %{name}-thumbnailer %{buildroot}%{_bindir}/%{name}-thumbnailer
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_datadir}/thumbnailers/%{name}.thumbnailer

# Mime support
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_datadir}/mime/packages/%{name}.xml

# rpm macros
mkdir -p %{buildroot}%{macrosdir}
sed -e 's/@VERSION@/%{blender_api}/g' %{SOURCE4} > %{buildroot}%{macrosdir}/macros.%{name}

# AppData
%if 0%{?fedora} || 0%{?rhel} >= 8
install -p -m 644 -D %{SOURCE2} %{buildroot}%{_metainfodir}/%{org}.appdata.xml
%endif

# Localization
%find_lang %{name}

# rpmlint fixes
find %{buildroot} -name ".so" -exec chmod 755 {} \;
find %{buildroot} -name ".so.*" -exec chmod 755 {} \;

chrpath -d %{buildroot}%{_libdir}/%{name}/%{blender_api}/python/lib/python3.10/site-packages/libextern_draco.so

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
%if 0%{?fedora} || 0%{?rhel} >= 8
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{org}.appdata.xml
%endif

%files -f %{name}.lang
%license *.txt license
%doc readme.html
%{_bindir}/%{name}
%{_bindir}/%{name}-thumbnailer
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_datadir}/mime/packages/%{name}.xml
%{_datadir}/thumbnailers/%{name}.thumbnailer
%{_libdir}/%{name}/
# In the CUDA subpackage
%exclude %{_libdir}/%{name}/%{blender_api}/scripts/addons/cycles/lib/*.cubin
%exclude %{_libdir}/%{name}/%{blender_api}/scripts/addons/cycles/lib/*.ptx
%if 0%{?fedora} || 0%{?rhel} >= 8
%{_metainfodir}/%{org}.appdata.xml
%endif

%files cuda
%{_libdir}/%{name}/%{blender_api}/scripts/addons/cycles/lib/*.cubin
%{_libdir}/%{name}/%{blender_api}/scripts/addons/cycles/lib/*.ptx

%files rpm-macros
%{macrosdir}/macros.%{name}

%changelog
* Sat Jan 06 2024 Simone Caronni <negativo17@gmail.com> - 2:4.0.2-1
- Update to 4.0.2.

* Fri Oct 06 2023 Simone Caronni <negativo17@gmail.com> - 2:3.6.4-2
- Filter out provided libraries.

* Fri Oct 06 2023 Simone Caronni <negativo17@gmail.com> - 2:3.6.4-1
- Update to 3.6.4.

* Wed Sep 27 2023 Simone Caronni <negativo17@gmail.com> - 2:3.6.3-1
- Update to 3.6.3.

* Thu Aug 24 2023 Simone Caronni <negativo17@gmail.com> - 2:3.6.2-1
- Update to 3.6.2.

* Thu Jul 20 2023 Simone Caronni <negativo17@gmail.com> - 2:3.6.1-1
- Update to 3.6.1.

* Fri May 05 2023 Simone Caronni <negativo17@gmail.com> - 2:3.5.1-1
- Update to 3.5.1.

* Thu Apr 13 2023 Simone Caronni <negativo17@gmail.com> - 2:3.5.0-1
- Update to 3.5.0.

* Tue Jan 10 2023 Lars R. Damerow <lars@pixar.com> - 2:3.4.1-2
- Filter out automatic Provides/Requires for libcycles_kernel_oneapi_aot library.

* Wed Dec 21 2022 Simone Caronni <negativo17@gmail.com> - 2:3.4.1-1
- Update to 3.4.1.

* Thu Dec 15 2022 Simone Caronni <negativo17@gmail.com> - 2:3.4.0-2
- Fix libraries.

* Tue Dec 13 2022 Simone Caronni <negativo17@gmail.com> - 2:3.4.0-1
- Update to 3.4.0.

* Tue Nov 15 2022 Simone Caronni <negativo17@gmail.com> - 2:3.3.1-2
- Filter out Ncurses 5 libraries.

* Wed Oct 12 2022 Simone Caronni <negativo17@gmail.com> - 2:3.3.1-1
- Update to 3.3.1.

* Fri Sep 30 2022 Simone Caronni <negativo17@gmail.com> - 2:3.3.0-3
- Make private libraries visible.
- Trim changelog.

* Thu Sep 29 2022 Simone Caronni <negativo17@gmail.com> - 2:3.3.0-2
- Filter out SYCL library.

* Wed Sep 21 2022 Simone Caronni <negativo17@gmail.com> - 2:3.3.0-1
- Update to 3.3.0.

* Fri Jul 22 2022 Simone Caronni <negativo17@gmail.com> - 2:3.2.1-1
- Update to 3.2.1.

* Thu Jun 16 2022 Simone Caronni <negativo17@gmail.com> - 2:3.2.0-1
- Update to 3.2.0.

* Thu Apr 21 2022 Simone Caronni <negativo17@gmail.com> - 2:3.1.2-1
- Update to 3.1.2.

* Sun Jan 23 2022 Simone Caronni <negativo17@gmail.com> - 2:3.0.0-2
- Fix build on RHEL/CentOS 7.

* Sat Jan 22 2022 Simone Caronni <negativo17@gmail.com> - 2:3.0.0-1
- Update to 3.0.0.

* Thu Nov 18 2021 Simone Caronni <negativo17@gmail.com> - 2:2.93.6-1
- Update to 2.93.6.

* Mon Nov 08 2021 Simone Caronni <negativo17@gmail.com> - 2:2.93.5-1
- Update to 2.93.5.

* Wed Sep 22 2021 Simone Caronni <negativo17@gmail.com> - 2:2.93.4-2
- Do not attempt to strip binaries.

* Wed Sep 01 2021 Simone Caronni <negativo17@gmail.com> - 2:2.93.4-1
- Update to 2.93.4.

* Mon Aug 09 2021 Simone Caronni <negativo17@gmail.com> - 2:2.93.2-1
- Update to 2.93.2.

* Tue Jul 20 2021 Simone Caronni <negativo17@gmail.com> - 2:2.93.1-1
- Update to 2.93.1.

* Thu Jun 03 2021 Simone Caronni <negativo17@gmail.com> - 2:2.93.0-1
- Update to 2.93.0.
- Fix icon.

* Wed Mar 10 2021 Simone Caronni <negativo17@gmail.com> - 2:2.92.0-1
- Update to 2.92.0.

* Wed Jan 27 2021 Simone Caronni <negativo17@gmail.com> - 2:2.91.2-1
- Update to 2.91.2.

* Sat Nov 28 2020 Simone Caronni <negativo17@gmail.com> - 2:2.91.0-1
- Update to 2.91.0.

* Tue Oct 06 2020 Simone Caronni <negativo17@gmail.com> - 2:2.90.1-1
- Update to 2.90.1.

* Sat Sep 05 2020 Simone Caronni <negativo17@gmail.com> - 2:2.90.0-1
- Switch to release binaries as the depending libraries in Fedora are all at the
  wrong versions.
- Update to 2.90.0.
- Fix build on RHEL/CentOS.

* Tue Aug 25 2020 Simone Caronni <negativo17@gmail.com> - 2:2.83.5-5
- Merge changes from Fedora.
- Enable CUDA & OptiX.
