# Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

#------------------------------------------------------------------------------
# directory for config.h
include_directories(${CMAKE_BINARY_DIR})

#------------------------------------------------------------------------------
# build libeverybeam-oskar.so
add_library(oskar SHARED oskarelementresponse.cc oskardatafile.cc
                         oskardataset.cc)

string(TOLOWER ${CMAKE_PROJECT_NAME} projectname)
set_target_properties(oskar PROPERTIES LIBRARY_OUTPUT_NAME
                                       "${projectname}-oskar")
if(SKBUILD)
  set_target_properties(oskar PROPERTIES INSTALL_RPATH "$ORIGIN")
endif()
# Make sure that when other targets within this project link against the oskar target,
# they can find the include files.
target_include_directories(
  oskar PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>)

#------------------------------------------------------------------------------
# Link against HDF5 and OpenMP
target_link_libraries(oskar PUBLIC ${HDF5_LIBRARIES} ${HDF5_CXX_LIBRARIES}
                                   ${OpenMP_CXX_FLAGS} everybeam-core)

# Link against ska-sdp-func. Disable compiler warnings using 'SYSTEM'.
get_target_property(ska_sdp_func_include_dirs ska_sdp_func
                    INTERFACE_INCLUDE_DIRECTORIES)
target_include_directories(oskar SYSTEM PRIVATE ${ska_sdp_func_include_dirs})
target_link_libraries(oskar PRIVATE ska_sdp_func)

#------------------------------------------------------------------------------
# install libeverybeam-oskar.so
install(
  TARGETS oskar
  COMPONENT libraries
  EXPORT EveryBeamTargets
  DESTINATION ${INSTALL_LIBDIR})

#install oskar coefficients
install(
  FILES "${CMAKE_SOURCE_DIR}/coeffs/oskar.h5"
  COMPONENT data-files
  DESTINATION ${EVERYBEAM_INSTALL_DATADIR})
