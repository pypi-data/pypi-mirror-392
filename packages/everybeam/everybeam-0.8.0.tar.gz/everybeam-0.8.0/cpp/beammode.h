// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_BEAMMODE_H_
#define EVERYBEAM_BEAMMODE_H_

#include <string>

#include <boost/algorithm/string/case_conv.hpp>

namespace everybeam {

/**
 * Describes which beam is computed: array, element or both.
 * These may have different meanings for different telescopes. For LOFAR HBA,
 * the element beam is the dipole beam, and the array beam is the combination
 * of the tile factor and station-array factor.
 */
enum class BeamMode { kNone, kFull, kArrayFactor, kElement };

inline std::string ToString(BeamMode mode) {
  switch (mode) {
    case BeamMode::kNone:
      return "None";
    case BeamMode::kFull:
      return "Full";
    case BeamMode::kArrayFactor:
      return "ArrayFactor";
    case BeamMode::kElement:
      return "Element";
  }
  throw std::runtime_error("Invalid beam mode");
}

inline BeamMode ParseBeamMode(const std::string& str) {
  const std::string lower_str = boost::algorithm::to_lower_copy(str);
  if (lower_str == "none")
    return BeamMode::kNone;
  else if (lower_str == "full" || lower_str == "default")
    return BeamMode::kFull;
  else if (lower_str == "arrayfactor" || lower_str == "array_factor")
    return BeamMode::kArrayFactor;
  else if (lower_str == "element")
    return BeamMode::kElement;
  else
    throw std::runtime_error(
        "Invalid beam mode \'" + str +
        "\', options are: None, Default, Full, ArrayFactor or Element");
}

}  // namespace everybeam

#endif
