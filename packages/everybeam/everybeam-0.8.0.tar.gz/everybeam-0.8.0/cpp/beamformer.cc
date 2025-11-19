// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "beamformer.h"

#include "common/constants.h"
#include "common/mathutils.h"

#include <cmath>
#include <cassert>
namespace everybeam {

std::shared_ptr<Antenna> BeamFormer::Clone() const {
  auto beamformer_clone = std::make_shared<BeamFormer>(
      GetCoordinateSystem(), GetPhaseReferencePosition());

  // antennas_ is a vector of pointers to Antennas, so
  // this creates a shallow copy, in the sense that
  // the antennas are not copied, only the pointers.
  beamformer_clone->antennas_ = antennas_;
  beamformer_clone->delta_phase_reference_positions_ =
      delta_phase_reference_positions_;
  return beamformer_clone;
}

std::shared_ptr<Antenna> BeamFormer::ExtractAntenna(
    size_t antenna_index) const {
  std::shared_ptr<Antenna> antenna = antennas_[antenna_index]->Clone();
  antenna->Transform(GetCoordinateSystem());
  return antenna;
}

vector3r_t BeamFormer::TransformToLocalPosition(const vector3r_t& position) {
  // Get antenna position relative to coordinate system origin
  const vector3r_t dposition{position[0] - GetCoordinateSystem().origin[0],
                             position[1] - GetCoordinateSystem().origin[1],
                             position[2] - GetCoordinateSystem().origin[2]};
  // Return inner product on orthogonal unit vectors of coordinate system
  return {
      dot(GetCoordinateSystem().axes.p, dposition),
      dot(GetCoordinateSystem().axes.q, dposition),
      dot(GetCoordinateSystem().axes.r, dposition),
  };
}

void BeamFormer::ComputeWeightedResponses(
    aocommon::MC2x2Diag* result,
    const std::span<const vector3r_t>& pointings) const {
  // Get geometric response for pointing direction
  aocommon::UVector<std::complex<double>> geometric_response =
      ComputeGeometricResponse(delta_phase_reference_positions_, pointings);

  // Initialize and fill result

  std::array<double, 2> weight_sum = {0.0, 0.0};
  for (size_t idx = 0; idx < antennas_.size(); ++idx) {
    // Compute the weights
    weight_sum[0] += antennas_[idx]->IsEnabled(0);
    weight_sum[1] += antennas_[idx]->IsEnabled(1);
  }

  for (size_t p = 0; p < pointings.size(); ++p) {
    for (size_t idx = 0; idx < antennas_.size(); ++idx) {
      // Get geometric response at index
      const std::complex<double> phasor =
          geometric_response[idx * pointings.size() + p];
      // Compute the delays in x/y direction
      result[idx * pointings.size() + p] = {
          phasor * (1.0 * antennas_[idx]->IsEnabled(0)),
          phasor * (1.0 * antennas_[idx]->IsEnabled(1))};
      // Normalize the weight by the number of antennas
      result[idx * pointings.size() + p] = {
          result[idx * pointings.size() + p].Get(0) / weight_sum[0],
          result[idx * pointings.size() + p].Get(1) / weight_sum[1]};
    }
  }
}

void BeamFormer::LocalResponse(aocommon::MC2x2* result,
                               const ElementResponse& element_response,
                               double time,
                               const std::span<const double>& freqs,
                               const vector3r_t& direction,
                               const Options& options) const {
  // Weighted subtraction of the pointing direction (0-direction), and the
  // direction of interest. Weights are given by corresponding freqs.
  std::vector<vector3r_t> delta_directions(freqs.size());
  for (size_t i = 0; i < freqs.size(); i++) {
    const vector3r_t delta_direction =
        options.reference_freqs[i] * options.station0 - freqs[i] * direction;
    delta_directions[i] = delta_direction;
  }

  // Weights based on (weighted) difference vector between
  // pointing direction and direction of interest of beam
  std::vector<aocommon::MC2x2Diag> weights(freqs.size() * antennas_.size());
  ComputeWeightedResponses(weights.data(), delta_directions);

  // Copy options into local_options. Needed to propagate
  // the potential change in the rotate boolean downstream.
  Options local_options = options;

  // If fixate_direction_ is true, compute and cache quantities related to the
  // field. This is done for LOBEs beamformers in which all elements inside the
  // beamformer have the same basisfunction for a given direction.
  std::shared_ptr<ElementResponse> local_element_response;
  if (fixate_direction_) {
    local_element_response = element_response.FixateDirection(direction);
    local_options.rotate = false;
  }

  std::fill_n(result, freqs.size(), aocommon::MC2x2(0.0, 0.0, 0.0, 0.0));

  std::vector<aocommon::MC2x2> antenna_response(freqs.size());
  for (size_t idx = 0; idx < antennas_.size(); ++idx) {
    antennas_[idx]->Response(
        antenna_response.data(),
        local_element_response ? *local_element_response : element_response,
        time, freqs, direction, local_options);
    for (size_t f = 0; f < freqs.size(); f++) {
      result[f] += weights[idx * freqs.size() + f] * antenna_response[f];
    }
  }

  // If the Jones matrix needs to be rotated from theta, phi directions
  // to north, east directions, but this has not been done yet, do it here
  if (options.rotate && !local_options.rotate) {
    // cross with unit upward pointing vector {0.0, 0.0, 1.0}
    for (size_t f = 0; f < freqs.size(); f++) {
      const vector3r_t e_phi = normalize(cross(direction));
      const vector3r_t e_theta = cross(e_phi, direction);
      result[f] *= {dot(e_theta, options.north), dot(e_theta, options.east),
                    dot(e_phi, options.north), dot(e_phi, options.east)};
    }
  }
}

void BeamFormer::LocalArrayFactor(aocommon::MC2x2Diag* result, double time,
                                  const std::span<const double>& freqs,
                                  const vector3r_t& direction,
                                  const Options& options) const {
  // Weighted subtraction of the pointing direction (0-direction), and the
  // direction of interest (direction). Weights are given by corresponding
  // freqs.
  std::vector<vector3r_t> delta_directions(freqs.size());
  for (size_t i = 0; i < freqs.size(); i++) {
    const vector3r_t delta_direction =
        options.reference_freqs[i] * options.station0 - freqs[i] * direction;
    delta_directions[i] = delta_direction;
  }
  // Weights based on (weighted) difference vector between
  // pointing direction and direction of interest of beam
  std::vector<aocommon::MC2x2Diag> weights(freqs.size() * antennas_.size());
  ComputeWeightedResponses(weights.data(), delta_directions);
  std::fill_n(result, freqs.size(), aocommon::MC2x2Diag(0.0, 0.0));
  std::vector<aocommon::MC2x2Diag> antenna_array_factor(freqs.size());
  for (size_t idx = 0; idx < antennas_.size(); ++idx) {
    antennas_[idx]->ArrayFactor(antenna_array_factor.data(), time, freqs,
                                direction, options);
    for (size_t f = 0; f < freqs.size(); f++) {
      result[f] += weights[idx * freqs.size() + f] * antenna_array_factor[f];
    }
  }
}

}  // namespace everybeam
