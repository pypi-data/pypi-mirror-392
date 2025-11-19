// oskar.h: Base class for computing the response for the OSKAR
// telescope.
//
// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_TELESCOPE_OSKAR_H_
#define EVERYBEAM_TELESCOPE_OSKAR_H_

#include <memory>

#include <casacore/measures/Measures/MPosition.h>
#include <casacore/measures/Measures/MDirection.h>
#include <casacore/measures/Measures/MEpoch.h>

#include "phasedarray.h"
#include "../stationnode.h"

namespace everybeam {
namespace telescope {

//! OSKAR telescope class
class [[gnu::visibility("default")]] OSKAR final : public PhasedArray {
 public:
  /**
   * @brief Construct an OSKAR object from a Measurement Set.
   *
   * @param ms MeasurementSet, containing frequency data, delay direction and
   *           pre-applied beam options.
   * @param options Telescope options.
   */
  OSKAR(const casacore::MeasurementSet& ms, const Options& options);

  /**
   * @brief Constructs an OSKAR object with the specified meta-data.
   *
   * @param station_tree Station tree with positions. See StationNode class.
   * @param delay_direction Direction used for delay calculations.
   * @param options Telescope configuration options. See Options struct.
   */
  OSKAR(const StationNode& station_tree, casacore::MDirection delay_direction,
        const Options& options);

  //! Get the tile beam direction, equal to delay direction for OSKAR!
  casacore::MDirection GetTileBeamDirection() const override {
    std::cout << "OSKAR has no tile. tile_beam_dir is equal to the delay_dir."
              << std::endl;
    return PhasedArray::GetTileBeamDirection();
  };

  //! Get the preapplied beam direction, equal to delay direction for OSKAR!
  casacore::MDirection GetPreappliedBeamDirection() const override {
    std::cout << "OSKAR has no preapplied beam direction (yet). "
                 "preapplied_beam_dir is equal to the delay_dir."
              << std::endl;
    return PhasedArray::GetPreappliedBeamDirection();
  };
};
}  // namespace telescope
}  // namespace everybeam

#endif  // EVERYBEAM_TELESCOPE_OSKAR_H_
