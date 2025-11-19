#!/bin/bash
#
# This script should be called by `cibuildwheel` in the `before-all` stage.

function install_packages
{
  /bin/echo -e "\n==> Installing packages using the package manager ...\n"
  # Install OpenBLAS since libblas.so on CentOS 7 does not have cblas functions.
  # CMake will prefer OpenBLAS over the generic libblas.so
  yum install -y boost169-devel fftw-devel openblas-devel wget
  # Install (other) Casacore dependencies
  yum install -y cfitsio-devel flex gsl-devel ncurses-devel readline-devel wcslib-devel
}

# Build a thread-safe HDF5 library. The hdf5-devel package is not threadsafe.
function download_and_build_hdf5
{
  /bin/echo -e "\n==> Downloading and unpacking HDF5 ${HDF5_VERSION} ...\n"
  site="https://support.hdfgroup.org"
  directory="ftp/HDF5/releases/hdf5-${HDF5_VERSION%.*}/hdf5-${HDF5_VERSION}/src"
  file="hdf5-${HDF5_VERSION}.tar.gz"
  url="${site}/${directory}/${file}"
  curl -fsSLo - "${url}" | tar -C "${WORKDIR}" -xzf -

  /bin/echo -e "\n==> Building and installing HDF5 ${HDF5_VERSION} ...\n"
  cd "${WORKDIR}/hdf5-${HDF5_VERSION}"
  ./configure \
    --quiet \
    --prefix /usr/local \
    --with-szlib \
    --enable-cxx \
    --disable-tests
  make --jobs=`nproc` --quiet install
}

# Build Casacore using a custom "everybeam::casacore" namespace.
function download_and_build_casacore
{
  echo -e "\n==> Downloading and unpacking Casacore ${CASACORE_VERSION} ...\n"
  url="https://github.com/casacore/casacore/archive/refs/tags/v${CASACORE_VERSION}.tar.gz"
  curl -fsSLo - "${url}" | tar -C "${WORKDIR}" -xzf -

  CASACORE_DATA=/usr/local/share/casacore/data
  mkdir -p ${CASACORE_DATA}
  url="https://www.astron.nl/iers/WSRT_Measures.ztar"
  curl -fsSLo - "${url}" | tar -C ${CASACORE_DATA} -xzf -

  echo -e "\n==> Building and installing Casacore ${CASACORE_VERSION} ...\n"
  mkdir -p "${WORKDIR}/casacore-build"
  cd "${WORKDIR}/casacore-build"
  # Override BOOST_* environment settings from pyproject.toml, so Casacore
  # cannot find Boost. It will then skip building tests.
  # (Some tests require a newer Boost version and do not build at all.)
  cmake \
    -DCMAKE_CXX_FLAGS="-Dcasacore=everybeam::casacore" \
    -DBUILD_PYTHON=OFF \
    -DBUILD_PYTHON3=OFF \
    -DBUILD_TESTING=OFF \
    -DBOOST_INCLUDEDIR=/does/not/exist \
    -DBOOST_LIBRARYDIR=/does/not/exist \
    "${WORKDIR}/casacore-${CASACORE_VERSION}"
  make --jobs=`nproc` --quiet install
}

set -euo pipefail
install_packages
download_and_build_casacore
download_and_build_hdf5
