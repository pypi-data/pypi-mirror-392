// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "beamformerlofarlba.h"

namespace everybeam {

std::shared_ptr<Antenna> BeamFormerLofarLBA::Clone() const {
  auto beamformer_clone =
      std::make_shared<BeamFormerLofarLBA>(GetCoordinateSystem());

  // NOTE: this is an incomplete clone, only creating a deep-copy of the
  // element. In fact, it also hides an upcast from an ElementHamaker into
  // an Element object.
  // The sole and single purpose of Clone() is to be used in
  // Station::SetAntenna!
  beamformer_clone->SetElement(std::make_shared<Element>(*element_));
  return beamformer_clone;
}

void BeamFormerLofarLBA::LocalArrayFactor(aocommon::MC2x2Diag* result,
                                          double time,
                                          const std::span<const double>& freqs,
                                          const vector3r_t& direction,
                                          const Options& options) const {
  // Compute the array factor of the field
  FieldArrayFactor(result, time, freqs, direction, options, element_positions_,
                   element_enabled_);
}
}  // namespace everybeam
