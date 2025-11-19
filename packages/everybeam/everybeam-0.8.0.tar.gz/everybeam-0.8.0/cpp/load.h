// load.h: Main interface for loading a telescope
//
// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_LOAD_H_
#define EVERYBEAM_LOAD_H_

#include <array>
#include <vector>

#include <casacore/ms/MeasurementSets/MeasurementSet.h>

#include "telescope/telescope.h"
#include "beammode.h"
#include "options.h"
#include "elementresponse.h"
#include "stationnode.h"

namespace everybeam {
/**
 * @brief Available TelescopeType enums
 *
 */
enum TelescopeType {
  kUnknownTelescope,
  kAARTFAAC,
  kATCATelescope,
  kALMATelescope,
  kDsa110Telescope,
  kGMRTTelescope,
  kLofarTelescope,
  kMeerKATTelescope,
  kOSKARTelescope,
  kMWATelescope,
  kSkaMidTelescope,
  kVLATelescope,
  kOvroLwaTelescope,
};

/**
 * @brief Derive the TelescopeType from a given MS
 *
 * @param ms
 * @return TelescopeType
 */
[[gnu::visibility("default")]] TelescopeType GetTelescopeType(
    const casacore::MeasurementSet& ms);

/**
 * @brief Load telescope given a measurement set. Telescope is determined
 * from MeasurementSet meta-data.
 *
 * @param ms MeasurementSet
 * @param options Options
 * @return Unique pointer to Telescope object
 */
[[gnu::visibility("default")]] std::unique_ptr<telescope::Telescope> Load(
    const casacore::MeasurementSet& ms, const Options& options);

/**
 * @brief Load telescope given a path to a measurement set. Telescope is
 * determined from MeasurementSet meta-data.
 *
 * @param ms MeasurementSet
 * @param options Options
 * @return Unique pointer to Telescope object
 */
[[gnu::visibility("default")]] std::unique_ptr<telescope::Telescope> Load(
    const std::string& ms_name, const Options& options);

/**
 * @brief Creates a telescope from the specified metadata.
 *
 * This function has arguments for all telescope types. Most telescopes do not
 * use all arguments. The function will throw an invalid_argument exception if
 * any of the required arguments are missing or invalid.
 *
 * @param options Configuration options for the telescope.
 *        The element_response_model element of this Options object determines
 *        the telescope type. It may thus not be ElementResponseModel::kDefault.
 * @param station_tree Station tree which recursively specificies the coordinate
 *        system and position of each station and its child elements. The tree
 *        structure should be appropriate for the requested telescope type.
 * @param delay_directions Vector with ra, dec coordinates, specifying the
 *        delay direction for each field. EveryBeam uses the J2000 reference
 *        frame. If there is only one field (e.g. for LOFAR), give a list of
 *        length one here.
 * @param tile_beam_direction An array with ra, dec coordinates, specifying the
 *        tile beam pointing direction. EveryBeam uses the J2000 reference
 *        frame.
 * @param preapplied_beam_direction An array with ra, dec coordinates,
 *        specifying the preapplied beam pointing direction. EveryBeam uses the
 *        J2000 reference frame. Only used for phased array telescopes.
 * @param preapplied_beam_mode Defines the beam corrections that have been
 *        applied to the preapplied beam. Only used for phased array telescopes.
 * @param dish_diameters Vector with dish diameters (in meters) for each
 *        station. Only used for dish-based telescopes.
 * @param reference_frequency Reference frequency used for beamforming (Hz).
          When use_channel_frequency is true, this value is ignored.
 * @param mwa_delay_factors Delay factors for the 16 elements of an MWA tile, in
 *        multiples of 435 ps. Only used for MWA telescopes.
 * @return A unique pointer to the created telescope instance.
 * @throw std::runtime_error If creating a telescope for the given
 *        element response model is not supported.
 * @throw std::invalid_argument If one of the arguments does not meet the
 *        telescope requirements. For example, if the station tree shape is
 *        inappropriate.
 */
[[gnu::visibility("default")]] std::unique_ptr<telescope::Telescope>
CreateTelescope(const Options& options, const StationNode& station_tree,
                const std::vector<std::array<double, 2>>& delay_directions = {},
                const std::array<double, 2>& tile_beam_direction = {0.0, 0.0},
                const std::array<double, 2>& preapplied_beam_direction = {0.0,
                                                                          0.0},
                BeamMode preapplied_beam_mode = BeamMode::kNone,
                const std::vector<double>& dish_diameters = {},
                double reference_frequency = 0.0,
                const std::vector<int>& mwa_delay_factors = {});

}  // namespace everybeam

#endif  // EVERYBEAM_LOAD_H_
