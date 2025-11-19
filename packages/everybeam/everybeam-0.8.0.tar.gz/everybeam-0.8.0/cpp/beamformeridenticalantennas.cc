// Copyright (C) 2022 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "beamformeridenticalantennas.h"

#include "common/constants.h"
#include "common/mathutils.h"

#include <cmath>

namespace everybeam {

std::shared_ptr<Antenna> BeamFormerIdenticalAntennas::Clone() const {
  auto beamformer_clone = std::make_shared<BeamFormerIdenticalAntennas>(
      GetCoordinateSystem(), GetPhaseReferencePosition());
  beamformer_clone->antennas_ = antennas_;
  return beamformer_clone;
}

void BeamFormerIdenticalAntennas::LocalResponse(
    aocommon::MC2x2* result, const ElementResponse& element_response,
    double time, const std::span<const double>& freqs,
    const vector3r_t& direction, const Options& options) const {
  const std::shared_ptr<Antenna>& antenna = antennas_[0];

  antenna->Response(result, element_response, time, freqs, direction, options);
  std::vector<aocommon::MC2x2Diag> array_factor(freqs.size());
  LocalArrayFactor(array_factor.data(), time, freqs, direction, options);

  for (size_t f = 0; f < freqs.size(); f++) {
    result[f] = array_factor[f] * result[f];
  }
}
}  // namespace everybeam
