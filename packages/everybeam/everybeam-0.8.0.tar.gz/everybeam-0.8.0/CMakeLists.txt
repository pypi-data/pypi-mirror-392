# Copyright (C) 2021 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

#------------------------------------------------------------------------------
# Top level CMakeLists.txt file for EveryBeam
cmake_minimum_required(VERSION 3.15)

include(CheckFunctionExists)

#------------------------------------------------------------------------------
# Set version name and project number
set(EVERYBEAM_VERSION 0.8.0) # Keep in sync with `pyproject.toml` file
if(EVERYBEAM_VERSION MATCHES "^([0-9]+)\\.([0-9]+)\\.([0-9]+)")
  set(EVERYBEAM_VERSION_MAJOR "${CMAKE_MATCH_1}")
  set(EVERYBEAM_VERSION_MINOR "${CMAKE_MATCH_2}")
  set(EVERYBEAM_VERSION_PATCH "${CMAKE_MATCH_3}")
else()
  message(
    FATAL_ERROR "Failed to parse EVERYBEAM_VERSION='${EVERYBEAM_VERSION}'")
endif()

project(
  EveryBeam
  VERSION ${EVERYBEAM_VERSION}
  LANGUAGES CXX)

# CMake versions less than 3.17 do not support CMAKE_MESSAGE_LOG_LEVEL
# Fake it here to silence unwanted output
if(CMAKE_VERSION VERSION_LESS "3.17")
  function(message)
    if(ARGC EQUAL 0)
      return()
    endif()
    if(CMAKE_MESSAGE_LOG_LEVEL STREQUAL "ERROR")
      if((NOT ARGV0 STREQUAL "FATAL_ERROR") AND (NOT ARGV0 STREQUAL "SEND_ERROR"
                                                ))
        return()
      endif()
    endif()
    _message(${ARGN})
  endfunction()
endif()

# An empty CMAKE_BUILD_TYPE results in an incomplete installation of
# ska-sdp-func, added to the project through FetchContent().
# Running cmake again after a 'make install' will result in an error due
# to this incomplete installation being found in the CMAKE_INSTALL_PREFIX
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
  message(STATUS "Setting CMAKE_BUILD_TYPE to ${CMAKE_BUILD_TYPE}")
endif()

option(BUILD_WITH_PYTHON "Build python bindings" OFF)
option(BUILD_APT_PACKAGES "Build apt package" OFF)
option(BUILD_TESTING "Build tests" OFF)
option(DOWNLOAD_LOBES "Download and install LOBEs coefficient files" OFF)
option(DOWNLOAD_LWA "Download and install OVRO-LWA coefficient file" OFF)
option(PORTABLE "Build portable binaries (with slightly decreased performance)"
       OFF)

string(TOLOWER ${CMAKE_PROJECT_NAME} projectname)

# When the software is built with, e.g., `pip` or `build`, `scikit-build-core`
# controls the build, and software will be installed in `site-packages`. In
# this case we do not want to install libraries in `lib`, but instead follow
# the convention of installing libraries in a directory `<package>.libs`.
if(SKBUILD)
  set(INSTALL_LIBDIR everybeam.libs)
else()
  set(INSTALL_LIBDIR lib)
endif()

# Set the path to CMake modules
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/CMake)

# Hide internal symbols. Hide C symbols, too, since ska-sdp-func contains C.
set(CMAKE_C_VISIBILITY_PRESET "hidden")
set(CMAKE_CXX_VISIBILITY_PRESET "hidden")

# Build an ska-sdp-func library, for inclusion into EveryBeam.
include(FetchContent)
message(STATUS "Fetching and configuring ska-sdp-func")

# Disable CUDA support for ska-sdp-func, since it may cause compilation errors
# if CUDA is found. Currently, EveryBeam does not use any CUDA functions.
set(FIND_CUDA
    OFF
    CACHE INTERNAL "")

FetchContent_Declare(
  ska_sdp_func
  GIT_REPOSITORY "https://gitlab.com/ska-telescope/sdp/ska-sdp-func.git"
  GIT_TAG 1.2.2
  PATCH_COMMAND
    # Turn the ska-sdp-func library from a shared library into an 'OBJECT'
    # library. Bundling ska-sdp-func statically this way avoids conflicts with
    # other ska-sdp-func library installations.
    # Since EveryBeam only uses few functions from ska-sdp-func (for OSKAR),
    # the overhead of including these objects in EveryBeam is minimal.
    #
    # In the command, replace \ by \\\\ since CMake first copies the string to
    # an ExternalProject_Add command in another CMakeLists.txt file, and the
    # command needs \\ escapes at that point.
    sed -i "s=\\\\(add_library(.{PROJECT_NAME}\\\\) \\\\$=\\\\1 OBJECT $=g"
    CMakeLists.txt)
FetchContent_MakeAvailable(ska_sdp_func)

message(STATUS "Finished configuring ska-sdp-func")

# Configure directory for data files
add_compile_options(
  -O3
  -Wall
  -Wnon-virtual-dtor
  -Wzero-as-null-pointer-constant
  -Wduplicated-branches
  -Wundef
  -Wvla
  -Wpointer-arith
  -Wextra
  -Wno-unused-parameter)

string(APPEND CMAKE_SHARED_LINKER_FLAGS " -Wl,--no-undefined")
# Note: Use type `STRING` here, instead of `PATH`. Because, if the user
# specified a _relative_ path on the command-line without specifying the type
# `PATH`, then the `set` command will treat the path as relative to the current
# working directory and convert it to an absolute path. We do *not* want this!
set(EVERYBEAM_DATADIR
    "share/${projectname}"
    CACHE STRING "EveryBeam data directory")
if(IS_ABSOLUTE ${EVERYBEAM_DATADIR})
  set(EVERYBEAM_ABSOLUTE_DATADIR "${EVERYBEAM_DATADIR}")
else()
  set(EVERYBEAM_ABSOLUTE_DATADIR "${CMAKE_INSTALL_PREFIX}/${EVERYBEAM_DATADIR}")
endif()

# When the software is built with, e.g., `pip` or `build`, `scikit-build-core`
# controls the build. In this case we need to follow the naming convention in
# PEP-491 for the data directory, otherwise the data files will not be
# installed in the right directory when the python wheel is unpacked.
if(SKBUILD)
  # Following naming convention of data directory in PEP 491
  set(EVERYBEAM_INSTALL_DATADIR
      "${projectname}-${EVERYBEAM_VERSION}.data/data/share/${projectname}")
else()
  set(EVERYBEAM_INSTALL_DATADIR ${EVERYBEAM_DATADIR})
endif()
message("Installing data files in: ${EVERYBEAM_INSTALL_DATADIR}")

# Find and include git submodules
find_package(Git QUIET)
if(GIT_FOUND AND EXISTS "${PROJECT_SOURCE_DIR}/.git")
  # Update submodules as needed
  option(GIT_SUBMODULE "Check submodules during build" ON)
  if(GIT_SUBMODULE)
    message(STATUS "Submodule update")
    execute_process(
      COMMAND ${GIT_EXECUTABLE} submodule update --init --recursive --checkout
              --depth 1
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      RESULT_VARIABLE GIT_SUBMOD_RESULT)
    if(NOT GIT_SUBMOD_RESULT EQUAL "0")
      message(
        FATAL_ERROR
          "git submodule update --init failed with ${GIT_SUBMOD_RESULT}, please checkout submodules"
      )
    endif()
  endif()
endif()

# Include logic that selects the target CPU for compilation
# User may optionally set `TARGET_CPU` if `PORTABLE=OFF`
include(external/aocommon/CMake/SetTargetCPU.cmake)

# Include aocommon/eigen3 headers
include_directories("${CMAKE_SOURCE_DIR}/external/aocommon/include")
include_directories(SYSTEM "${CMAKE_SOURCE_DIR}/external/eigen")

# Include schaapcommon, which also fetches the specified XTensor libraries.
set(XTENSOR_LIBRARIES xtl xtensor xtensor-blas xtensor-fftw)
set(SCHAAPCOMMON_MODULES h5parm)
add_subdirectory("${CMAKE_SOURCE_DIR}/external/schaapcommon")
include_directories("${CMAKE_SOURCE_DIR}/external/schaapcommon/include")

# Find and include HDF5
find_package(
  HDF5
  COMPONENTS CXX
  REQUIRED)
add_definitions(${HDF5_DEFINITIONS} -DH5_USE_110_API)
include_directories(SYSTEM ${HDF5_INCLUDE_DIRS})

find_package(Threads REQUIRED)

# Find and include Casacore
# Ignore version errors when building ReadTheDocs documentation.
set(CASACORE_MAKE_REQUIRED_EXTERNALS_OPTIONAL TRUE)
find_package(Casacore REQUIRED COMPONENTS casa ms tables measures fits)
include_directories(SYSTEM ${CASACORE_INCLUDE_DIRS})
if(CASACORE_VERSION VERSION_LESS "3.6" AND NOT DEFINED ENV{READTHEDOCS})
  message(
    FATAL_ERROR
      "This version of EveryBeam requires at least version 3.6 of Casacore (version found: ${CASACORE_VERSION})."
  )
endif()

# Find and include Boost headers (boost::math required for MWA beam)
find_package(
  Boost
  COMPONENTS date_time
  REQUIRED)
include_directories(SYSTEM ${Boost_INCLUDE_DIRS})

# Find and include FFTW3 float libraries
find_package(
  FFTW3
  COMPONENTS single
  REQUIRED)
include_directories(SYSTEM ${FFTW3_INCLUDE_DIR})

# Find BLAS and LAPACK, needed for everybeam::aterms only
find_package(BLAS REQUIRED)
find_package(LAPACK REQUIRED)

# Check if BLAS provides CBLAS functions. If it doesn't, use GSL.
set(CMAKE_REQUIRED_LIBRARIES ${BLAS_LIBRARIES})
check_function_exists(cblas_sgemv FOUND_CBLAS_SGEMV)
unset(CMAKE_REQUIRED_LIBRARIES)

if(NOT FOUND_CBLAS_SGEMV)
  message(
    NOTICE
    "BLAS library (${BLAS_LIBRARIES}) does not include cblas functions. Using GSL instead."
  )
  find_package(GSL REQUIRED)
  list(APPEND BLAS_LIBRARIES GSL::gslcblas)
endif()

# Find CFITSIO, needed for everybeam::aterms only
find_package(CFITSIO REQUIRED)
include_directories(SYSTEM ${CFITSIO_INCLUDE_DIRS})

#------------------------------------------------------------------------------
# Set CMake and compiler options

# wget needs to be installed in order to download coefficient files on the fly
include(FindWget)
if(NOT WGET_FOUND)
  message(FATAL_ERROR "wget not found. Install wget on your local system")
endif()

if(POLICY CMP0074)
  cmake_policy(SET CMP0074 NEW)
endif()

# Set compile options
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

# An investigation was done to determine if the --ffast-math
# compiler option was possible in Everybeam. The conclusion
# was that it was not advisable because of relevant numerical
# discrepancy. Learn the details at
# https://jira.skatelescope.org/browse/AST-1502.
add_compile_options(
  "${OpenMP_CXX_FLAGS}"
  -Wall
  -Wnon-virtual-dtor
  -Wzero-as-null-pointer-constant
  -Wduplicated-branches
  -Wundef
  -Wvla
  -Wpointer-arith
  -Wextra
  -Wno-unused-parameter)
string(APPEND CMAKE_SHARED_LINKER_FLAGS " -Wl,--no-undefined")

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
  # GCC 8.x requires linking with stdc++fs for the filesystem library
  # https://gcc.gnu.org/onlinedocs/gcc-9.1.0/libstdc++/manual/manual/status.html#status.iso.2017
  if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 9.0)
    link_libraries(stdc++fs)
  elseif(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 8.0)
    message(
      FATAL_ERROR "The GCC version is too old, upgrade to GCC 8.0 or newer")
  endif()
endif()

if(NOT CMAKE_BUILD_TYPE MATCHES Debug)
  add_compile_options(-DNDEBUG)
endif()

# The following stuff will set the "rpath" correctly, so that
# LD_LIBRARY_PATH doesn't have to be set.

# use, i.e. don't skip the full RPATH for the build tree
set(CMAKE_SKIP_BUILD_RPATH FALSE)
# when building, don't use the install RPATH already
# (but later on when installing)
set(CMAKE_BUILD_WITH_INSTALL_RPATH FALSE)
# add the automatically determined parts of the RPATH
# which point to directories outside the build tree to the install RPATH
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
# the RPATH to be used when installing, but only if it's not a system directory
list(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES
     "${CMAKE_INSTALL_PREFIX}/${INSTALL_LIBDIR}" isSystemDir)
if("${isSystemDir}" STREQUAL "-1")
  set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${INSTALL_LIBDIR}")
endif()

#------------------------------------------------------------------------------
# Set up a test_data directory in the build directory.
# Create symbolic links to the files/directories in the source directory.
if(${CMAKE_VERSION} VERSION_GREATER_EQUAL 3.14) # Required for file(CREATE_LINK)
  set(DATA_DIR ${CMAKE_BINARY_DIR}/test_data)
  file(MAKE_DIRECTORY ${DATA_DIR})
  file(GLOB SOURCE_DATA_FILES "${CMAKE_SOURCE_DIR}/test_data/*")
  foreach(SOURCE_DATA_FILE ${SOURCE_DATA_FILES})
    string(REPLACE ${CMAKE_SOURCE_DIR} ${CMAKE_BINARY_DIR} BINARY_DATA_FILE
                   ${SOURCE_DATA_FILE})
    file(CREATE_LINK ${SOURCE_DATA_FILE} ${BINARY_DATA_FILE} SYMBOLIC)
  endforeach()
else()
  # For older versions, fall back to using the source directory.
  set(DATA_DIR ${CMAKE_SOURCE_DIR}/test_data)
endif()

#------------------------------------------------------------------------------
# Add source
add_subdirectory(cpp)

#------------------------------------------------------------------------------
# Add tests
if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME AND BUILD_TESTING)
  include(CTest)

  add_subdirectory(cpp/test)

  # TODO: compiling the demos should probably be a different cmake project
  # in which we use find_package(EveryBeam)
  add_subdirectory(demo)
endif()

#------------------------------------------------------------------------------
# Generate config.h and version.h headers
configure_file(${CMAKE_SOURCE_DIR}/CMake/config.h.in
               ${CMAKE_BINARY_DIR}/config.h)
configure_file(${CMAKE_SOURCE_DIR}/CMake/version.h.in
               ${CMAKE_BINARY_DIR}/version.h)

install(FILES ${CMAKE_BINARY_DIR}/config.h ${CMAKE_BINARY_DIR}/version.h
        DESTINATION "include/${CMAKE_PROJECT_NAME}")

#------------------------------------------------------------------------------
if(BUILD_WITH_PYTHON)
  add_subdirectory(python)

  if(BUILD_TESTING)
    add_subdirectory(python/test)
  endif()
endif()

#------------------------------------------------------------------------------
# Documentation
add_subdirectory(doc)

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Allow packaging with "make package"
if(BUILD_APT_PACKAGES)
  add_subdirectory(package)
endif()
#------------------------------------------------------------------------------
