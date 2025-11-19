// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_BEAMFORMERLOFARHBA_H
#define EVERYBEAM_BEAMFORMERLOFARHBA_H

#include "beamformerlofar.h"

namespace everybeam {
/**
 * @brief Optimized implementation of the BeamFormer class for the LOFAR HBA
 * telescope in combination with Hamaker element response model.
 *
 */
class BeamFormerLofarHBA : public BeamFormerLofar {
 public:
  /**
   * @brief Construct a new BeamFormerLofarHBA object given a coordinate system.
   *
   * @param coordinate_system
   */
  BeamFormerLofarHBA(const StationCoordinateSystem& coordinate_system)
      : BeamFormerLofar(coordinate_system) {}

  /**
   * @brief Returns an (incomplete!) clone of the BeamFormerLofarHBA class
   * only the element_ is copied. This method is intended to be exclusively
   * used in Station::SetAntenna!
   *
   * @return std::shared_ptr<Antenna>
   */
  std::shared_ptr<Antenna> Clone() const final override;

  /**
   * @brief Set the (unique) Tile for the BeamFormerLofarHBA object.
   *
   * @param beamformer
   */
  void SetTile(BeamFormer::Ptr beamformer) { tile_ = beamformer; }

  /**
   * @brief Add tile position to the tile_positions_ array
   *
   * @param position
   */
  void AddTilePosition(const vector3r_t& position) {
    tile_positions_.push_back(position);
  }

  /**
   * @brief Mark whether tile is enabled by pushing back boolean array to
   * tile_enabled_ array
   *
   * @param enabled
   */
  void AddTileEnabled(const std::array<bool, 2> enabled) {
    tile_enabled_.push_back(enabled);
  }

 private:
  // Local Array factor override
  void LocalArrayFactor(aocommon::MC2x2Diag* result, double time,
                        const std::span<const double>& freq,
                        const vector3r_t& direction,
                        const Options& options) const final override;

  // HBA specific: Array Factor at tile level, weighting the elements
  void TileArrayFactor(std::complex<double>* result, double time,
                       const std::span<const double>& freqs,
                       const vector3r_t& direction,
                       const Options& options) const;

  // BeamFormerLofarHBA has only one unique tile, and ntiles
  // unique tile positions
  std::shared_ptr<BeamFormer> tile_;
  std::vector<vector3r_t> tile_positions_;

  // Is tile enabled?
  std::vector<std::array<bool, 2>> tile_enabled_;
};
}  // namespace everybeam
#endif
