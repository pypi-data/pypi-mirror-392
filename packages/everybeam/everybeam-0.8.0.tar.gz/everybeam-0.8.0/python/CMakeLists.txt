# Copyright (C) 2024 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

project(everybeam_pybind11)

if(CMAKE_VERSION VERSION_LESS "3.18")
  if(DEFINED ENV{CIBUILDWHEEL})
    # Build using `cibuildwheel`
    message(
      FATAL_ERROR
        "Package `cibuildwheel` requires CMake >= 3.18, but you have ${CMAKE_VERSION}."
    )
  endif()
  set(Python3_DEV_COMPONENT Development)
else()
  # When using cibuildwheel, the "Development" component is not available.
  # Therefore, only depend on "Development.Module" with CMake >= 3.18.
  set(Python3_DEV_COMPONENT Development.Module)
endif()

find_package(
  Python3
  COMPONENTS Interpreter ${Python3_DEV_COMPONENT}
  REQUIRED)

# Load pybind11 *after* finding Python, otherwise pybind11 may use a different
# Python version.
add_subdirectory(${CMAKE_SOURCE_DIR}/external/pybind11
                 ${CMAKE_BINARY_DIR}/external/pybind11)

# Create the binding library
# pyeverybeam is a temporary alias for everybeam target
pybind11_add_module(
  pyeverybeam
  wrappers/pyelementresponse.cc
  wrappers/pyload.cc
  wrappers/pylobes.cc
  wrappers/pystationnode.cc
  wrappers/pytelescope.cc
  wrappers/pyutils.cc
  wrappers/wrapper.cc)

target_include_directories(pyeverybeam
                           PUBLIC "$<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/cpp>")
target_include_directories(pyeverybeam SYSTEM PRIVATE ${pybind11_INCLUDE_DIRS})
# Build pyeverybeam without its dependencies on ReadTheDocs, since its only
# purpose is extracting documentation for the Python bindings.
if(NOT DEFINED ENV{READTHEDOCS})
  target_link_libraries(pyeverybeam PUBLIC everybeam)
endif()
set_target_properties(pyeverybeam PROPERTIES OUTPUT_NAME everybeam)
if(SKBUILD)
  set_target_properties(pyeverybeam PROPERTIES INSTALL_RPATH
                                               "$ORIGIN/${INSTALL_LIBDIR}")
endif()

# Define where the python module will be installed. When using scikit-build,
# it must be the current directory; otherwise, use site-packages directory.
if(NOT DEFINED Python3_LIBRARY_DIR)
  if(DEFINED SKBUILD)
    set(Python3_LIBRARY_DIR .)
  else()
    execute_process(
      COMMAND ${Python3_EXECUTABLE} -c
              "import site; print(site.getsitepackages()[0])"
      OUTPUT_VARIABLE Python3_DIST_PATH
      OUTPUT_STRIP_TRAILING_WHITESPACE)

    if(Python3_DIST_PATH
       MATCHES
       "\\/(lib.*\\/python${Python3_VERSION_MAJOR}\\.${Python3_VERSION_MINOR}\\/.*)"
    )
      set(Python3_LIBRARY_DIR ${CMAKE_MATCH_1})
    else()
      message(
        FATAL_ERROR "Failed to parse Python3_DIST_PATH='${Python3_DIST_PATH}'")
    endif()
  endif()
endif()

# Install pyeverybeam in site-packages directory
install(
  TARGETS pyeverybeam
  COMPONENT libraries
  LIBRARY DESTINATION ${Python3_LIBRARY_DIR})
