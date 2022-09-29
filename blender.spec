%global debug_package %{nil}
%global __strip /bin/true

%global blender_api 3.3
%global org org.blender.Blender

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%global macrosdir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)

%global __requires_exclude ^(libsycl\\.so.*)$
%global __provides_exclude ^(libsycl\\.so.*)$

Name:       blender
Epoch:      2
Version:    3.3.0
Release:    2%{?dist}
Summary:    3D modeling, animation, rendering and post-production
License:    GPLv2
URL:        http://www.blender.org

ExclusiveArch:  x86_64

Source0:    http://download.%{name}.org/release/Blender%{blender_api}/%{name}-%{version}-linux-x64.tar.xz
Source1:    %{name}.thumbnailer
# URL can be derived by selecting the proper tag at:
# https://developer.blender.org/diffusion/B/history/master/release/freedesktop/org.blender.Blender.appdata.xml;v%{version}
Source2:    https://dev-files.blender.org/file/download/f6exmlw5dktdwuyuoe5x/PHID-FILE-2fxtmx5lq7pf2pvnvvv2/org.blender.Blender.appdata.xml
Source3:    %{name}.xml
Source4:    macros.%{name}

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
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" .

%if 0%{?rhel} == 7 || 0%{?rhel} == 8
sed -i -e '/PrefersNonDefaultGPU/d' %{name}.desktop
%endif

%install
# Main program
mkdir -p %{buildroot}%{_libdir}/%{name}
cp -fra %{blender_api} %{name} blender-symbolic.svg %{buildroot}%{_libdir}/%{name}
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
#find %{buildroot}%{_libdir}/%{name}/%{blender_api}/scripts -name "*.py" -exec chmod 755 {} \;
#find %%{buildroot}%%{_datadir}/%%{name}/scripts -type f -exec sed -i -e 's/\r$//g' {} \;

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
%if 0%{?fedora} || 0%{?rhel} >= 8
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{org}.appdata.xml
%endif

%files -f %{name}.lang
%license *.txt
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

* Tue Aug 25 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.5-4
- Temporarily exclude s390x second architecutre

* Tue Aug 25 2020 Charalampos Stratakis <cstratak@redhat.com> - 1:2.83.5-3
- Use c++14 for properly building with the latest version of openvdb

* Mon Aug 24 2020 Simone Caronni <negativo17@gmail.com> - 1:2.83.5-2
- Be consistent with build options format and distribution conditionals.
- rpmlint fixes.
- Fix build dependencies.
- Fix Python 3.9 patch.
- Disable OpenShadingLanguage, 1.11 is not supported.
- Disable Embree, 3.11 is not supported.

* Wed Aug 19 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.5-1
- Update to 2.83.5 (#1855165)

* Wed Aug 05 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.4-1
- Update to 2.83.4 (#1855165)

* Sat Aug 01 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.3-4
- Use cmake macros for build and install

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1:2.83.3-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1:2.83.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 22 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.3-1
- Update to 2.83.3 (#1855165)
- Enable embree and osl for cycles rendering

* Thu Jul 09 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.2-2
- Add openshadinglanguage dependency
- Reenable upstream patch to build on Python 3.9 for Fedora 33+ (#1843100)

* Thu Jul 09 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.2-1
- Update to 2.83.2 (#1855165)

* Thu Jun 25 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.1-1
- Update to 2.83.1 (#1843623)

* Sun Jun 21 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.0-4
- Apply upstream patch to build on Python 3.9 (#1843100)

* Sun Jun 21 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.0-3
- Fix installtion path for fonts directory (#1849429)
- More conversion to pkgconf format

* Sat Jun 20 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.0-2
- Remove undocumented and undefined function on Python 3.9
- Use documented python function defined on Python 3.9 (#1843100)

* Sun Jun 14 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.0-1.1
- Temporarily exclude ARM architecture (#1843100)

* Wed Jun 03 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.83.0-1
- Update to 2.83.0 (#1843623)
- Clean up spec file

* Tue May 12 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.82a-5
- Rebuild for embree 3.10.0

* Mon May 11 2020 Gwyn Ciesla <gwync@protonmail.com> - 1:2.82a-4
- Rebuild for new LibRaw

* Sat Apr 11 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.82a-3
- Rebuild for oidn 1.2.0

* Sat Apr 04 2020 Simone Caronni <negativo17@gmail.com> - 1:2.82a-2
- Remove unfinished RHEL 7 support in SPEC file.
- Move desktop file validation to check section.
- Fix FFmpeg conditional.
- Explicitly declare version in patch, hopefully it does not require an udpate.
- Trim changelog.

* Sat Mar 14 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.82a-1
- Update to 2.82a (#1810743)

* Thu Mar 05 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.82-3
- Add Obsolete blenderplayer line for system upgrade (#1810743)

* Sun Feb 23 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.82-2
- Patch for upstream invalid appdata causing segmentation fault

* Thu Feb 13 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.82-1
- Update to 2.82 (#1802530)
- Drop custom cmake parameters set by default on upstream
- Disable default upstream ffmpeg support due to patents issue
- Temporarily disable appstream validation

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1:2.81a-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Jan 27 2020 Richard Shaw <hobbes1069@gmail.com> - 1:2.81a-5
- Rebuild for OpenImageIO 2.1.10.1.

* Fri Jan 24 2020 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.81a-4
- Use pkgconfig for many build requirements as possible
- Replace pkgconfig(freeglut) by pkgconfig(glut) for Fedora 32 and above
- Enable OpenImageDenoise support (rhbz #1794521)
