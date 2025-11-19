# Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

# Ensure that the Boost unit test framework is available.
find_package(
  Boost
  COMPONENTS unit_test_framework
  REQUIRED)

# Set cache values if not specified
set(MOCK_MS
    LOFAR_HBA_MOCK
    LOFAR_LBA_MOCK
    AARTFAAC_LBA_MOCK
    AARTFAAC_6_LBA_MOCK
    GMRT_MOCK
    OSKAR_MOCK
    SCREEN_FITTING
    SKA_MID_MOCK
    VLA_MOCK
    ALMA_MOCK
    MWA_MOCK)
foreach(mock ${MOCK_MS})
  set(${mock}_MS
      ${DATA_DIR}/${mock}.ms
      CACHE PATH "")
endforeach()

set(MWA_COEFF_PATH
    ${DATA_DIR}/mwa_full_embedded_element_pattern.h5
    CACHE PATH "")
set(H5PARMATERM_MOCK_PATH
    ${DATA_DIR}/H5PARMATERM_MOCK.h5
    CACHE PATH "")
set(H5_SOLUTIONS_PATH
    ${DATA_DIR}/solutions.h5
    CACHE PATH "")
set(KL_SCREEN_PATH
    ${DATA_DIR}/kl_screen_0.fits
    CACHE PATH "")
set(LWA_MOCK_PATH
    ${DATA_DIR}/LWA_OVRO_MOCK.ms
    CACHE PATH "")
set(DISH_MOCK_PATH
    ${DATA_DIR}/DISH_MOCK.ms
    CACHE PATH "")
set(LWA_COEFF_PATH
    ${CMAKE_BINARY_DIR}/coeffs/lwa
    CACHE PATH "")
set(LOBES_COEFF_PATH
    ${CMAKE_BINARY_DIR}/coeffs/lobes
    CACHE PATH "")

#------------------------------------------------------------------------------
set(TEST_FILENAMES
    runtests.cc
    talma.cc
    tatermconfig.cc
    tcasautils.cc
    tdish.cc
    telementresponsefixeddirection.cc
    testcommon.cc
    tsphericalharmonicsresponse.cc
    tgmrt.cc
    tgriddedresponse.cc
    tload.cc
    tlofar_hba.cc
    tlofar_lba.cc
    tlofar_aartfaac.cc
    tlwa.cc
    tlwaelementresponse.cc
    tmwa.cc
    tmsreadutils.cc
    toskar.cc
    tphasedarray.cc
    tphasedarraypoint.cc
    tskamid.cc
    tstation.cc
    tstationnode.cc
    tvla.cc
    tvoltagepattern.cc
    tcache.cc
    tklfittingaterm.cc
    tfourierfittingaterm.cc
    tfourierfitter.cc
    tklfitter.cc
    th5parmaterm.cc)

# Add boost dynamic link flag for all test files.
# https://www.boost.org/doc/libs/1_66_0/libs/test/doc/html/boost_test/usage_variants.html
# Without this flag, linking is incorrect and boost performs duplicate delete()
# calls after running all tests, in the cleanup phase.
set_source_files_properties(${TEST_FILENAMES} PROPERTIES COMPILE_DEFINITIONS
                                                         "BOOST_TEST_DYN_LINK")

add_custom_target(
  download_mocks
  WORKING_DIRECTORY ${DATA_DIR}
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh lba.MS.tar.bz2
          LOFAR_LBA_MOCK.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh
          L258627-one-timestep.tar.bz2 LOFAR_HBA_MOCK.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh aartfaac.MS.tgz
          AARTFAAC_LBA_MOCK.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh
          AARTFAAC_6_LBA_MOCK.ms.tar.gz AARTFAAC_6_LBA_MOCK.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh GMRT_MOCK.tar.bz2
          GMRT_MOCK.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh
          OSKAR-single-timeslot.tar.bz2 OSKAR_MOCK.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh
          SKA_MID_SIM-1channel-1timestep.tar.bz2 SKA_MID_MOCK.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh MWA-single-timeslot.tar.bz2
          MWA_MOCK.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh small-vla-set.tar.bz2
          VLA_MOCK.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh screentest_ms.tar.gz
          SCREEN_FITTING.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh lwa-ovro.MS.tar.bz2
          LWA_OVRO_MOCK.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_ms.sh meerkat_test.tar.gz
          DISH_MOCK.ms
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_compressed_file.sh
          OVRO_LWA_FEKO_TEST.tar.gz OVRO_LWA_FEKO_TEST.h5
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_h5_solutions.sh
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_mwa_coeff.sh
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_h5parmaterm_mock.sh
  COMMAND ${CMAKE_SOURCE_DIR}/scripts/download_kl_fits_screen.sh)

add_custom_target(
  make_alma_mock
  DEPENDS download_mocks
  WORKING_DIRECTORY ${DATA_DIR}
  COMMAND cp -r ${VLA_MOCK_MS} ${ALMA_MOCK_MS}
  COMMAND taql
          "UPDATE ${ALMA_MOCK_MS}::OBSERVATION SET TELESCOPE_NAME=\\\"ALMA\\\""
  COMMAND taql "UPDATE ${ALMA_MOCK_MS}::ANTENNA SET DISH_DIAMETER=7")

add_custom_target(make_mocks DEPENDS download_mocks make_alma_mock)

add_test(NAME make_mocks COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR}
                                 --target make_mocks)
set_tests_properties(make_mocks PROPERTIES FIXTURES_SETUP mocks)

add_executable(unittests ${TEST_FILENAMES})
target_link_libraries(
  unittests
  everybeam
  ${Boost_LIBRARIES}
  schaapcommon
  xtensor
  xtl
  xtensor-fftw)

# Required to get the config.h header
target_include_directories(unittests PRIVATE ${CMAKE_BINARY_DIR})

# Add test for automatically (re)building unittests if needed.
add_test(NAME buildunittests COMMAND ${CMAKE_COMMAND} --build
                                     ${CMAKE_BINARY_DIR} --target unittests)
set_tests_properties(buildunittests PROPERTIES FIXTURES_SETUP unittests)

add_test(NAME unittests COMMAND unittests -f JUNIT -k unittests.xml
                                --catch_system_error=yes)
set_tests_properties(unittests PROPERTIES LABELS unit FIXTURES_REQUIRED
                                          "unittests;mocks")
