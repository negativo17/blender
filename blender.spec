%global debug_package %{nil}
%global __strip /bin/true

%global blender_api 4.4
%global org org.blender.Blender

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%global macrosdir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)

# Bundled libraries:
%global __requires_exclude ^(libsycl\\.so.*|libcycles_kernel_oneapi_aot\\.so.*|libI.*\\.so.*|libOpen.*\\.so.*|libboost_.*\\.so.*|libembree.*\\.so.*|libopenvdb.*\\.so.*|libosd.*\\.so.*|libosl.*\\.so.*|libtbb\\.so.*|libvulkan\\.so.*|libusd.*\\.so.*)$
%global __provides_exclude ^(libsycl\\.so.*|libcycles_kernel_oneapi_aot\\.so.*|libI.*\\.so.*|libOpen.*\\.so.*|libboost_.*\\.so.*|libembree.*\\.so.*|libopenvdb.*\\.so.*|libosd.*\\.so.*|libosl.*\\.so.*|libtbb\\.so.*|libvulkan\\.so.*|libusd.*\\.so.*)$

Name:       blender
Epoch:      2
Version:    4.4.0
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
BuildRequires:  libappstream-glib
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

# Hardware acceleration. Intel (oneAPI, SYCL) is always included as embree is
# linked into the main executable and it also deals with CPUs.
# https://docs.blender.org/manual/en/latest/editors/preferences/system.html#cycles-render-device

%package cuda
Summary:       Nvidia CUDA support for Blender
Requires:      %{name} = %{epoch}:%{version}-%{release}
# Required to enable autocompilation of kernels
# Requires:    cuda-nvrtc-devel

%description cuda
This package contains CUDA support for Blender, to enable Cycles rendering on
supported Nvidia GPUs.

%package hip
Summary:       AMD HIP RT support for Blender
Requires:      %{name} = %{epoch}:%{version}-%{release}

%description hip
This package contains ROCm HIP support for Blender, to enable Cycles rendering
on supported AMD GPUs.

%prep
%autosetup -p1 -n %{name}-%{version}-linux-x64

# Fix all Python shebangs recursively in .
%if 0%{?fedora}
%{__python3} %{_rpmconfigdir}/redhat/pathfix.py -pni "%{__python3} %{py3_shbang_opts}" .
%else
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" .
%endif

# Fix all library permissions:
find . -type f -name "*lib*.so*" -exec chmod 755 {} \;

%if 0%{?rhel} == 8
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
install -p -m 644 -D %{SOURCE2} %{buildroot}%{_metainfodir}/%{org}.metainfo.xml
sed -i \
  -e '/type="faq"/d' \
  -e '/type="vcs-browser"/d' \
  -e '/type="translate"/d' \
  -e '/type="vcs-browser"/d' \
  -e '/type="contribute"/d' \
  %{buildroot}%{_metainfodir}/%{org}.metainfo.xml

# Localization
%find_lang %{name}

# rpmlint fixes
find %{buildroot} -name ".so" -exec chmod 755 {} \;
find %{buildroot} -name ".so.*" -exec chmod 755 {} \;

chrpath -d %{buildroot}%{_libdir}/%{name}/%{blender_api}/scripts/addons_core/io_scene_gltf2/libextern_draco.so

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{org}.metainfo.xml

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
%{_metainfodir}/%{org}.metainfo.xml

# Stuff that goes into the hw acceleration subpackages.
%exclude %{_libdir}/%{name}/%{blender_api}/scripts/addons_core/cycles/lib
%exclude %{_libdir}/%{name}/lib/libOpenImageDenoise_device_cuda.so.*
%exclude %{_libdir}/%{name}/lib/libOpenImageDenoise_device_hip.so.*

%files cuda
%{_libdir}/%{name}/%{blender_api}/scripts/addons_core/cycles/lib
%{_libdir}/%{name}/lib/libOpenImageDenoise_device_cuda.so.*

%files hip
%{_libdir}/%{name}/lib/libOpenImageDenoise_device_hip.so.*

%files rpm-macros
%{macrosdir}/macros.%{name}

%changelog
* Thu Apr 10 2025 Simone Caronni <negativo17@gmail.com> - 2:4.4.0-1
- Update to 4.4.0.

* Thu Mar 13 2025 Simone Caronni <negativo17@gmail.com> - 2:4.3.2-1
- Update to 4.3.2.
- Trim changelog.

* Wed Oct 23 2024 Simone Caronni <negativo17@gmail.com> - 2:4.2.3-1
- Update to 4.2.3.

* Thu Sep 26 2024 Simone Caronni <negativo17@gmail.com> - 2:4.2.2-1
- Update to 4.2.2.

* Tue Aug 06 2024 Simone Caronni <negativo17@gmail.com> - 2:4.2.0-1
- Update to 4.2.0.

* Thu Apr 25 2024 Simone Caronni <negativo17@gmail.com> - 2:4.1.1-1
- Update to 4.1.1.

* Wed Apr 17 2024 Simone Caronni <negativo17@gmail.com> - 2:4.1.0-2
- Split of AMD ROCm HIP subpackage.

* Fri Apr 12 2024 Simone Caronni <negativo17@gmail.com> - 2:4.1.0-1
- Update to 4.1.0.
- Make sure Provides/Requires are properly set by setting permissions on
  libraries before the package is assembled (#9).

* Sat Jan 06 2024 Simone Caronni <negativo17@gmail.com> - 2:4.0.2-1
- Update to 4.0.2.
