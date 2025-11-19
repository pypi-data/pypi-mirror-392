// lwa.h: Base class for computing the response for the OVRO-LWA
// telescope.
//
// Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_TELESCOPE_LWA_H_
#define EVERYBEAM_TELESCOPE_LWA_H_

#include "phasedarray.h"

namespace everybeam::telescope {

// LWA telescope class
class [[gnu::visibility("default")]] Lwa final : public PhasedArray {
 public:
  /**
   * @brief Construct a new Lwa object
   *
   * @param ms MeasurementSet
   * @param options telescope options
   */
  Lwa(const casacore::MeasurementSet& ms, const Options& options);
};

}  // namespace everybeam::telescope

#endif  // EVERYBEAM_TELESCOPE_LWA_H_
