// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "beamformerlofarhba.h"
#include "common/mathutils.h"

namespace everybeam {

std::shared_ptr<Antenna> BeamFormerLofarHBA::Clone() const {
  auto beamformer_clone =
      std::make_shared<BeamFormerLofarHBA>(GetCoordinateSystem());

  // NOTE: this is an incomplete clone, only creating a deep-copy of the
  // element. In fact, it also hides an upcast from an ElementHamaker into
  // an Element object.
  // The sole and single purpose of Clone() is to be used in
  // Station::SetAntenna!
  beamformer_clone->SetElement(std::make_shared<Element>(*element_));
  return beamformer_clone;
}

void BeamFormerLofarHBA::LocalArrayFactor(aocommon::MC2x2Diag* result,
                                          double time,
                                          const std::span<const double>& freqs,
                                          const vector3r_t& direction,
                                          const Options& options) const {
  // Compute the array factor of the field

  FieldArrayFactor(result, time, freqs, direction, options, tile_positions_,
                   tile_enabled_);

  // Compute the array factor of a tile
  std::vector<std::complex<double>> array_factor_tile(freqs.size());
  TileArrayFactor(array_factor_tile.data(), time, freqs, direction, options);

  for (size_t f = 0; f < freqs.size(); ++f) {
    result[f] = result[f] * array_factor_tile[f];
  }
}

void BeamFormerLofarHBA::TileArrayFactor(std::complex<double>* result,
                                         [[maybe_unused]] double time,
                                         const std::span<const double>& freqs,
                                         const vector3r_t& direction,
                                         const Options& options) const {
  // Weighted subtraction of the directions, with weights given by corresponding
  // freqs. Purpose is to correctly handle the case in which options.freq0 !=
  // freq
  std::vector<vector3r_t> delta_directions(freqs.size());
  for (size_t f = 0; f < freqs.size(); ++f) {
    vector3r_t delta_direction =
        options.reference_freqs[f] * options.tile0 - freqs[f] * direction;
    delta_directions[f] = delta_direction;
  }
  // Get geometric response for the difference vector stored in "pointing"
  const aocommon::UVector<std::complex<double>> geometric_response =
      BeamFormer::ComputeGeometricResponse(element_positions_,
                                           delta_directions);

  const size_t kNElements = element_positions_.size();
  // Initialize and fill result
  std::fill_n(result, freqs.size(), 0.0);
  for (size_t f = 0; f < freqs.size(); ++f) {
    for (size_t e = 0; e < kNElements; ++e) {
      result[f] += geometric_response[e * freqs.size() + f];
    }

    // Normalize the result by the number of tiles
    const double weight = kNElements;

    result[f] /= weight;
  }
}
}  // namespace everybeam
