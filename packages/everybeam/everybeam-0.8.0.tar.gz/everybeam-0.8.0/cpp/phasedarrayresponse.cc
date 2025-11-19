// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "telescope/phasedarray.h"
#include "phasedarrayresponse.h"

#include <cassert>

namespace everybeam {

PhasedArrayResponse::PhasedArrayResponse(
    const telescope::PhasedArray& phased_array)
    : phased_array_(phased_array) {}

bool PhasedArrayResponse::CalculateBeamNormalisation(
    BeamMode beam_mode, double time, double frequency, size_t station_index,
    aocommon::MC2x2F& inverse_gain) const {
  const Options& options = phased_array_.GetOptions();
  const BeamNormalisationMode beam_normalisation_mode =
      options.beam_normalisation_mode;
  const BeamMode preapplied_beam_mode = phased_array_.GetPreappliedBeamMode();

  if (beam_normalisation_mode == BeamNormalisationMode::kNone) {
    return false;
  }

  const double subband_frequency = options.use_channel_frequency
                                       ? frequency
                                       : phased_array_.GetSubbandFrequency();

  // if the normalisation mode is kPreApplied, but no beam correction was pre
  // applied then there is nothing to do
  if (beam_normalisation_mode == BeamNormalisationMode::kPreApplied &&
      preapplied_beam_mode == BeamMode::kNone) {
    return false;
  }

  const std::span frequency_list(&frequency, 1);
  // If the normalisation mode is kPreApplied, or kPreAppliedOrFull and the
  // fallback to Full is not needed then the response for the diff_beam_centre_
  // with preapplied_beam_mode_ needs to be computed
  aocommon::MC2x2 result;
  if (beam_normalisation_mode == BeamNormalisationMode::kPreApplied ||
      (beam_normalisation_mode == BeamNormalisationMode::kPreAppliedOrFull &&
       preapplied_beam_mode != BeamMode::kNone)) {
    phased_array_.GetStation(station_index)
        .Response(&result, preapplied_beam_mode, time, frequency_list,
                  diff_beam_centre_, std::span(&subband_frequency, 1),
                  station0_, tile0_);
  } else {
    // in all other cases the response for the reference direction with
    // beam_mode is needed
    phased_array_.GetStation(station_index)
        .Response(&result, beam_mode, time, frequency_list, diff_beam_centre_,
                  std::span(&subband_frequency, 1), station0_, tile0_);
  }
  inverse_gain = aocommon::MC2x2F(result);

  switch (beam_normalisation_mode) {
    case BeamNormalisationMode::kFull:
    case BeamNormalisationMode::kPreApplied:
    case BeamNormalisationMode::kPreAppliedOrFull:
      if (!inverse_gain.Invert()) {
        inverse_gain = aocommon::MC2x2F::Zero();
      }
      break;
    case BeamNormalisationMode::kAmplitude: {
      const float norm_inverse_gain = Norm(inverse_gain);
      const float amplitude_inv =
          (norm_inverse_gain == 0.0) ? 0.0
                                     : 1.0 / std::sqrt(0.5 * norm_inverse_gain);
      inverse_gain = aocommon::MC2x2F(amplitude_inv, 0.0, 0.0, amplitude_inv);
      break;
    }
    case BeamNormalisationMode::kNone:
      throw std::runtime_error("Invalid beam normalisation mode here");
  }
  return true;
}

}  // namespace everybeam
