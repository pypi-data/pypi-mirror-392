// Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "oskar.h"

#include <cassert>

#include <aocommon/banddata.h>
#include <casacore/measures/TableMeasures/ArrayMeasColumn.h>

#include "../beamformeridenticalantennas.h"
#include "../common/mathutils.h"
#include "../common/casautils.h"

using casacore::MeasurementSet;
using everybeam::Station;
using everybeam::griddedresponse::GriddedResponse;
using everybeam::pointresponse::PointResponse;
using everybeam::telescope::OSKAR;

namespace everybeam::telescope {

namespace {
Options SetTelescopeOptions(const Options& options) {
  Options new_options = options;
  if (options.element_response_model == ElementResponseModel::kDefault) {
    new_options.element_response_model = ElementResponseModel::kOSKARDipole;
  }

  // OSKAR never uses the subband frequency.
  if (!options.use_channel_frequency) {
    throw std::runtime_error("For OSKAR, use_channel_frequency must be true.");
  }

  return new_options;
}

std::shared_ptr<BeamFormer> CreateBeamFormer(const StationNode& antenna_tree,
                                             std::size_t station_id) {
  constexpr StationCoordinateSystem::Axes kOskarAntennaOrientation =
      StationCoordinateSystem::kIdentityAxes;

  if (!antenna_tree.GetChildren().empty()) {
    throw std::invalid_argument("Create OSKAR stations: Station node " +
                                std::to_string(station_id) +
                                " should not have child nodes itself.");
  }

  const StationCoordinateSystem& coordinate_system =
      antenna_tree.GetCoordinateSystem();

  std::shared_ptr<BeamFormer> beam_former =
      std::make_shared<BeamFormerIdenticalAntennas>(coordinate_system);
  const std::size_t n_elements = antenna_tree.GetChildPositions().size();
  for (std::size_t i = 0; i < n_elements; ++i) {
    // Tranform antenna position to field coordinates.
    const vector3r_t field_position = {
        dot(antenna_tree.GetChildPositions()[i], coordinate_system.axes.p),
        dot(antenna_tree.GetChildPositions()[i], coordinate_system.axes.q),
        dot(antenna_tree.GetChildPositions()[i], coordinate_system.axes.r)};

    const StationCoordinateSystem antenna_coordinate_system(
        field_position, kOskarAntennaOrientation);
    beam_former->AddAntenna(std::make_shared<Element>(
        antenna_coordinate_system, station_id, antenna_tree.IsXEnabled(i),
        antenna_tree.IsYEnabled(i)));
  }

  return beam_former;
}

std::vector<std::unique_ptr<Station>> CreateStations(
    const StationNode& station_tree, const Options& options) {
  const Options oskar_options = SetTelescopeOptions(options);
  const std::size_t n_stations = station_tree.GetChildPositions().size();

  if (station_tree.GetChildren().size() != n_stations) {
    throw std::invalid_argument(
        "Create OSKAR stations: Top level station node should have child "
        "nodes.");
  }

  std::vector<std::unique_ptr<Station>> stations;
  stations.reserve(n_stations);
  for (std::size_t i = 0; i < n_stations; ++i) {
    const StationNode& antenna_tree = station_tree.GetChildren()[i];
    std::shared_ptr<BeamFormer> beam_former = CreateBeamFormer(antenna_tree, i);

    const std::string& station_name = antenna_tree.GetName().empty()
                                          ? "station" + std::to_string(i)
                                          : antenna_tree.GetName();
    auto station = std::make_unique<Station>(
        station_name, station_tree.GetChildPositions()[i], oskar_options);
    station->SetAntenna(std::move(beam_former));
    stations.push_back(std::move(station));
  }
  return stations;
}

}  // namespace

OSKAR::OSKAR(const MeasurementSet& ms, const Options& options)
    : PhasedArray(ms, SetTelescopeOptions(options)) {
  casacore::ScalarMeasColumn<casacore::MDirection> delay_dir_col(
      ms.field(),
      casacore::MSField::columnName(casacore::MSFieldEnums::DELAY_DIR));
  SetDelayDirection(delay_dir_col(0));
  // Tile beam direction has dummy values for OSKAR.
  SetTileBeamDirection(delay_dir_col(0));

  CalculatePreappliedBeamOptions(ms);
}

OSKAR::OSKAR(const StationNode& station_tree,
             casacore::MDirection delay_direction, const Options& options)
    : PhasedArray(CreateStations(station_tree, options),
                  SetTelescopeOptions(options)) {
  SetDelayDirection(delay_direction);
  // OSKAR has no tile and no preapplied beam direction (yet).
  // Use the delay direction as dummy value for these directions.
  SetTileBeamDirection(delay_direction);
  SetPreappliedBeamDirection(delay_direction);
}

}  // namespace everybeam::telescope
