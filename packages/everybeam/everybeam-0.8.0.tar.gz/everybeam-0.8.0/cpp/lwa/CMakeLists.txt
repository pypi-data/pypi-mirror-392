# Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

if(DOWNLOAD_LWA OR BUILD_TESTING)
  # Download the LWA coefficient files if DOWNLOAD_LWA=On, leads to
  # a small amount of overhead in make command, even if the coefficient
  # files have been dowloaded. Because the unit tests require
  # DOWNLOAD_LWA, this is also enabled when BUILD_TESTING is on.
  file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/coeffs/lwa)
  add_custom_target(
    download_lwa_coefficients
    COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_lwa_coeffs.sh
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/coeffs/lwa)

  # Execute the download script before building the everybeam library.
  add_dependencies(everybeam download_lwa_coefficients)

  # install coefficients
  message("Install LWA coefficients in: ${EVERYBEAM_INSTALL_DATADIR}/lwa")
  install(FILES "${CMAKE_BINARY_DIR}/coeffs/lwa/LWA_OVRO.h5"
          DESTINATION "${EVERYBEAM_INSTALL_DATADIR}/lwa")

endif()
