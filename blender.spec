%global blender_api 2.79b

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%global macrosdir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)

%ifarch %{ix86} x86_64
%global cyclesflag ON
%else
%global cyclesflag OFF
%endif

%ifarch x86_64

# Each CUDA ptxas invocation can consume more than 4 gb of memory, so limit the
# number of parallel make jobs to something suitable for your system when the
# CUDA build is enabled.
%global _with_cuda 1
%global cuda_version 9.2

%endif

# Enable this or rebuild the package with "--with=ffmpeg" to enable FFmpeg
# support.
%global _with_ffmpeg 1

# Enable this or rebuild the package with "--with=openvdb" to enable OpenVDB
# support.
# %%global _with_openvdb 1

Name:       blender
Epoch:      2
Version:    %{blender_api}
Release:    18%{?dist}

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
# Backported patch for openjpeg2 support from
# https://lists.blender.org/pipermail/bf-blender-cvs/2016-July/088691.html
# but without patch-updating the bundled openjpeg2 version
Patch7:     %{name}-2.79-openjpeg2.patch
Patch8:     util_sseb.patch
Patch9:     tree_hpp.patch
# Backported from https://developer.blender.org/rB1db47a2ccd1e68994bf8140eba6cc2a26a2bc91f
Patch10:     %{name}-2.79-python37.patch
# Patch mostly from upstream, for more details see:
# https://developer.blender.org/rB66d8bfb85c61aafe3bad2edf0e7b4d9d694ee2e7
# https://github.com/OpenImageIO/oiio/wiki/OIIO-2.0-Porting-Guide
Patch11:     blender-oiio2.patch
# Commit to make OpenGL_GL_PREFERENCES=GLVND work
# https://developer.blender.org/rB0658d047a94a86060f039790898a80a7adb0dcd9
Patch12:     blender-cmake_opengl.patch
# Patch to build with GCC9
Patch13:     0001-Fix-for-GCC9-new-OpenMP-data-sharing.patch

%{?_with_cuda:
%if 0%{?fedora} >= 30
BuildRequires:  cuda-gcc-c++
%endif
BuildRequires:  cuda-devel >= %{cuda_version}
}

# Development stuff
BuildRequires:  boost-devel
BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  expat-devel
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  git
BuildRequires:  jemalloc-devel
BuildRequires:  libtool
BuildRequires:  libspnav-devel
BuildRequires:  libxml2-devel
BuildRequires:  openssl-devel
BuildRequires:  pcre-devel
BuildRequires:  pugixml-devel
BuildRequires:  python3-devel >= 3.5
BuildRequires:  python3-numpy
BuildRequires:  python3-requests
BuildRequires:  subversion-devel

# Compression stuff
BuildRequires:  lzo-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
%if 0%{?fedora} >= 30
BuildRequires:  minizip-compat-devel
%else
BuildRequires:  minizip-devel
%endif

# 3D modeling stuff
BuildRequires:  fftw-devel
BuildRequires:  ftgl-devel
BuildRequires:  glew-devel
BuildRequires:  freeglut-devel
BuildRequires:  libGL-devel
BuildRequires:  libGLU-devel
BuildRequires:  libXi-devel
BuildRequires:  openCOLLADA-devel >= svn825
BuildRequires:  ode-devel
BuildRequires:  SDL2-devel
BuildRequires:  xorg-x11-proto-devel

# Picture/Video stuff
BuildRequires:  alembic-devel
%{?_with_ffmpeg:
BuildRequires:  compat-ffmpeg-devel
}
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libtheora-devel
BuildRequires:  libtiff-devel
BuildRequires:  OpenColorIO-devel
BuildRequires:  OpenEXR-devel
BuildRequires:  OpenImageIO-devel
BuildRequires:  openjpeg2-devel
%{?_with_openvdb:
BuildRequires:  openvdb-devel
}
BuildRequires:  tbb-devel

# Audio stuff
BuildRequires:  freealut-devel
BuildRequires:  jack-audio-connection-kit-devel
BuildRequires:  libao-devel
BuildRequires:  libogg-devel
BuildRequires:  libsamplerate-devel
BuildRequires:  libsndfile-devel
BuildRequires:  libvorbis-devel

# Typography stuff
BuildRequires:  fontpackages-devel
BuildRequires:  freetype-devel

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

# Delete the bundled FindOpenJPEG to make find_package use the system version
# instead (the local version hardcodes the openjpeg version so it is not update
# proof)
rm -f build_files/cmake/Modules/FindOpenJPEG.cmake

%{?_with_ffmpeg:
sed -i -e 's|/include/ffmpeg|/include/compat-ffmpeg|g' build_files/cmake/platform/platform_unix.cmake
}

%{?_with_cuda:
sed -i \
    -e 's|libcuda.so|libcuda.so.1|g' \
    -e 's|libnvrtc.so|libnvrtc.so.%{cuda_version}|g' \
    extern/cuew/src/cuew.c

sed -i -e \
%if 0%{?fedora} >= 30
    's|${CUDA_NVCC_FLAGS}|-I/usr/include/cuda -ccbin /usr/bin/cuda-g++|g' \
%else
    's|${CUDA_NVCC_FLAGS}|-I/usr/include/cuda|g' \
%endif
    intern/cycles/kernel/CMakeLists.txt

}

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
    -DOpenGL_GL_PREFERENCE=GLVND \
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
    %{?_with_openvdb:-DWITH_OPENVDB=ON -DWITH_OPENVDB_BLOSC=ON} \
    -DWITH_PLAYER=ON \
    -DWITH_PYTHON=ON \
    -DWITH_PYTHON_INSTALL=OFF \
    -DWITH_PYTHON_INSTALL_REQUESTS=OFF \
    -DWITH_PYTHON_SAFETY=ON \
    -DWITH_SDL=ON \
    -DWITH_SYSTEM_LZO=ON \
    -DWITH_SYSTEM_OPENJPEG=ON \
%if 0%{?_with_cuda}
    -DCUDA_NVCC_EXECUTABLE=%{_bindir}/nvcc \
    -DCYCLES_CUDA_BINARIES_ARCH="sm_30;sm_35;sm_37;sm_50;sm_52;sm_60;sm_61" \
    -DWITH_CYCLES_CUDA_BINARIES=ON
%endif

#make VERBOSE=1 # %%{?_smp_mflags}
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
%if 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &> /dev/null || :
/bin/touch --no-create %{_datadir}/mime/packages &> /dev/null || :
%endif

%postun
%if 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &> /dev/null || :
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &> /dev/null || :
    /usr/bin/update-mime-database %{?fedora:-n} %{_datadir}/mime &> /dev/null || :
fi
%endif

%posttrans
%if 0%{?rhel} == 7
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
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
%{_datadir}/%{name}/scripts/addons/cycles/lib/*.cubin
}

%changelog
* Fri Jun 14 2019 Simone Caronni <negativo17@gmail.com> - 2:2.79b-18
- Rebuild for alembic 1.7.11.

* Sun May 12 2019 Simone Caronni <negativo17@gmail.com> - 2:2.79b-17
- Rebase on Fedora SPEC file.
- Fix build for GCC9 new OpenMP data sharing
- Add patch for OpenImageIO 2.0 API changes.
- Trim changelog.

* Mon Nov 05 2018 Simone Caronni <negativo17@gmail.com> - 2:2.79b-9
- Update build requirements for Fedora 29.
- Apply workaround for "no text in GUI" bug (#1631922).

* Thu Aug 30 2018 Simone Caronni <negativo17@gmail.com> - 2:2.79b-8
- Rebuild for CUDA 9.2.

* Tue Jul 17 2018 Simone Caronni <negativo17@gmail.com> - 2:2.79b-7
- Rebase on Fedora SPEC file.

* Tue Jul 17 2018 Simone Caronni <negativo17@gmail.com> - 1:2.79b-6
- Allow rebuilding with OpenVDB support.
- Be consistent with spaces/tabs (rpmlint).

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:2.79b-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 1:2.79b-4
- Rebuilt for Python 3.7

* Tue Apr 24 2018 Richard Shaw <hobbes1069@gmail.com> - 1:2.79b-3
- Rebuild for openCOLLADA 1.6.62.

* Thu Mar 29 2018 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.79b-2
- Rebuild with applied upstream patches

* Thu Mar 22 2018 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.79b-1
- Update to 2.79b
- Reenable openvdb

* Wed Feb 28 2018 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.79a-1
- Update to 2.79a
- Add gcc-c++
- Temporarily disable openvdb due failure to build
- Upstream patch for compile fix with GCC 8.0

* Mon Feb 26 2018 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.79-8
- Rebuild for boost 1.66

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:2.79-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jan 17 2018 Sandro Mani <manisandro@gmail.com> - 1:2.79-6
- Switch to openjpeg2

* Sun Jan 07 2018 Richard Shaw <hobbes1069@gmail.com> - 1:2.79-5
- Rebuild for OpenImageIO 1.8.7.

* Sat Jan 06 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1:2.79-4
- Remove obsolete scriptlets
