%bcond_without bootstrap

# LTO triggers a compilation error for a source level issue.  Given that LTO should not
# change the validity of any given source and the nature of the error (undefined enum), I
# suspect a generator program is mis-behaving in some way.  This needs further debugging,
# until that's done, disable LTO.  This has to happen before setting the flags below.
%define _lto_cflags %{nil}

%global dotnetver 7.0

%global host_version 7.0.3
%global runtime_version 7.0.3
%global aspnetcore_runtime_version %{runtime_version}
%global sdk_version 7.0.201
%global sdk_feature_band_version 7.0.100
%global templates_version %{runtime_version}
#%%global templates_version %%(echo %%{runtime_version} | awk 'BEGIN { FS="."; OFS="." } {print $1, $2, $3+1 }')

%global host_rpm_version %{host_version}
%global runtime_rpm_version %{runtime_version}
%global aspnetcore_runtime_rpm_version %{aspnetcore_runtime_version}
%global sdk_rpm_version %{sdk_version}

# upstream can update releases without revving the SDK version so these don't always match
%global upstream_tag v%{sdk_version}

%global use_bundled_libunwind 0

%ifarch %{aarch64} ppc64le s390x
%global use_bundled_libunwind 1
%endif

%ifarch %{aarch64}
%global runtime_arch arm64
%endif
%ifarch ppc64le
%global runtime_arch ppc64le
%endif
%ifarch s390x
%global runtime_arch s390x
%endif
%ifarch %{x86_64}
%global runtime_arch x64
%endif

%global mono_archs s390x ppc64le

%{!?runtime_id:%global runtime_id %(. /etc/os-release ; echo "${ID}.${VERSION_ID}")-%{runtime_arch}}

Name:           dotnet%{dotnetver}
Version:        %{sdk_rpm_version}
Release:        2
Summary:        .NET Runtime and SDK
License:        0BSD AND Apache-2.0 AND (Apache-2.0 WITH LLVM-Exception) AND APSL-2.0 AND BSD-2-Clause AND BSD-3-Clause AND BSD-4-Clause AND BSL-1.0 AND bzip2-1.0.6 AND CC0-1.0 AND CC-BY-3.0 AND CC-BY-4.0 AND CC-PDDC AND CNRI-Python AND EPL-1.0 AND GPL-2.0-only AND (GPL-2.0-only WITH GCC-exception-2.0) AND GPL-2.0-or-later AND GPL-3.0-only AND ICU AND ISC AND LGPL-2.1-only AND LGPL-2.1-or-later AND LicenseRef-Fedora-Public-Domain AND LicenseRef-ISO-8879 AND MIT AND MIT-Wu AND MS-PL AND MS-RL AND NCSA AND OFL-1.1 AND OpenSSL AND Unicode-DFS-2015 AND Unicode-DFS-2016 AND W3C-19980720 AND X11 AND Zlib

URL:            https://github.com/dotnet/

%if %{with bootstrap}
# The source is generated on a Cooker box via:
# ./build-dotnet-tarball --bootstrap %%{upstream_tag}
Source0:        dotnet-%{upstream_tag}-x64-bootstrap.tar.xz
# Generated via ./build-arm64-bootstrap-tarball
Source1:        dotnet-arm64-prebuilts-2022-10-12.tar.gz
# Generated manually, same pattern as the arm64 tarball
Source2:        dotnet-ppc64le-prebuilts-2022-10-21.tar.gz
# Generated manually, same pattern as the arm64 tarball
Source3:        dotnet-s390x-prebuilts-2022-10-12.tar.gz
%else
# The source is generated on a Fedora box via:
# ./build-dotnet-tarball %%{upstream_tag}
Source0:        dotnet-%{upstream_tag}.tar.gz
%endif

Source10:       check-debug-symbols.py
Source11:       dotnet.sh.in

# Disable apphost; there's no net6.0 apphost for ppc64le
Patch1:        roslyn-analyzers-ppc64le-apphost.patch


ExclusiveArch:  %{aarch64} ppc64le s390x %{x86_64}


BuildRequires:  clang
BuildRequires:  cmake
BuildRequires:  coreutils
%if %{without bootstrap}
BuildRequires:  dotnet-sdk-%{dotnetver}
BuildRequires:  dotnet-sdk-%{dotnetver}-source-built-artifacts
%endif
BuildRequires:  findutils
BuildRequires:  git
BuildRequires:  locales-en
BuildRequires:  hostname
BuildRequires:  krb5-devel
BuildRequires:  libicu-devel
%if ! %{use_bundled_libunwind}
BuildRequires:  libunwind-devel
%endif
%ifarch %{aarch64}
BuildRequires:  lld
%endif
# If the build ever crashes, then having lldb installed might help the
# runtime generate a backtrace for the crash
BuildRequires:  lldb
BuildRequires:  llvm
BuildRequires:  make
BuildRequires:  pkgconfig(lttng-ust)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  python3
BuildRequires:  tar
BuildRequires:  util-linux
BuildRequires:  zlib-devel

# Avoid generating provides and requires for private libraries
%global privlibs             libhostfxr
%global privlibs %{privlibs}|libclrgc
%global privlibs %{privlibs}|libclrjit
%global privlibs %{privlibs}|libcoreclr
%global privlibs %{privlibs}|libcoreclrtraceptprovider
%global privlibs %{privlibs}|libhostpolicy
%global privlibs %{privlibs}|libmscordaccore
%global privlibs %{privlibs}|libmscordbi
%global privlibs %{privlibs}|libnethost
%global privlibs %{privlibs}|libSystem.Globalization.Native
%global privlibs %{privlibs}|libSystem.IO.Compression.Native
%global privlibs %{privlibs}|libSystem.Native
%global privlibs %{privlibs}|libSystem.Net.Security.Native
%global privlibs %{privlibs}|libSystem.Security.Cryptography.Native.OpenSsl
%global __provides_exclude ^(%{privlibs})\\.so
%global __requires_exclude ^(%{privlibs})\\.so


%description
.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, macOS and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.

.NET contains a runtime conforming to .NET Standards a set of
framework libraries, an SDK containing compilers and a 'dotnet'
application to drive everything.


%package -n dotnet-host

Version:        %{host_rpm_version}
Summary:        .NET command line launcher

%description -n dotnet-host
The .NET host is a command line program that runs a standalone
.NET application or launches the SDK.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-hostfxr-%{dotnetver}

Version:        %{host_rpm_version}
Summary:        .NET command line host resolver

# Theoretically any version of the host should work. But lets aim for the one
# provided by this package, or from a newer version of .NET
Requires:       dotnet-host%{?_isa} >= %{host_rpm_version}-%{release}

%description -n dotnet-hostfxr-%{dotnetver}
The .NET host resolver contains the logic to resolve and select
the right version of the .NET SDK or runtime to use.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-runtime-%{dotnetver}

Version:        %{runtime_rpm_version}
Summary:        NET %{dotnetver} runtime

Requires:       dotnet-hostfxr-%{dotnetver}%{?_isa} >= %{host_rpm_version}-%{release}

# libicu is dlopen()ed
Requires:       libicu%{?_isa}

# See src/runtime/src/libraries/Native/AnyOS/brotli-version.txt
Provides: bundled(libbrotli) = 1.0.9
%if %{use_bundled_libunwind}
# See src/runtime/src/coreclr/pal/src/libunwind/libunwind-version.txt
Provides: bundled(libunwind) = 1.5.rc1.28.g9165d2a1
%endif

%description -n dotnet-runtime-%{dotnetver}
The .NET runtime contains everything needed to run .NET applications.
It includes a high performance Virtual Machine as well as the framework
libraries used by .NET applications.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n aspnetcore-runtime-%{dotnetver}

Version:        %{aspnetcore_runtime_rpm_version}
Summary:        ASP.NET Core %{dotnetver} runtime

Requires:       dotnet-runtime-%{dotnetver}%{?_isa} = %{runtime_rpm_version}-%{release}

%description -n aspnetcore-runtime-%{dotnetver}
The ASP.NET Core runtime contains everything needed to run .NET
web applications. It includes a high performance Virtual Machine as
well as the framework libraries used by .NET applications.

ASP.NET Core is a fast, lightweight and modular platform for creating
cross platform web applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-templates-%{dotnetver}

Version:        %{sdk_rpm_version}
Summary:        .NET %{dotnetver} templates

# Theoretically any version of the host should work. But lets aim for the one
# provided by this package, or from a newer version of .NET
Requires:       dotnet-host%{?_isa} >= %{host_rpm_version}-%{release}

%description -n dotnet-templates-%{dotnetver}
This package contains templates used by the .NET SDK.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-sdk-%{dotnetver}

Version:        %{sdk_rpm_version}
Summary:        .NET %{dotnetver} Software Development Kit

Provides:       bundled(js-jquery)

Requires:       dotnet-runtime-%{dotnetver}%{?_isa} >= %{runtime_rpm_version}-%{release}
Requires:       aspnetcore-runtime-%{dotnetver}%{?_isa} >= %{aspnetcore_runtime_rpm_version}-%{release}

Requires:       dotnet-apphost-pack-%{dotnetver}%{?_isa} >= %{runtime_rpm_version}-%{release}
Requires:       dotnet-targeting-pack-%{dotnetver}%{?_isa} >= %{runtime_rpm_version}-%{release}
Requires:       aspnetcore-targeting-pack-%{dotnetver}%{?_isa} >= %{aspnetcore_runtime_rpm_version}-%{release}
Requires:       netstandard-targeting-pack-2.1%{?_isa} >= %{sdk_rpm_version}-%{release}

Requires:       dotnet-templates-%{dotnetver}%{?_isa} >= %{sdk_rpm_version}-%{release}

%description -n dotnet-sdk-%{dotnetver}
The .NET SDK is a collection of command line applications to
create, build, publish and run .NET applications.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%global dotnet_targeting_pack() %{expand:
%package -n %{1}

Version:        %{2}
Summary:        Targeting Pack for %{3} %{4}

Requires:       dotnet-host%{?_isa}

%description -n %{1}
This package provides a targeting pack for %{3} %{4}
that allows developers to compile against and target %{3} %{4}
applications using the .NET SDK.

%files -n %{1}
%dir %{_libdir}/dotnet/packs
%{_libdir}/dotnet/packs/%{5}
}

%dotnet_targeting_pack dotnet-apphost-pack-%{dotnetver} %{runtime_rpm_version} Microsoft.NETCore.App %{dotnetver} Microsoft.NETCore.App.Host.%{runtime_id}
%dotnet_targeting_pack dotnet-targeting-pack-%{dotnetver} %{runtime_rpm_version} Microsoft.NETCore.App %{dotnetver} Microsoft.NETCore.App.Ref
%dotnet_targeting_pack aspnetcore-targeting-pack-%{dotnetver} %{aspnetcore_runtime_rpm_version} Microsoft.AspNetCore.App %{dotnetver} Microsoft.AspNetCore.App.Ref
%dotnet_targeting_pack netstandard-targeting-pack-2.1 %{sdk_rpm_version} NETStandard.Library 2.1 NETStandard.Library.Ref


%package -n dotnet-sdk-%{dotnetver}-source-built-artifacts

Version:        %{sdk_rpm_version}
Summary:        Internal package for building .NET %{dotnetver} Software Development Kit

%description -n dotnet-sdk-%{dotnetver}-source-built-artifacts
The .NET source-built archive is a collection of packages needed
to build the .NET SDK itself.

These are not meant for general use.


%prep
%if %{without bootstrap}
%setup -q -n dotnet-%{upstream_tag}

# Remove all prebuilts
find -iname '*.dll' -type f -delete
find -iname '*.so' -type f -delete
find -iname '*.tar.gz' -type f -delete
find -iname '*.nupkg' -type f -delete
find -iname '*.zip' -type f -delete

rm -rf .dotnet/
rm -rf packages/source-built

mkdir -p packages/archive
ln -s %{_libdir}/dotnet/source-built-artifacts/Private.SourceBuilt.Artifacts.*.tar.gz packages/archive/

%else

%setup -q -T -b 0 -n dotnet-%{upstream_tag}-x64-bootstrap

%ifnarch %{x86_64}

rm -rf .dotnet
%ifarch %{aarch64}
tar -x --strip-components=1 -f %{SOURCE1} -C packages/prebuilt
%endif
%ifarch ppc64le
tar -x --strip-components=1 -f %{SOURCE2} -C packages/prebuilt
%endif
%ifarch s390x
tar -x --strip-components=1 -f %{SOURCE3} -C packages/prebuilt
%endif

mkdir -p .dotnet
tar xf packages/prebuilt/dotnet-sdk*.tar.gz -C .dotnet/
rm packages/prebuilt/dotnet-sdk*.tar.gz

boot_sdk_version=$(ls -1 .dotnet/sdk/)
sed -i -E 's|"dotnet": "[^"]+"|"dotnet" : "'$boot_sdk_version'"|' global.json

%ifarch ppc64le s390x
ilasm_version=$(ls packages/prebuilt| grep -i ilasm | tr 'A-Z' 'a-z' | sed -E 's|runtime.linux-'%{runtime_arch}'.microsoft.netcore.ilasm.||' | sed -E 's|.nupkg$||')
echo $ilasm_version

mkdir -p packages-customized-local
pushd packages-customized-local
tar xf ../packages/archive/Private.SourceBuilt.Artifacts.*.tar.gz
sed -i -E 's|<MicrosoftNETCoreILAsmVersion>[^<]+</MicrosoftNETCoreILAsmVersion>|<MicrosoftNETCoreILAsmVersion>'$ilasm_version'</MicrosoftNETCoreILAsmVersion>|' PackageVersions.props
sed -i -E 's|<MicrosoftNETCoreILDAsmVersion>[^<]+</MicrosoftNETCoreILDAsmVersion>|<MicrosoftNETCoreILDAsmVersion>'$ilasm_version'</MicrosoftNETCoreILDAsmVersion>|' PackageVersions.props
tar czf ../packages/archive/Private.SourceBuilt.Artifacts.*.tar.gz *
popd

%endif

%endif

%endif

%autopatch -p1

# Fix bad hardcoded path in build
sed -i 's|/usr/share/dotnet|%{_libdir}/dotnet|' src/runtime/src/native/corehost/hostmisc/pal.unix.cpp

%if ! %{use_bundled_libunwind}
sed -i -E 's|( /p:BuildDebPackage=false)|\1 --cmakeargs -DCLR_CMAKE_USE_SYSTEM_LIBUNWIND=TRUE|' src/runtime/eng/SourceBuild.props
%endif


%build
cat /etc/os-release

%if %{without bootstrap}
# We need to create a copy because we will mutate this
cp -a %{_libdir}/dotnet previously-built-dotnet
find previously-built-dotnet
%endif

# Setting this macro ensures that only clang supported options will be
# added to ldflags and cflags.
%global toolchain clang
%set_build_flags

# -fstack-clash-protection breaks CoreCLR
CFLAGS=$(echo $CFLAGS  | sed -e 's/-fstack-clash-protection//' )
CXXFLAGS=$(echo $CXXFLAGS  | sed -e 's/-fstack-clash-protection//' )

%ifarch %{aarch64}
# -mbranch-protection=standard breaks unwinding in CoreCLR through libunwind
CFLAGS=$(echo $CFLAGS | sed -e 's/-mbranch-protection=standard //')
CXXFLAGS=$(echo $CXXFLAGS | sed -e 's/-mbranch-protection=standard //')
%endif

%ifarch s390x
# -march=z13 -mtune=z14 makes clang crash while compiling .NET
CFLAGS=$(echo $CFLAGS | sed -e 's/ -march=z13//')
CFLAGS=$(echo $CFLAGS | sed -e 's/ -mtune=z14//')
CXXFLAGS=$(echo $CXXFLAGS | sed -e 's/ -march=z13//')
CXXFLAGS=$(echo $CXXFLAGS | sed -e 's/ -mtune=z14//')
%endif

export EXTRA_CFLAGS="$CFLAGS"
export EXTRA_CXXFLAGS="$CXXFLAGS"
export EXTRA_LDFLAGS="$LDFLAGS"

# Disable tracing, which is incompatible with certain versions of
# lttng See https://github.com/dotnet/runtime/issues/57784. The
# suggested compile-time change doesn't work, unfortunately.
export COMPlus_LTTng=0

# OpenSSL 3.0 in RHEL 9 and newer versions of Fedora has disabled
# SHA1, used by .NET for strong name signing. See
# https://github.com/dotnet/runtime/issues/67304
# https://gitlab.com/redhat/centos-stream/rpms/openssl/-/commit/78fb78d30755ae18fdaef28ef392f4e67c662ff6
export OPENSSL_ENABLE_SHA1_SIGNATURES=1

VERBOSE=1 ./build.sh \
%if %{without bootstrap}
    --with-sdk previously-built-dotnet \
%endif
%ifarch %{mono_archs}
    --use-mono-runtime \
%endif
    -- \
    /p:MinimalConsoleLogOutput=false \
    /p:ContinueOnPrebuiltBaselineError=true \
    /v:n \
    /p:LogVerbosity=n \


echo \
    /p:SkipPortableRuntimeBuild=true \


sed -e 's|[@]LIBDIR[@]|%{_libdir}|g' %{SOURCE11} > dotnet.sh


%install
install -dm 0755 %{buildroot}%{_libdir}/dotnet
ls artifacts/%{runtime_arch}/Release
tar xf artifacts/%{runtime_arch}/Release/dotnet-sdk-%{sdk_version}-%{runtime_id}.tar.gz -C %{buildroot}%{_libdir}/dotnet/

# See https://github.com/dotnet/source-build/issues/2579
find %{buildroot}%{_libdir}/dotnet/ -type f -name 'testhost.x86' -delete
find %{buildroot}%{_libdir}/dotnet/ -type f -name 'vstest.console' -delete

# Install managed symbols: disabled because they don't contain sources
# but point to the paths the sources would have been at in the build
# servers. The end user experience is pretty bad atm.
# tar xf artifacts/%%{runtime_arch}/Release/runtime/dotnet-runtime-symbols-%%{runtime_id}-%%{runtime_version}.tar.gz \
#    -C %%{buildroot}/%%{_libdir}/dotnet/shared/Microsoft.NETCore.App/%%{runtime_version}/

# Fix executable permissions on files
find %{buildroot}%{_libdir}/dotnet/ -type f -name 'apphost' -exec chmod +x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name 'singlefilehost' -exec chmod +x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name 'lib*so' -exec chmod +x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.a' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.dll' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.h' -exec chmod 0644 {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.json' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.pdb' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.props' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.pubxml' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.targets' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.txt' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.xml' -exec chmod -x {} \;

install -dm 0755 %{buildroot}%{_sysconfdir}/profile.d/
install dotnet.sh %{buildroot}%{_sysconfdir}/profile.d/

install -dm 0755 %{buildroot}/%{_datadir}/bash-completion/completions
# dynamic completion needs the file to be named the same as the base command
install src/sdk/scripts/register-completions.bash %{buildroot}/%{_datadir}/bash-completion/completions/dotnet

# TODO: the zsh completion script needs to be ported to use #compdef
#install -dm 755 %%{buildroot}/%%{_datadir}/zsh/site-functions
#install src/cli/scripts/register-completions.zsh %%{buildroot}/%%{_datadir}/zsh/site-functions/_dotnet

install -dm 0755 %{buildroot}%{_bindir}
ln -s ../../%{_libdir}/dotnet/dotnet %{buildroot}%{_bindir}/

for section in 1 7; do
    install -dm 0755 %{buildroot}%{_mandir}/man${section}/
    find -iname 'dotnet*'.${section} -type f -exec cp {} %{buildroot}%{_mandir}/man${section}/ \;
done

install -dm 0755 %{buildroot}%{_sysconfdir}/dotnet
echo "%{_libdir}/dotnet" >> install_location
install install_location %{buildroot}%{_sysconfdir}/dotnet/
echo "%{_libdir}/dotnet" >> install_location_%{runtime_arch}
install install_location_%{runtime_arch} %{buildroot}%{_sysconfdir}/dotnet/

install -dm 0755 %{buildroot}%{_libdir}/dotnet/source-built-artifacts
install -m 0644 artifacts/%{runtime_arch}/Release/Private.SourceBuilt.Artifacts.*.tar.gz %{buildroot}/%{_libdir}/dotnet/source-built-artifacts/


# Quick and dirty check for https://github.com/dotnet/source-build/issues/2731
test -f %{buildroot}%{_libdir}/dotnet/sdk/%{sdk_version}/Sdks/Microsoft.NET.Sdk/Sdk/Sdk.props

# Check debug symbols in all elf objects. This is not in %%check
# because native binaries are stripped by rpm-build after %%install.
# So we need to do this check earlier.
echo "Testing build results for debug symbols..."
%{SOURCE10} -v %{buildroot}%{_libdir}/dotnet/



%check
# lttng in Fedora > 35 is incompatible with .NET
# FIXME need to see if that's true for OM
#export COMPlus_LTTng=0

%{buildroot}%{_libdir}/dotnet/dotnet --info
%{buildroot}%{_libdir}/dotnet/dotnet --version

%files -n dotnet-host
%dir %{_libdir}/dotnet
%{_libdir}/dotnet/dotnet
%dir %{_libdir}/dotnet/host
%dir %{_libdir}/dotnet/host/fxr
%{_bindir}/dotnet
%license %{_libdir}/dotnet/LICENSE.txt
%license %{_libdir}/dotnet/ThirdPartyNotices.txt
%doc %{_mandir}/man1/dotnet*.1.*
%doc %{_mandir}/man7/dotnet*.7.*
%config(noreplace) %{_sysconfdir}/profile.d/dotnet.sh
%config(noreplace) %{_sysconfdir}/dotnet
%dir %{_datadir}/bash-completion
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/dotnet

%files -n dotnet-hostfxr-%{dotnetver}
%dir %{_libdir}/dotnet/host/fxr
%{_libdir}/dotnet/host/fxr/%{host_version}

%files -n dotnet-runtime-%{dotnetver}
%dir %{_libdir}/dotnet/shared
%dir %{_libdir}/dotnet/shared/Microsoft.NETCore.App
%{_libdir}/dotnet/shared/Microsoft.NETCore.App/%{runtime_version}

%files -n aspnetcore-runtime-%{dotnetver}
%dir %{_libdir}/dotnet/shared
%dir %{_libdir}/dotnet/shared/Microsoft.AspNetCore.App
%{_libdir}/dotnet/shared/Microsoft.AspNetCore.App/%{aspnetcore_runtime_version}

%files -n dotnet-templates-%{dotnetver}
%dir %{_libdir}/dotnet/templates
%{_libdir}/dotnet/templates/%{templates_version}

%files -n dotnet-sdk-%{dotnetver}
%dir %{_libdir}/dotnet/sdk
%{_libdir}/dotnet/sdk/%{sdk_version}
%dir %{_libdir}/dotnet/sdk-manifests
%{_libdir}/dotnet/sdk-manifests/%{sdk_feature_band_version}
%{_libdir}/dotnet/metadata
%dir %{_libdir}/dotnet/packs

%files -n dotnet-sdk-%{dotnetver}-source-built-artifacts
%dir %{_libdir}/dotnet
%{_libdir}/dotnet/source-built-artifacts
