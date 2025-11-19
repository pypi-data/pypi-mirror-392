# Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

# directory for config.h
include_directories(${CMAKE_BINARY_DIR})

# build libhamaker.so
add_library(hamaker SHARED hamakerelementresponse.cc hamakercoeff.cc)
target_link_libraries(hamaker PUBLIC ${HDF5_CXX_LIBRARIES} everybeam-core)
string(TOLOWER ${CMAKE_PROJECT_NAME} projectname)
set_target_properties(hamaker PROPERTIES LIBRARY_OUTPUT_NAME
                                         "${projectname}-hamaker")
if(SKBUILD)
  set_target_properties(hamaker PROPERTIES INSTALL_RPATH "$ORIGIN")
endif()

# install libhamaker.so
install(
  TARGETS hamaker
  COMPONENT libraries
  EXPORT EveryBeamTargets
  DESTINATION ${INSTALL_LIBDIR})

# install coefficients
message("Install Hamaker coefficients in: ${EVERYBEAM_INSTALL_DATADIR}")
install(
  FILES "${CMAKE_SOURCE_DIR}/coeffs/HamakerHBACoeff.h5"
        "${CMAKE_SOURCE_DIR}/coeffs/HamakerLBACoeff.h5"
  COMPONENT data-files
  DESTINATION ${EVERYBEAM_INSTALL_DATADIR})
