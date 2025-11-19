# Copyright (C) 2024 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

project(everybeam_cpp)

#------------------------------------------------------------------------------
add_library(everybeam-core SHARED elementresponse.cc options.cc)
target_include_directories(everybeam-core PRIVATE "${CMAKE_BINARY_DIR}")

add_library(
  everybeam SHARED
  antenna.cc
  beamformer.cc
  beamformer_fastmath.cc
  beamformeridenticalantennas.cc
  beamformerlofar.cc
  beamformerlofarhba.cc
  beamformerlofarlba.cc
  circularsymmetric/atcacoefficients.cc
  circularsymmetric/gmrtcoefficients.cc
  circularsymmetric/meerkatcoefficients.cc
  circularsymmetric/vlacoefficients.cc
  circularsymmetric/voltagepattern.cc
  common/sphericalharmonics.cc
  common/fftresampler.cc
  coords/itrfconverter.cc
  coords/itrfdirection.cc
  element.cc
  elementhamaker.cc
  elementresponse.cc
  elementresponsefactory.cc
  everybeam.cc
  griddedresponse/aartfaacgrid.cc
  griddedresponse/griddedresponse.cc
  griddedresponse/dishgrid.cc
  griddedresponse/mwagrid.cc
  # Phased array telescopes (SKA, LOFAR)
  griddedresponse/phasedarraygrid.cc
  griddedresponse/skamidgrid.cc
  load.cc
  lobes/lobeselementresponse.cc
  oskar/skalowelementresponse.cc
  lwa/lwaelementresponse.cc
  msreadutils.cc
  # MWA(beam) related
  mwabeam/tilebeam2016.cc
  mwabeam/beam2016implementation.cc
  options.cc
  phasedarrayresponse.cc
  pointresponse/phasedarraypoint.cc
  pointresponse/dishpoint.cc
  pointresponse/mwapoint.cc
  pointresponse/skamidpoint.cc
  sphericalharmonicsresponse.cc
  sphericalharmonicsresponsefixeddirection.cc
  station.cc
  telescope/alma.cc
  telescope/lofar.cc
  telescope/dish.cc
  telescope/dsa110.cc
  telescope/lofar.cc
  telescope/lwa.cc
  telescope/mwa.cc
  telescope/phasedarray.cc
  telescope/oskar.cc
  telescope/skamid.cc
  griddedresponse/aartfaacgrid.cc
  griddedresponse/airygrid.cc
  griddedresponse/dishgrid.cc
  griddedresponse/griddedresponse.cc
  griddedresponse/mwagrid.cc
  griddedresponse/skamidgrid.cc
  pointresponse/airypoint.cc
  pointresponse/dishpoint.cc
  pointresponse/mwapoint.cc
  pointresponse/phasedarraypoint.cc
  pointresponse/skamidpoint.cc
  circularsymmetric/atcacoefficients.cc
  circularsymmetric/gmrtcoefficients.cc
  circularsymmetric/meerkatcoefficients.cc
  circularsymmetric/vlacoefficients.cc
  circularsymmetric/voltagepattern.cc
  # Phased array telescopes (SKA, LOFAR)
  griddedresponse/phasedarraygrid.cc
  # MWA(beam) related
  mwabeam/tilebeam2016.cc
  mwabeam/beam2016implementation.cc)

set_source_files_properties(beamformer_fastmath.cc
                            PROPERTIES COMPILE_FLAGS "-fopenmp -ffast-math")

# Make sure that when other targets within this project link against the everybeam target,
# they can find the include files.
target_include_directories(
  everybeam PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>)
# Required to get config.h header
target_include_directories(everybeam PRIVATE "${CMAKE_BINARY_DIR}")

target_include_directories(everybeam PUBLIC ${CASACORE_INCLUDE_DIR})

target_link_libraries(everybeam PRIVATE aterms)
target_link_libraries(everybeam PUBLIC hamaker oskar skamidbeam)
target_link_libraries(
  everybeam PUBLIC ${CASACORE_LIBRARIES} ${HDF5_CXX_LIBRARIES}
                   ${FFTW3F_LIBRARY} ${CFITSIO_LIBRARY})
target_link_libraries(everybeam PRIVATE schaapcommon Threads::Threads
                                        Boost::date_time xtensor)

if(SKBUILD)
  set_target_properties(everybeam PROPERTIES INSTALL_RPATH "$ORIGIN")
endif()

install(
  TARGETS everybeam everybeam-core
  COMPONENT libraries
  EXPORT EveryBeamTargets
  DESTINATION ${INSTALL_LIBDIR})

install(
  FILES antenna.h
        beamformer.h
        beamformeridenticalantennas.h
        beammode.h
        beamnormalisationmode.h
        element.h
        elementhamaker.h
        elementresponse.h
        everybeam.h
        msreadutils.h
        station.h
        stationnode.h
        load.h
        options.h
        phasedarrayresponse.h
        telescope.h
  DESTINATION "include/${CMAKE_PROJECT_NAME}")

# Install EveryBeamTargets.cmake, which contains the EveryBeam cmake targets.
# Other install() calls generate the contents for EveryBeamTargets.cmake.
# EveryBeamConfig.cmake includes the generated EveryBeamTargets.cmake.
install(
  EXPORT EveryBeamTargets
  NAMESPACE EveryBeam::
  DESTINATION "lib/${projectname}")

# Set-up cmake configuration files
configure_file("${CMAKE_SOURCE_DIR}/CMake/EveryBeamConfig.cmake.in"
               "${CMAKE_BINARY_DIR}/CMakeFiles/EveryBeamConfig.cmake" @ONLY)
configure_file(
  "${CMAKE_SOURCE_DIR}/CMake/EveryBeamConfigVersion.cmake.in"
  "${CMAKE_BINARY_DIR}/CMakeFiles/EveryBeamConfigVersion.cmake" @ONLY)

install(FILES "${CMAKE_BINARY_DIR}/CMakeFiles/EveryBeamConfig.cmake"
              "${CMAKE_BINARY_DIR}/CMakeFiles/EveryBeamConfigVersion.cmake"
        DESTINATION "lib/${projectname}")

add_subdirectory(aterms)
add_subdirectory(circularsymmetric)
add_subdirectory(common)
add_subdirectory(coords)
add_subdirectory(griddedresponse)
add_subdirectory(hamaker)
add_subdirectory(lobes)
add_subdirectory(lwa)
add_subdirectory(oskar)
add_subdirectory(pointresponse)
add_subdirectory(skamidbeam)
add_subdirectory(telescope)
