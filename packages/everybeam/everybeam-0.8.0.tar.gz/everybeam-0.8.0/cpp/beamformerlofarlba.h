// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_BEAMFORMERLOFARLBA_H
#define EVERYBEAM_BEAMFORMERLOFARLBA_H

#include "beamformerlofar.h"

namespace everybeam {
/**
 * @brief Optimized implementation of the BeamFormer class for the LOFAR LBA
 * telescope in combination with Hamaker element response model.
 *
 */
class BeamFormerLofarLBA : public BeamFormerLofar {
 public:
  /**
   * @brief Construct a new BeamFormerLofarLBA object given a coordinate system.
   *
   * @param coordinate_system
   */
  BeamFormerLofarLBA(const StationCoordinateSystem& coordinate_system)
      : BeamFormerLofar(coordinate_system) {}

  /**
   * @brief Returns an (incomplete!) clone of the BeamFormerLofarLBA class
   * only the element_ is copied. This method is intended to be exclusively
   * used in Station::SetAntenna!
   *
   * @return std::shared_ptr<Antenna>
   */
  std::shared_ptr<Antenna> Clone() const final override;

  /**
   * @brief Mark whether the element is enabled by pushing back boolean array to
   * element_enabled_ array
   *
   * @param enabled
   */
  void AddElementEnabled(const std::array<bool, 2> enabled) {
    element_enabled_.push_back(enabled);
  }

 private:
  // Local Array factor override
  void LocalArrayFactor(aocommon::MC2x2Diag* result, double time,
                        const std::span<const double>& freqs,
                        const vector3r_t& direction,
                        const Options& options) const final override;

  // Is element enabled?
  std::vector<std::array<bool, 2>> element_enabled_;
};
}  // namespace everybeam
#endif
