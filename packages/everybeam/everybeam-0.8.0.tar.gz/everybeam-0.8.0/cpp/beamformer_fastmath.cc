// Copyright (C) 2024 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

// This file contains functions that can be safely compiled
// "-ffast-math", e.g., which do not need handling of NaNs. In this
// mode GCC will vectorise functions using its built-in libmvec.
#include "beamformer.h"

#include "common/constants.h"
#include "common/mathutils.h"

namespace everybeam {

aocommon::UVector<std::complex<double>> BeamFormer::ComputeGeometricResponse(
    const std::span<const vector3r_t>& phase_reference_positions,
    const std::span<const vector3r_t>& directions) {
  constexpr double two_pi_over_c = -2.0 * M_PI / common::c;

  const size_t n_references = phase_reference_positions.size();
  const size_t n_directions = directions.size();
  // Allocate and fill result vector by looping over antennas
  aocommon::UVector<std::complex<double>> result(n_references * n_directions);
  aocommon::UVector<double> dl(n_references * n_directions);
  aocommon::UVector<double> sin_phase(n_references * n_directions);
  aocommon::UVector<double> cos_phase(n_references * n_directions);

  for (size_t f = 0; f < directions.size(); f++) {
    for (size_t i = 0; i < phase_reference_positions.size(); ++i) {
      dl[i * n_directions + f] =
          two_pi_over_c * dot(directions[f], phase_reference_positions[i]);
    }
  }

// Note that sincos() does not vectorize yet, and
// separate sin() cos() is merged to sincos() by the compiler.
// Hence split the loop into separate sin(), cos() loops.
#pragma omp simd
  for (size_t i = 0; i < n_references * n_directions; ++i) {
    cos_phase[i] = std::cos(dl[i]);
  }
#pragma omp simd
  for (size_t i = 0; i < n_references * n_directions; ++i) {
    sin_phase[i] = std::sin(dl[i]);
  }

#pragma omp simd
  for (size_t i = 0; i < n_references * n_directions; ++i) {
    result[i] = {cos_phase[i], sin_phase[i]};
  }

  return result;
}

}  // namespace everybeam
