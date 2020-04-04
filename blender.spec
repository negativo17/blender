%global blender_api 2.82

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
%global cuda_version 10.2

%endif

# Comment this to enable FFmpeg support.
#global _without_ffmpeg 1

Name:       blender
Epoch:      2
Version:    %{blender_api}a
Release:    3%{?dist}

Summary:    3D modeling, animation, rendering and post-production
License:    GPLv2
URL:        http://www.blender.org

Source0:    http://download.%{name}.org/source/%{name}-%{version}.tar.xz
Source1:    %{name}.thumbnailer
Source2:    %{name}-fonts.metainfo.xml
Source5:    %{name}.xml
Source10:   macros.%{name}

Patch0:     %{name}-2.81a-droid.patch
# Invalid upstream appdata causes segmentation fault
# https://github.com/hughsie/appstream-glib/issues/337
# https://developer.blender.org/D7149
Patch1:     %{name}-2.82a-fix_appdata_validation.patch

%{?_with_cuda:
%if 0%{?fedora} >= 30
BuildRequires:  cuda-gcc-c++
%endif
BuildRequires:  cuda-devel >= %{cuda_version}
}

# Development stuff
BuildRequires:  boost-devel
BuildRequires:  cmake3
BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  git
BuildRequires:  libtool
BuildRequires:  libspnav-devel
#BuildRequires:  meson
BuildRequires:  pkgconfig(blosc)
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(jemalloc)
BuildRequires:  pkgconfig(libpcre)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(python3) >= 3.5
BuildRequires:  pkgconfig(xxf86vm)
BuildRequires:  pugixml-devel
BuildRequires:  python3-numpy
BuildRequires:  python3-requests
BuildRequires:  subversion-devel

# Compression stuff
BuildRequires:  lzo-devel
BuildRequires:  pkgconfig(liblzma)
BuildRequires:  pkgconfig(zlib)

# 3D modeling stuff
%ifarch x86_64
BuildRequires:  embree-devel
BuildRequires:  oidn-devel
%endif
BuildRequires:  openCOLLADA-devel >= svn825
BuildRequires:  pkgconfig(fftw3)
BuildRequires:  pkgconfig(ftgl)
BuildRequires:  pkgconfig(glew)

%if 0%{?fedora} > 31
BuildRequires:  pkgconfig(glut)
%else
BuildRequires:  pkgconfig(freeglut)
%endif
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(glu)
BuildRequires:  pkgconfig(xi)
BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(ode)
BuildRequires:  opensubdiv-devel
BuildRequires:  pkgconfig(sdl2)
BuildRequires:  pkgconfig(xproto)

# Picture/Video stuff
BuildRequires:  alembic-devel
%{!?_without_ffmpeg:
BuildRequires:  ffmpeg-devel
}
BuildRequires:  openvdb-devel
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(theora)
BuildRequires:  pkgconfig(libtiff-4)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(OpenColorIO)
BuildRequires:  pkgconfig(OpenEXR)
BuildRequires:  pkgconfig(OpenImageIO)
BuildRequires:  pkgconfig(libopenjp2)
BuildRequires:  pkgconfig(tbb)

# Audio stuff
BuildRequires:  pkgconfig(freealut)
BuildRequires:  pkgconfig(jack)
BuildRequires:  pkgconfig(ao)
BuildRequires:  pkgconfig(ogg)
BuildRequires:  pkgconfig(samplerate)
BuildRequires:  pkgconfig(sndfile)
BuildRequires:  pkgconfig(vorbis)
BuildRequires:  pkgconfig(opus)

# Typography stuff
BuildRequires:  fontpackages-devel
BuildRequires:  pkgconfig(freetype2)

# Appstream stuff
BuildRequires:  libappstream-glib

Requires:       google-droid-sans-fonts
Requires:       hicolor-icon-theme
Requires:       %{name}-fonts = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       fontpackages-filesystem
Requires:       python3-numpy
Requires:       python3-requests
Provides:       blender(ABI) = %{blender_api}

# Obsolete the standalone Blender player retired by upstream
Obsoletes:      blenderplayer < 1:2.80-1
Provides:       blenderplayer = 1:2.80-1

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

%package fonts
Summary:        International Blender mono space font
License:        ASL 2.0 and GPLv3 and Bitstream Vera and Public Domain
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

# Fix all Python shebangs recursively in .
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" .

mkdir cmake-make

%build
pushd cmake-make

%cmake .. \
%ifnarch %{ix86} x86_64
    -DWITH_RAYOPTIMIZATION=OFF \
%endif
    -DBOOST_ROOT=%{_prefix} \
    -DBUILD_SHARED_LIBS=OFF \
    -DCMAKE_SKIP_RPATH=ON \
    -DPYTHON_VERSION=%{python3_version} \
    -DOpenGL_GL_PREFERENCE=GLVND \
    %{?_without_ffmpeg:-DWITH_CODEC_FFMPEG=OFF} \
    -DWITH_CYCLES=%{cyclesflag} \
    -DWITH_DOC_MANPAGE=ON \
    -DWITH_INSTALL_PORTABLE=OFF \
    -DWITH_PYTHON_INSTALL=OFF \
    -DWITH_PYTHON_INSTALL_REQUESTS=OFF \
    -DWITH_PYTHON_SAFETY=ON \
%if 0%{?_with_cuda}
    -DCUDA_NVCC_EXECUTABLE=%{_bindir}/nvcc \
    -DCYCLES_CUDA_BINARIES_ARCH="sm_30;sm_35;sm_37;sm_50;sm_52;sm_60;sm_61;sm_70;sm_75" \
    -DWITH_CYCLES_CUDA_BINARIES=ON \
    -DWITH_CYCLES_CUDA_BUILD_SERIAL=ON
%endif

%make_build
popd


%install
pushd cmake-make
%make_install
popd


# Thumbnailer
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_datadir}/thumbnailers/%{name}.thumbnailer

# Mime support
install -p -D -m 644 %{SOURCE5} %{buildroot}%{_datadir}/mime/packages/%{name}.xml

# Deal with docs in the files section
rm -rf %{buildroot}%{_docdir}/%{name}/*

# rpm macros
mkdir -p %{buildroot}%{macrosdir}
sed -e 's/@VERSION@/%{blender_api}/g' %{SOURCE10} > %{buildroot}%{macrosdir}/macros.%{name}

# AppData
install -p -m 644 -D release/freedesktop/org.%{name}.Blender.appdata.xml \
          %{buildroot}%{_metainfodir}/%{name}.appdata.xml
install -p -m 644 -D %{SOURCE2} %{buildroot}%{_metainfodir}/%{name}-fonts.metainfo.xml

# Localization
%find_lang %{name}

# Avoid having locales listed twice
rm -fr %{buildroot}%{_datadir}/%{blender_api}/locale/languages

# rpmlint fixes
find %{buildroot}%{_datadir}/%{name}/%{blender_api}/scripts -name "*.py" -exec chmod 755 {} \;
#find %%{buildroot}%%{_datadir}/%%{name}/scripts -type f -exec sed -i -e 's/\r$//g' {} \;

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{name}.appdata.xml
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{name}-fonts.metainfo.xml

%files -f %{name}.lang
%license COPYING
%license doc/license/*-license.txt
%license release/text/copyright.txt
%doc release/text/readme.html
%{_bindir}/%{name}
%{_bindir}/%{name}-thumbnailer.py
%{_datadir}/applications/%{name}.desktop
%{_datadir}/%{name}/
%exclude %{_datadir}/%{name}/%{blender_api}/scripts/addons/cycles/lib/*.cubin
%{_datadir}/icons/hicolor/*/apps/%{name}*.*
%{_datadir}/mime/packages/%{name}.xml
%{_datadir}/thumbnailers/%{name}.thumbnailer
%{_mandir}/man1/%{name}.*
%{_metainfodir}/%{name}.appdata.xml

%files rpm-macros
%{macrosdir}/macros.%{name}

%files fonts
%license release/datafiles/LICENSE-*.ttf.txt
%{_fontbasedir}/%{name}/
%{_metainfodir}/%{name}-fonts.metainfo.xml

%{?_with_cuda:
%files cuda
%{_datadir}/%{name}/%{blender_api}/scripts/addons/cycles/lib/*.cubin
}

%changelog
* Sat Apr 04 2020 Simone Caronni <negativo17@gmail.com> - 2:2.82a-3
- Rebase on Fedora's master branch.

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
 
* Sat Dec 14 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.81a-3
- Rebuild for openvdb 7.0.0

* Thu Dec 12 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.81a-2
- Rebuilt for openvdb 7.0.0

* Thu Dec 05 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.81a-1
- Update to 2.81a

* Thu Nov 21 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.81-2
- Temporarily exclude ppc64le and armv7hl architectures due to failure

* Thu Nov 21 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.81-1
- Update to 2.81
- Drop upstream patch
- Enable oidn support for x86_64 architecture 
- Patch on appdata fixing tags

* Sun Nov 03 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.80-13
- Rebuilt for alembic 1.7.12

* Sat Nov 02 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.80-12
- Rebuilt with opensubdiv

* Wed Oct 16 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.80-11
- Upstream patch fixing compatibility with python 3.8

* Sun Oct 13 2019 Simone Caronni <negativo17@gmail.com> - 1:2.80-10
- Actually re-enable OpenVDB.

* Tue Sep 24 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.80-9
- Enable OpenSubDiv (rhbz#1754797)
- Rebuilt for openvdb 6.2.0
- Use provided upsteam metadata

* Thu Aug 22 2019 Miro Hrončok <mhroncok@redhat.com> - 1:2.80-8
- Rebuilt for Python 3.8

* Mon Aug 19 2019 Simone Caronni <negativo17@gmail.com> - 1:2.80-7
- Enable OpenVDB.

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 1:2.80-6
- Rebuilt for Python 3.8

* Sun Aug 18 2019 Simone Caronni <negativo17@gmail.com> - 1:2.80-5
- Clean up patches/sources.
- Fix installation of locales, scripts, thumbnailer, etc.
- Rpmlint fixes.
- Add ppc64le and s390x support.

* Thu Aug 15 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.80-4
- Restore broken international fonts support

* Wed Aug 14 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.80-3
- Set embree dependency to x86_64 architecture
- Temporarily disable build for ppc64le and s390x

* Tue Jul 30 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.80-2
- Enable embree, webp and bzip support
- Remove game engine support dropped from upstream
- Drop blenderplayer standalone package

* Tue Jul 30 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.80-1
- Update to 2.80

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:2.79b-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sat May 18 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.79b-17
- Rebuild for alembic 1.7.11

* Wed Apr 10 2019 Richard Shaw <hobbes1069@gmail.com> - 1:2.79b-16
- Rebuild for OpenEXR 2.3.0.

* Thu Apr 04 2019 Richard Shaw <hobbes1069@gmail.com> - 1:2.79b-15
- Rebuild for OpenColorIO 1.1.1.

* Wed Apr 03 01:33:05 CET 2019 Robert-André Mauchin <zebob.m@gmail.com> - 1:2.79b-14
- Fix build for GCC9 new OpenMP data sharing

* Thu Mar 14 2019 Mohan Boddu <mboddu@bhujji.com> - 1:2.79b-13
- Rebuild for OpenImageIO 2.0.5

* Thu Mar 14 2019 Luya Tshimbalanga <luya@fedoraproject.org> - 1:2.79b-12
- Rebuild for boost 1.69

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:2.79b-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild
