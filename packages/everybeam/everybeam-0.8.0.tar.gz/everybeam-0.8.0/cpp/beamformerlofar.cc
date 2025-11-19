// Copyright (C) 2022 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "beamformerlofar.h"
#include "beamformer.h"

#include "common/constants.h"
#include "common/mathutils.h"

#include <cmath>
#include <cassert>

namespace everybeam {
void BeamFormerLofar::FieldArrayFactor(
    aocommon::MC2x2Diag* result, [[maybe_unused]] double time,
    const std::span<const double>& freqs, const vector3r_t& direction,
    const Options& options, const std::vector<vector3r_t>& antenna_positions,
    const std::vector<std::array<bool, 2>>& antenna_enabled) const {
  assert(antenna_positions.size() == antenna_enabled.size());
  // Weighted subtraction of the directions, with weights given
  // by corresponding freqs. Purpose is to correctly handle the
  // case in which options.freq0 != freq
  std::vector<vector3r_t> delta_directions(freqs.size());
  for (size_t f = 0; f < freqs.size(); ++f) {
    const vector3r_t delta_direction =
        options.reference_freqs[f] * options.station0 - freqs[f] * direction;
    delta_directions[f] = delta_direction;
  }
  // Get geometric response for pointing direction
  aocommon::UVector<std::complex<double>> geometric_response =
      BeamFormer::ComputeGeometricResponse(antenna_positions, delta_directions);

  std::vector<std::complex<double>> response_sum_xx(freqs.size());
  std::vector<std::complex<double>> response_sum_yy(freqs.size());

  std::array<double, 2> weight_sum = {0.0, 0.0};

  for (size_t idx = 0; idx < antenna_positions.size(); ++idx) {
    for (size_t f = 0; f < freqs.size(); ++f) {
      response_sum_xx[f] += geometric_response[idx * freqs.size() + f] *
                            (1.0 * antenna_enabled[idx][0]);
      response_sum_yy[f] += geometric_response[idx * freqs.size() + f] *
                            (1.0 * antenna_enabled[idx][1]);
    }
    weight_sum[0] += (1.0 * antenna_enabled[idx][0]);
    weight_sum[1] += (1.0 * antenna_enabled[idx][1]);
  }

  // Normalize the weight by the number of enabled tiles
  for (size_t f = 0; f < freqs.size(); ++f) {
    result[f] = aocommon::MC2x2Diag(response_sum_xx[f] / weight_sum[0],
                                    response_sum_yy[f] / weight_sum[1]);
  }
}

void BeamFormerLofar::LocalResponse(aocommon::MC2x2* result,
                                    const ElementResponse& element_response,
                                    double time,
                                    const std::span<const double>& freqs,
                                    const vector3r_t& direction,
                                    const Options& options) const {
  // Compute the combined array factor
  std::vector<aocommon::MC2x2Diag> array_factor(freqs.size());
  LocalArrayFactor(array_factor.data(), time, freqs, direction, options);

  // NOTE: there are maybe some redundant transformations in element-> response
  element_->Response(result, element_response, time, freqs, direction, options);
  for (size_t f = 0; f < freqs.size(); f++) {
    result[f] = array_factor[f] * result[f];
  }
}

}  // namespace everybeam
