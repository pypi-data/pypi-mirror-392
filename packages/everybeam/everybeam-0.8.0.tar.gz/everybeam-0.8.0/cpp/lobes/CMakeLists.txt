# Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

#------------------------------------------------------------------------------
if(DOWNLOAD_LOBES)
  # Download the LOBES coefficient files if DOWNLOAD_LOBES=On.
  file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/coeffs/lobes)
  add_custom_target(
    download_lobes_coefficients
    COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_lobes_coeffs.sh
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/coeffs/lobes)

  #Execute downloading of LOBEs coefficients here
  add_dependencies(everybeam download_lobes_coefficients)
endif()

if(NOT DOWNLOAD_LOBES
   AND BUILD_TESTING
   AND NOT "$ENV{CI}")
  # Download only the LOBES coefficient files related to unit tests if
  # DOWNLOAD_LOBES=Off and BUILD_TESTING=On.
  # On CI, never (re)download coefficient files, since they're already in
  # the base docker images.
  file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/coeffs/lobes)
  add_custom_target(
    download_lobes_coefficients_testing
    COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_lobes_coeffs_testing.sh
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/coeffs/lobes)

  #Execute downloading of LOBEs coefficients here
  add_dependencies(everybeam download_lobes_coefficients_testing)
endif()

# install coefficients
message("Install LOBES coefficients in: ${EVERYBEAM_INSTALL_DATADIR}/lobes")
install(
  DIRECTORY "${CMAKE_BINARY_DIR}/coeffs/lobes"
  COMPONENT data-files
  DESTINATION ${EVERYBEAM_INSTALL_DATADIR}
  FILES_MATCHING
  PATTERN "LOBES_*")

#------------------------------------------------------------------------------
# TODO: can't we remove all this?
set(MISC_DIR ${CMAKE_SOURCE_DIR}/scripts/misc)

configure_file(${MISC_DIR}/F4far_new.py
               ${CMAKE_CURRENT_BINARY_DIR}/F4far_new.py COPYONLY)
configure_file(${MISC_DIR}/calc_modes_1deg_noback.py
               ${CMAKE_CURRENT_BINARY_DIR}/calc_modes_1deg_noback.py COPYONLY)
configure_file(${MISC_DIR}/hamaker_vs_lobes.py
               ${CMAKE_CURRENT_BINARY_DIR}/hamaker_vs_lobes.py COPYONLY)
configure_file(${MISC_DIR}/test_beam_model.py
               ${CMAKE_CURRENT_BINARY_DIR}/test_beam_model.py COPYONLY)
