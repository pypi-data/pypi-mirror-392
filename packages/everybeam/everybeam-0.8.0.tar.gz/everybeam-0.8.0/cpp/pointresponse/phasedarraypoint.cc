// Copyright (C) 2021 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "phasedarraypoint.h"
#include "../telescope/phasedarray.h"
#include "../common/types.h"

#include "./../coords/itrfdirection.h"
#include "./../coords/itrfconverter.h"

#include <limits>
namespace everybeam {

using telescope::PhasedArray;

namespace pointresponse {

PhasedArrayPoint::PhasedArrayPoint(const PhasedArray& phased_array, double time)
    : PointResponse(&phased_array, time),
      PhasedArrayResponse(phased_array),
      ra_(std::numeric_limits<double>::min()),
      dec_(std::numeric_limits<double>::min()),
      has_partial_itrf_update_(false),
      is_local_(false),
      rotate_(true) {}

void PhasedArrayPoint::Response(BeamMode beam_mode,
                                aocommon::MC2x2F* response_matrices, double ra,
                                double dec, std::span<const double> freqs,
                                size_t station_idx,
                                [[maybe_unused]] size_t field_id) {
  // Only compute ITRF directions if values differ from cached values
  if (HasTimeUpdate() || has_partial_itrf_update_ ||
      std::abs(ra - ra_) > 1e-10 || std::abs(dec - dec_) > 1e-10) {
    UpdateITRFVectors(ra, dec);
    ClearTimeUpdate();
    has_partial_itrf_update_ = false;
  }

  std::vector<aocommon::MC2x2> gain_matrix(freqs.size());
  UnnormalisedResponse(gain_matrix.data(), beam_mode, station_idx, freqs,
                       itrf_direction_, station0_, tile0_);

  for (size_t f = 0; f < freqs.size(); ++f) {
    aocommon::MC2x2F inverse_central_gain;

    const bool apply_normalisation = CalculateBeamNormalisation(
        beam_mode, GetTime(), freqs[f], station_idx, inverse_central_gain);

    if (apply_normalisation) {
      response_matrices[f] =
          inverse_central_gain * aocommon::MC2x2F(gain_matrix[f]);
    } else {
      response_matrices[f] = aocommon::MC2x2F(gain_matrix[f]);
    }
  }
}

void PhasedArrayPoint::Response(BeamMode beam_mode,
                                std::complex<float>* response_matrix, double ra,
                                double dec, double freq, size_t station_idx,
                                [[maybe_unused]] size_t field_id) {
  aocommon::MC2x2F result;
  Response(beam_mode, &result, ra, dec, std::span(&freq, 1), station_idx,
           field_id);
  result.AssignTo(response_matrix);
}

void PhasedArrayPoint::Response(aocommon::MC2x2* result, BeamMode beam_mode,
                                size_t station_idx,
                                std::span<const double> freqs,
                                const vector3r_t& direction,
                                std::mutex* mutex) {
  if (HasTimeUpdate()) {
    if (mutex != nullptr) {
      // Caller takes over responsibility to be thread-safe
      UpdateITRFVectors(*mutex);
    } else {
      // Callee assumes that caller is thread-safe
      UpdateITRFVectors(mutex_);
    }
    ClearTimeUpdate();
    has_partial_itrf_update_ = true;
  }

  UnnormalisedResponse(result, beam_mode, station_idx, freqs, direction,
                       station0_, tile0_);

  // Conversion to MC2x2 (double) for inverse_central_gain needed
  for (size_t f = 0; f < freqs.size(); ++f) {
    aocommon::MC2x2F inverse_central_gain;
    const bool apply_normalisation = CalculateBeamNormalisation(
        beam_mode, GetTime(), freqs[f], station_idx, inverse_central_gain);
    if (apply_normalisation) {
      result[f] = aocommon::MC2x2(inverse_central_gain) * result[f];
    }
  }
}

void PhasedArrayPoint::UnnormalisedResponse(
    aocommon::MC2x2* result, BeamMode beam_mode, size_t station_idx,
    const std::span<const double>& freqs, const vector3r_t& direction,
    const vector3r_t& station0, const vector3r_t& tile0) const {
  const PhasedArray& phased_array = GetPhasedArray();

  std::span<const double> reference_freqs;
  // Avoid allocating the vector unnecessarily
  std::vector<double> subband_freqs;
  if (phased_array.GetOptions().use_channel_frequency) {
    reference_freqs = freqs;
  } else {
    subband_freqs.assign(freqs.size(), phased_array.GetSubbandFrequency());
    reference_freqs = subband_freqs;
  }

  phased_array.GetStation(station_idx)
      .Response(result, beam_mode, GetTime(), freqs, direction, reference_freqs,
                station0, tile0, is_local_, rotate_);
}

// Inlining this function causes issues, likely because of different
// ABIs of span between gcc versions 9 and 10.
aocommon::MC2x2 PhasedArrayPoint::UnnormalisedResponse(
    BeamMode beam_mode, size_t station_idx, double frequency,
    const vector3r_t& direction, const vector3r_t& station0,
    const vector3r_t& tile0) const {
  const PhasedArray& phased_array = GetPhasedArray();
  const double reference_frequency =
      phased_array.GetOptions().use_channel_frequency
          ? frequency
          : phased_array.GetSubbandFrequency();

  aocommon::MC2x2 result;
  phased_array.GetStation(station_idx)
      .Response(&result, beam_mode, GetTime(), std::span(&frequency, 1),
                direction, std::span(&reference_frequency, 1), station0, tile0,
                is_local_, rotate_);
  return result;
}

void PhasedArrayPoint::ElementResponse(aocommon::MC2x2* result,
                                       size_t station_idx,
                                       const std::span<const double>& freqs,
                                       const vector3r_t& direction,
                                       size_t element_idx) const {
  GetPhasedArray()
      .GetStation(station_idx)
      .ComputeElementResponse(result, GetTime(), freqs, direction, element_idx,
                              is_local_, rotate_);
}

void PhasedArrayPoint::UpdateITRFVectors(double ra, double dec) {
  const PhasedArray& phased_array = GetPhasedArray();
  ra_ = ra;
  dec_ = dec;
  // lock, since casacore::Direction is not thread-safe
  // The lock prevents different PhasedArrayPoints to calculate the
  // the station response simultaneously
  std::unique_lock<std::mutex> lock(mutex_);
  const coords::ItrfConverter itrf_converter(GetIntervalMidPoint());
  station0_ = itrf_converter.ToItrf(phased_array.GetDelayDirection());
  tile0_ = itrf_converter.ToItrf(phased_array.GetTileBeamDirection());
  // Only the n vector is relevant for a single point. l and m are not.
  itrf_direction_ = itrf_converter.RaDecToItrf(ra, dec);
  diff_beam_centre_ =
      itrf_converter.ToItrf(phased_array.GetPreappliedBeamDirection());
}

void PhasedArrayPoint::UpdateITRFVectors(std::mutex& mutex) {
  const PhasedArray& phased_array = GetPhasedArray();
  std::unique_lock<std::mutex> lock(mutex);
  const coords::ItrfConverter itrf_converter(GetTime());
  station0_ = itrf_converter.ToItrf(phased_array.GetDelayDirection());
  tile0_ = itrf_converter.ToItrf(phased_array.GetTileBeamDirection());
}

}  // namespace pointresponse
}  // namespace everybeam
