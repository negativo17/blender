%global blender_api 2.79

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%global macrosdir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)

%ifarch %{ix86} x86_64
%global cyclesflag ON
%else
%global cyclesflag OFF
%endif

%global _with_ffmpeg 1

%ifarch x86_64

# Each CUDA ptxas invocation can consume more than 4 gb of memory, so limit the
# number of parallel make jobs to something suitable for your system when the
# CUDA build is enabled.
%global _with_cuda 1
%global min_cuda_version 8.0

%endif

Name:       blender
Epoch:      2
Version:    %{blender_api}
Release:    1%{?dist}

Summary:    3D modeling, animation, rendering and post-production
License:    GPLv2
URL:        http://www.blender.org

Source0:    http://download.%{name}.org/source/%{name}-%{version}.tar.gz
Source1:    %{name}player.1
Source2:    %{name}-fonts.metainfo.xml
Source5:    %{name}.xml
Source6:    %{name}.appdata.xml
Source10:   macros.%{name}

Patch0:     %{name}-2.79-droid.patch
Patch1:     %{name}-2.79-thumbnailer.patch
Patch2:     %{name}-2.79-scripts.patch
Patch3:     %{name}-2.79-locale.patch
Patch4:     %{name}-2.79-manpages.patch
Patch5:     %{name}-2.79-unversioned-system-path.patch
Patch6:     %{name}-2.79-openvdb3-abi.patch
Patch7:     %{name}-2.79-cuda.patch

%{?_with_cuda:
# CUDA 8 requires gcc < 6
BuildRequires:  compat-gcc-53-c++
BuildRequires:  cuda-devel >= %{min_cuda_version}
}

%{?_with_ffmpeg:
BuildRequires:  ffmpeg-devel
}

BuildRequires:  alembic-devel
BuildRequires:  boost-devel
BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  esound-devel
BuildRequires:  expat-devel
BuildRequires:  fftw-devel
BuildRequires:  fontpackages-devel
BuildRequires:  freealut-devel
BuildRequires:  freeglut-devel
BuildRequires:  freetype-devel
BuildRequires:  ftgl-devel
BuildRequires:  gettext
BuildRequires:  git
BuildRequires:  glew-devel
BuildRequires:  jack-audio-connection-kit-devel
BuildRequires:  jemalloc-devel
BuildRequires:  libao-devel
BuildRequires:  libGL-devel
BuildRequires:  libGLU-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libogg-devel
BuildRequires:  libpng-devel
BuildRequires:  libsamplerate-devel
BuildRequires:  libsndfile-devel
BuildRequires:  libspnav-devel
BuildRequires:  libtheora-devel
BuildRequires:  libtiff-devel
BuildRequires:  libtool
BuildRequires:  libvorbis-devel
BuildRequires:  libXi-devel
BuildRequires:  libxml2-devel
BuildRequires:  lzo-devel
BuildRequires:  ode-devel
BuildRequires:  openCOLLADA-devel >= svn825
BuildRequires:  OpenColorIO-devel
BuildRequires:  OpenEXR-devel
BuildRequires:  OpenImageIO-devel
BuildRequires:  openjpeg-devel
BuildRequires:  openssl-devel
BuildRequires:  openvdb-devel
BuildRequires:  pcre-devel
BuildRequires:  pkgconfig(python3)
BuildRequires:  pugixml-devel
BuildRequires:  python3-requests
BuildRequires:  qhull-devel
BuildRequires:  SDL2-devel
BuildRequires:  subversion-devel
BuildRequires:  tbb-devel
BuildRequires:  xorg-x11-proto-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel

# Appstream stuff
BuildRequires:  libappstream-glib

Requires:       google-droid-sans-fonts
Requires:       %{name}-fonts = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       fontpackages-filesystem
Requires:       python3-numpy
Requires:       python3-requests
Provides:       blender(ABI) = %{blender_api}

%description
Blender is the essential software solution you need for 3D, from modeling,
animation, rendering and post-production to interactive creation and playback.

Professionals and novices can easily and inexpensively publish stand-alone,
secure, multi-platform content to the web, CD-ROMs, and other media.

%package -n blenderplayer
Summary:        Standalone Blender player
Provides:       %{name}(ABI) = %{blender_api}

%description -n blenderplayer
This package contains a stand alone release of the Blender player. You will need
this package to play games which are based on the Blender Game Engine.

%package rpm-macros
Summary:        RPM macros to build third-party blender addons packages
BuildArch:      noarch

%description rpm-macros
This package provides rpm macros to support the creation of third-party addon
packages to extend Blender.

%package fonts
Summary:        International Blender mono space font
License:        ASL 2.0 and GPlv3 and Bitstream Vera and Public Domain
BuildArch:      noarch
Obsoletes:      fonts-%{name} < 1:2.78-3
Provides:       fonts-%{name} = %{?epoch:%{epoch}:}%{version}-%{release}

%description fonts
This package contains an international Blender mono space font which is a
composition of several mono space fonts to cover several character sets.

%{?_with_cuda:
%package cuda
Summary:       CUDA support for Blender
Requires:      %{name} = %{?epoch:%{epoch}:}%{version}-%{release}
# It dynamically opens libcuda.so.1 and libnvrtc.so.8.0
Requires:      nvidia-driver-cuda-libs%{?_isa}
Requires:      cuda-nvrtc

%description cuda
This package contains CUDA support for Blender, to enable rendering on supported
Nvidia GPUs.
}

%prep
%autosetup -p1

mkdir cmake-make

%build
pushd cmake-make

%ifarch ppc64le
# Disable altivec for now, bug 1393157
# https://lists.blender.org/pipermail/bf-committers/2016-November/047844.html
export CXXFLAGS="$CXXFLAGS -mno-altivec"
%endif

%cmake .. \
%ifnarch %{ix86} x86_64
    -DWITH_RAYOPTIMIZATION=OFF \
%endif
    -DBOOST_ROOT=%{_prefix} \
    -DBUILD_SHARED_LIBS=OFF \
    -DCMAKE_SKIP_RPATH=ON \
    -DPYTHON_VERSION=$(%{__python3} -c "import sys ; print(sys.version[:3])") \
    -DWITH_ALEMBIC=ON \
    -DWITH_BUILDINFO=ON \
    %{?_with_ffmpeg:-DWITH_CODEC_FFMPEG=ON} \
    -DWITH_CODEC_SNDFILE=ON \
    -DWITH_CXX_GUARDEDALLOC=OFF \
    -DWITH_CYCLES=%{cyclesflag} \
    -DWITH_DOC_MANPAGE=ON \
    -DWITH_FFTW3=ON \
    -DWITH_GAMEENGINE=ON \
    -DWITH_IMAGE_OPENJPEG=ON \
    -DWITH_INPUT_NDOF=ON \
    -DWITH_INSTALL_PORTABLE=OFF \
    -DWITH_JACK=ON \
    -DWITH_MEM_JEMALLOC=ON \
    -DWITH_MOD_OCEANSIM=ON \
    -DWITH_OPENCOLLADA=ON \
    -DWITH_OPENCOLORIO=ON \
    -DWITH_OPENVDB=ON \
    -DWITH_OPENVDB_BLOSC=ON \
    -DWITH_PLAYER=ON \
    -DWITH_PYTHON=ON \
    -DWITH_PYTHON_INSTALL=OFF \
    -DWITH_PYTHON_INSTALL_REQUESTS=OFF \
    -DWITH_PYTHON_SAFETY=ON \
    -DWITH_SDL=ON \
    -DWITH_SYSTEM_LZO=ON \
    -DWITH_SYSTEM_OPENJPEG=ON \
    %{?_with_cuda:-DCUDA_NVCC_EXECUTABLE=%{_bindir}/nvcc} \
    %{?_with_cuda:-DWITH_CYCLES_CUDA_BINARIES=ON}

%make_build
popd

%install
pushd cmake-make
%make_install
popd

find %{buildroot}%{_datadir}/%{name}/scripts -type f -exec sed -i -e 's/\r$//g' {} \;

# Mime support
install -p -D -m 644 %{SOURCE5} %{buildroot}%{_datadir}/mime/packages/%{name}.xml

# Desktop icon
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

# Deal with docs in the files section
rm -rf %{buildroot}%{_docdir}/%{name}/*

# rpm macros
mkdir -p %{buildroot}%{macrosdir}
sed -e 's/@VERSION@/%{blender_api}/g' %{SOURCE10} > %{buildroot}%{macrosdir}/macros.%{name}

# AppData
install -p -m 644 -D %{SOURCE6} %{buildroot}%{_datadir}/appdata/%{name}.appdata.xml
install -p -m 644 -D %{SOURCE2} %{buildroot}%{_datadir}/metainfo/%{name}-fonts.metainfo.xml

# Localization
%find_lang %{name}
rm -fr %{buildroot}%{_datadir}/locale/languages

%check
appstream-util validate-relax --nonet %{buildroot}/%{_datadir}/appdata/%{name}.appdata.xml
appstream-util validate-relax --nonet %{buildroot}/%{_datadir}/metainfo/%{name}-fonts.metainfo.xml

%post
%if 0%{?fedora} == 24 || 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
%endif
/bin/touch --no-create %{_datadir}/icons/hicolor &> /dev/null || :
%if 0%{?rhel} == 7
/bin/touch --no-create %{_datadir}/mime/packages &> /dev/null || :
%endif

%postun
%if 0%{?fedora} == 24 || 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
%endif
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &> /dev/null || :
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &> /dev/null || :
%if 0%{?rhel} == 7
    /usr/bin/update-mime-database %{?fedora:-n} %{_datadir}/mime &> /dev/null || :
%endif
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
%if 0%{?rhel} == 7
/usr/bin/update-mime-database %{?fedora:-n} %{_datadir}/mime &> /dev/null || :
%endif

%files -f %{name}.lang
%license COPYING
%license doc/license/*-license.txt
%license release/text/copyright.txt
%doc release/text/readme.html
%{_bindir}/%{name}
%{_datadir}/appdata/%{name}.appdata.xml
%{_datadir}/applications/%{name}.desktop
%{_datadir}/%{name}/
%exclude %{_datadir}/%{name}/scripts/addons/cycles/kernel/kernels/cuda
%exclude %{_datadir}/%{name}/scripts/addons/cycles/lib/*.cubin
%{_datadir}/icons/hicolor/*/apps/%{name}.*
%{_datadir}/mime/packages/%{name}.xml
%{_mandir}/man1/%{name}.*

%files -n %{name}player
%license COPYING
%license doc/license/*-license.txt
%license release/text/copyright.txt
%{_bindir}/%{name}player
%{_mandir}/man1/%{name}player.*

%files rpm-macros
%{macrosdir}/macros.%{name}

%files fonts
%license release/datafiles/LICENSE-*.ttf.txt
%{_datadir}/metainfo/%{name}-fonts.metainfo.xml
%{_fontbasedir}/%{name}/

%{?_with_cuda:
%files cuda
%{_datadir}/%{name}/scripts/addons/cycles/kernel/kernels/cuda
%{_datadir}/%{name}/scripts/addons/cycles/lib/*.cubin
}

%changelog
* Thu Sep 21 2017 Simone Caronni <negativo17@gmail.com> - 2:2.79-1
- Update to 2.79.

* Fri Apr 28 2017 Simone Caronni <negativo17@gmail.com> - 2:2.78c-6
- Use GCC 5.3 compatibility package instead of Clang for CUDA components (fix
  build on Fedora 26+).

* Tue Apr 25 2017 Simone Caronni <negativo17@gmail.com> - 2:2.78c-5
- Enable Alembic support.

* Mon Apr 24 2017 Simone Caronni <negativo17@gmail.com> - 2:2.78c-4
- Unconditionally build OpenVDB support

* Fri Apr 21 2017 Simone Caronni <negativo17@gmail.com> - 2:2.78c-3
- Remove redundant fonts directory in blender-fonts package.
- Require Clang < 3.9 for building CUDA 8 support.

* Fri Apr 07 2017 Simone Caronni <negativo17@gmail.com> - 2:2.78c-2
- Merge in latest changes from Fedora.

* Mon Feb 27 2017 Simone Caronni <negativo17@gmail.com> - 2:2.78c-1
- Update to 2.78c.

* Sun Feb 12 2017 Simone Caronni <negativo17@gmail.com> - 2:2.78b-1
- Update to 2.78b.

* Wed Feb 01 2017 Simone Caronni <negativo17@gmail.com> - 2:2.78a-11
- Merge in SPEC file from Fedora.
- Update scriptlets as per packaging guidelines.
- Update patches.

* Sun Jan 29 2017 Simone Caronni <negativo17@gmail.com> - 2:2.78a-3
- Improve font installation.
- Update requirement.
- Add fonts AppData.
- Update GCC flags.

* Thu Dec 01 2016 Simone Caronni <negativo17@gmail.com> - 1:2.78a-2
- Use Clang for CUDA kernels.
- Bump Epoch.

* Thu Nov 03 2016 Simone Caronni <negativo17@gmail.com> - 1:2.78a-1
- Update to 2.78a.
- Rename fonts-blender to blender-fonts as in the Fedora package.
- Enable OpenVDB support.
- Enable CUDA NVRTC support.

* Fri Oct 14 2016 Simone Caronni <negativo17@gmail.com> - 1:2.78-1
- Update to 2.78.

* Fri Jul 22 2016 Simone Caronni <negativo17@gmail.com> - 1:2.77a-2
- Rebuild for ffmpeg 3.1.1.

* Sun Jun 12 2016 Simone Caronni <negativo17@gmail.com> - 1:2.77a-1
- Update to 2.77a, requires Python 3.5.
- Rebase all patches.

* Fri Dec 11 2015 Simone Caronni <negativo17@gmail.com> - 1:2.76-3
- Add Debian patches, enable localization support.
- Remove obsoletes/provides for blender-fonts (Fedora 10!).

* Fri Dec 11 2015 Simone Caronni <negativo17@gmail.com> - 1:2.76-2
- Clean up and rework spec file (license, obsolete tags, redundant commands,
  consistency in variable names, sorting, etc.).
- Adjust CMake options.
- Make CUDA build optional on x86_64.
- Make FFMPeg build optional.
- Make CUDA a subpackage that depends on the correct CUDA libraries.
- Move appdata content from spec file to a separate file.
- Enable OpenColorIO, FontConfig and RedCode support (bundled GPLv2 library that
  only exist inside the Blender source).

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.76-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Mon Oct 12 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1:2.76-1
- Update to 2.76
- Clean up specfile
- Enable SDL2

* Tue Sep 01 2015 Jonathan Wakely <jwakely@redhat.com> - 1:2.75-6
- Rebuilt for jemalloc-4.0.0

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 1:2.75-5
- Rebuilt for Boost 1.59

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.75-4
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Thu Jul 23 2015 Peter Robinson <pbrobinson@fedoraproject.org> 1:2.75-3
- Drop esound dep

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 1:2.75-2
- rebuild for Boost 1.58

* Tue Jul  7 2015 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.75-1
- New upstream release

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.74-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 16 2015 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.74-5
- Add dependency to numpy (#1222122I

* Tue May  5 2015 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.74-4
- Fix regression for 3D mice support

* Mon May  4 2015 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.74-3
- Enable 3D mice support

* Sun May 03 2015 Kalev Lember <kalevlember@gmail.com> - 1:2.74-2
- Rebuilt for GCC 5 C++11 ABI change

* Wed Apr  1 2015 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.74-1
- New upstream release

* Thu Mar 26 2015 Richard Hughes <rhughes@redhat.com> - 1:2.73a-5
- Add an AppData file for the software center

* Wed Feb 04 2015 Petr Machata <pmachata@redhat.com> - 1:2.73a-4
- Bump for rebuild.

* Wed Jan 28 2015 Richard Shaw <hobbes1069@gmail.com> - 1:2.73a-3
- Rebuild for OpenImageIO 1.5.10.

* Wed Jan 28 2015 Petr Machata <pmachata@redhat.com> - 1:2.73a-2
- Rebuild for boost 1.57.0

* Wed Jan 21 2015 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.73a-1
- New minor bug-fixing release from upstream

* Thu Jan  8 2015 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.73-1
- New upstream release

* Wed Nov 26 2014 Rex Dieter <rdieter@fedoraproject.org> - 1:2.72b-4
- rebuild (openexr)

* Thu Nov  6 2014 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.72b-3
- Fix odd dependy issue

* Sun Nov  2 2014 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.72b-2
- Fix dependency issue (#1157600)

* Thu Oct 23 2014 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.72b-1
- New upstream release

* Sat Oct 11 2014 Dan Horák <dan[at]danny.cz> - 1:2.72-3
- fix size_t inconsistency (upstream issue T42183)

* Thu Oct  9 2014 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.72-2
- Remove OpenCOLLADA patch

* Tue Sep 30 2014 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.72-1
- New upstream release
- Add patch to fix FTBFS with current OpenCOLLADA release

* Sat Sep 06 2014 François Cami <fcami@fedoraproject.org> - 1:2.71-4
- Rebuilt for openCOLLADA 0-19.git69b844d

* Sat Aug 16 2014 Rex Dieter <rdieter@fedoraproject.org> 1:2.71-3
- fix/update icon/mime scriptlets

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.71-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 29 2014 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.71-1
- New upstream release
- Use blender.1.py to build man page
- Disable parallel build

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.70a-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 28 2014 Kalev Lember <kalevlember@gmail.com> - 1:2.70a-5
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 1:2.70a-4
- Rebuild for boost 1.55.0

* Fri May 23 2014 David Tardon <dtardon@redhat.com> - 1:2.70a-3
- rebuild for boost 1.55.0

* Wed May 21 2014 Richard Shaw <hobbes1069@gmail.com> - 1:2.70a-2
- Rebuild for updated OpenImageIO 1.4.7.

* Wed Apr 16 2014 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.70a-1
- Minor upstream update

* Mon Mar 24 2014 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.70-2
- Disable CYCLES for non-Intel processors

* Thu Mar 20 2014 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.70-1
- New upstream releasw
- Exclude armv7hl

* Sun Mar  9 2014 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.69-7
- Use new rpm macro for rpm macro direcgory  (#1074263)

* Mon Jan 13 2014 Richard Shaw <hobbes1069@gmail.com> - 1:2.69-6
- Rebuild for updated OpenImageIO 1.3.11.

* Tue Dec 31 2013 François Cami <fcami@fedoraproject.org> - 1:2.69-5
- Enable parallel building.

* Tue Dec 31 2013 François Cami <fcami@fedoraproject.org> - 1:2.69-4
- Add Ocean Simulation (#1047589).
- Fix mixed use of tabs and spaces in blender.spec (rpmlint).

* Wed Nov 27 2013 Rex Dieter <rdieter@fedoraproject.org> - 1:2.69-3
- rebuild (openexr)

* Mon Nov 18 2013 Dave Airlie <airlied@redhat.com> - 1:2.69-2
- rebuilt for GLEW 1.10

* Thu Oct 31 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.69-1
- New upsream release

* Mon Sep  9 2013 François Cami <fcami@fedoraproject.org> - 1:2.68a-6
- Rebuild.

* Wed Sep  4 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.68a-5
- Include derived DoridSans font for CJK support (#867205)

* Sun Sep  1 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.68a-4
- Aboid twice occurance of locale files
- Fix typo in DroideSans font name

* Wed Aug 28 2013 François Cami <fcami@fedoraproject.org> - 1:2.68a-3
- Enable jemalloc and OpenColorIO. (#1002197)
- Re-enable localization (#867285)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.68a-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 30 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.68a-1
- New minor upstream bugfix release

* Mon Jul 29 2013 Petr Machata <pmachata@redhat.com> - 1:2.68-4
- Rebuild for boost 1.54.0

* Tue Jul 23 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.68-3
- Rebuilt again

* Mon Jul 22 2013 Richard Shaw <hobbes1069@gmail.com> - 1:2.68-2
- Rebuild for updated OpenImageIO.

* Fri Jul 19 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.68-1
- New upstream release

* Sun Jul  7 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.67b-3
- Suppress output of update-mime-database (#541041)

* Fri Jun  7 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.67b-1
- Minor upstream bugfix update

* Mon Jun  3 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.67a-3
- Fix crash in blender/makerna/intern/rna_access.c (ä969043)

* Sun May 26 2013 Dan Horák <dan[at]danny.cz> - 1:2.67a-2
- fix build on non-x86 arches

* Fri May 24 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.67a-1
- New minor upstream release

* Fri May 17 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.67-2
- Fix dependency issues with fonts subpackage
- Make fonts subpackage noarch

* Wed May  8 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.67-1
- New upstream release
- Add subpackage for international mono space font

* Sun Mar 10 2013 Rex Dieter <rdieter@fedoraproject.org> - 1:2.66a-2
- rebuild (OpenEXR)

* Wed Mar  6 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.66a-1
- New upstream release

* Sat Feb 23 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.66-2
- Fix wrong font name for international feature (#867205)

* Thu Feb 21 2013 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.66-1
- New upstream release
- Remove unnecessaries patches
- Add Patch to remove '//' in includes

* Sun Feb 10 2013 Denis Arnaud <denis.arnaud_fedora@m4x.org> - 1:2.65a-5
- Rebuild for Boost-1.53.0

* Sat Feb 09 2013 Denis Arnaud <denis.arnaud_fedora@m4x.org> - 1:2.65a-4
- Rebuild for Boost-1.53.0

* Fri Jan 18 2013 Adam Tkac <atkac redhat com> - 1:2.65a-3
- rebuild due to "jpeg8-ABI" feature drop

* Tue Jan 15 2013 Richard Shaw <hobbes1069@gmail.com> - 1:2.65a-2
- Rebuild for updated OpenImageIO library.

* Thu Dec 20 2012 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.65a-1
- New upstream release

* Sat Dec 15 2012 Jochen Schmitt <JOchen herr-schmitt de> - 1:2.65-4
- Fix SEGFAULT in blf_lang.c (#887413)

* Fri Dec 14 2012 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.65-3
- Remove Req. to the DejaVu Sans font

* Thu Dec 13 2012 Adam Jackson <ajax@redhat.com> - 1:2.65-2
- Rebuild for glew 1.9.0

* Tue Dec 11 2012 Jochen Schmitt <Jochen herr schmitt de> - 1:2.65-1
- New upstream release

* Mon Oct 29 2012 Dan Horák <dan[at]danny.cz> - 1:2.64a-3
- fix build on big endian arches

* Thu Oct 18 2012 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.64a-2
- Loading droid-sans font from /usr/share/fonts (#867205)

* Tue Oct  9 2012 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.64a-1
- New minor upstream update release

* Fri Oct  5 2012 Dan Horák <dan[at]danny.cz> - 1:2.64-2
- fix build on non-x86 64-bit arches

* Wed Oct  3 2012 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.64-1
- New upstream release

* Fri Sep  7 2012 Jochen Schmitt <JOchen herr-schmitt de> - 1:2.63a-10
- Add forgotten O_EXCL to CVE-patch

* Thu Sep  6 2012 Jochen Schmitt <JOchen herr-schmitt de> - 1:2.63a-8
- Porting blender-2.49b-cve.patch (#855092, CVE-2008-1103)

* Fri Aug 10 2012 Richard Shaw <hobbes1069@gmail.com> - 1:2.63a-7
- Rebuild for libboost 1.50.

* Sat Aug 04 2012 David Malcolm <dmalcolm@redhat.com> - 1:2.63a-6
- rebuild for https://fedoraproject.org/wiki/Features/Python_3.3

* Wed Aug 01 2012 Adam Jackson <ajax@redhat.com> - 1:2.63a-5
- -Rebuild for new glew

* Sun Jul 29 2012 Jochen Schmitt <Jochen herr-schmitt de> - 1:2.63a-4
- Rebult to fix broken dependencies

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.63a-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jun 26 2012 Richard Shaw <hobbes1069@gmail.com> 1:2.63a-2
- Bump revision to be >= f17 for AutoQA.

* Fri May 11 2012 Jochen Schmitt <Jochen herr-schmitt de> 1:2.63a-1
- New upstream release

* Fri Apr 27 2012 Jochen Schmitt <JOchen herr-schmitt de> 1:2.63-1
- New upstream release

* Wed Apr 25 2012 Jochen Schmitt <Jochen herr-schmitt de> 1:2.62-6
- Fix crash in libspnav (#814665)

* Tue Apr 24 2012 Jochen Schmitt <Jochen herr-schmitt de> 1:2.62-5
- Add cycles support (#812354)

* Fri Apr 13 2012 Jochen Schmitt <Jochen herr-schmitt de> 1:2.62-4
- Add BR to libspnav-devel

* Sun Mar 18 2012 Jochen Schmitt <Jochen herr-schmitt de> 1:2.62-3
- Rebuild for new OpenImageIO release

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 1:2.62-2
- Rebuilt for c++ ABI breakage

* Thu Feb 16 2012 Jochen Schmitt <Jochen herr-schmitt de> 1:2.62-1
- New upstream release

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> 1:2.61-6
- Rebuild against PCRE 8.30

* Thu Feb 09 2012 Rex Dieter <rdieter@fedoraproject.org> 1:2.61-5
- rebuild (openjpeg)

* Thu Feb  9 2012 Jochen Schmitt <Jochen herr-schmitt de> 1:2.61-4
- Remove unnecessary gcc-4.5 patch

* Wed Feb  8 2012 Jochen Schmitt <Jochen herr-schmitt de> 1:2.61-3
- Fix gcc-4.7 related issue

* Thu Jan  5 2012 Jochen Schmitt <JOchen herr-schmitt de> 1:2.61-2
- Fix typo in syspth patch (#771814)
