// Copyright (C) 2021 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "mwapoint.h"

#include <aocommon/matrix2x2.h>

#include <casacore/measures/Measures/MCPosition.h>

#include "../telescope/mwa.h"
#include "pointresponse/dishpoint.h"

namespace everybeam {
using mwabeam::TileBeam2016;
namespace pointresponse {

void MWAPoint::Response(BeamMode /* beam_mode */, std::complex<float>* buffer,
                        double ra, double dec, double freq,
                        size_t /* station_idx */, size_t /* field_id */) {
  const telescope::MWA& mwatelescope =
      static_cast<const telescope::MWA&>(GetTelescope());

  // Only compute J2000 vectors if time was updated
  if (HasTimeUpdate()) {
    SetJ200Vectors();
    ClearTimeUpdate();
  }

  if (!tile_beam_) {
    if (mwatelescope.GetOptions().coeff_path.empty()) {
      throw std::runtime_error("Missing path for MWA coefficients h5 file");
    }
    tile_beam_.emplace(mwatelescope.GetDelays().data(),
                       mwatelescope.GetOptions().frequency_interpolation,
                       mwatelescope.GetOptions().coeff_path);
  }

  aocommon::MC2x2 gains;
  tile_beam_->ArrayResponse(ra, dec, j2000_ref_, j2000_to_hadecref_,
                            j2000_to_azelgeoref_, arr_latitude_, freq, gains);
  gains.AssignTo(buffer);
}

void MWAPoint::ResponseDouble(BeamMode beam_mode,
                              aocommon::MC2x2* response_matrices, double ra,
                              double dec, std::span<const double> frequencies,
                              size_t station_id, size_t field_id) {
  const telescope::MWA& mwatelescope =
      static_cast<const telescope::MWA&>(GetTelescope());

  // Only compute J2000 vectors if time was updated
  if (HasTimeUpdate()) {
    SetJ200Vectors();
    ClearTimeUpdate();
  }

  if (!tile_beam_) {
    if (mwatelescope.GetOptions().coeff_path.empty()) {
      throw std::runtime_error("Missing path for MWA coefficients h5 file");
    }
    tile_beam_.emplace(mwatelescope.GetDelays().data(),
                       mwatelescope.GetOptions().frequency_interpolation,
                       mwatelescope.GetOptions().coeff_path);
  }

  tile_beam_->ArrayResponse(ra, dec, j2000_ref_, j2000_to_hadecref_,
                            j2000_to_azelgeoref_, arr_latitude_, frequencies,
                            response_matrices);
}

void MWAPoint::Response(BeamMode beam_mode, aocommon::MC2x2F* response_matrices,
                        double ra, double dec,
                        std::span<const double> frequencies, size_t station_id,
                        size_t field_id) {
  std::vector<aocommon::MC2x2> result(frequencies.size());
  ResponseDouble(beam_mode, result.data(), ra, dec, frequencies, station_id,
                 field_id);
  for (aocommon::MC2x2 m : result) {
    *response_matrices = aocommon::MC2x2F(m);
    ++response_matrices;
  }
}

aocommon::MC2x2 MWAPoint::Response(BeamMode beam_mode, size_t station_idx,
                                   double freq,
                                   const vector3r_t& itrf_direction,
                                   std::mutex* mutex) {
  aocommon::MC2x2 result;
  Response(&result, beam_mode, station_idx, std::span(&freq, 1), itrf_direction,
           mutex);
  return result;
}

void MWAPoint::Response(aocommon::MC2x2* result, BeamMode beam_mode,
                        size_t station_idx, std::span<const double> freqs,
                        const vector3r_t& itrf_direction, std::mutex* mutex) {
  // This is a simple implementation of the ITRF MWA response function in order
  // to get Dp3 to work with the MWA beam. It is quite slow because it does a
  // itrf->j2000->hadec.
  std::unique_lock<std::mutex> lock;
  if (mutex) lock = std::unique_lock<std::mutex>(*mutex);
  const casacore::MEpoch time_epoch(
      casacore::Quantity(GetIntervalMidPoint(), "s"));
  const telescope::MWA& mwatelescope =
      static_cast<const telescope::MWA&>(GetTelescope());
  casacore::MeasFrame frame(mwatelescope.GetArrayPosition(), time_epoch);
  const casacore::Vector<double> itrf_coord(
      {itrf_direction[0], itrf_direction[1], itrf_direction[2]});
  const casacore::Quantum<casacore::Vector<double>> itrf(itrf_coord, "m");
  const casacore::MDirection direction_itrf(itrf, casacore::MDirection::ITRF);
  casacore::MDirection::Convert measure_converter(
      casacore::MDirection::Ref(casacore::MDirection::ITRF, frame),
      casacore::MDirection::J2000);
  const casacore::Vector<double> j2000_dir =
      measure_converter(itrf).getValue().getValue();

  ResponseDouble(beam_mode, result, j2000_dir[0], j2000_dir[1], freqs,
                 station_idx, 0);
}

void MWAPoint::ResponseAllStations(BeamMode beam_mode,
                                   std::complex<float>* buffer, double ra,
                                   double dec, double freq, size_t) {
  Response(beam_mode, buffer, ra, dec, freq, 0.0, 0);
  // Just repeat nstations times
  for (size_t i = 1; i != GetTelescope().GetNrStations(); ++i) {
    std::copy_n(buffer, 4, buffer + i * 4);
  }
}

void MWAPoint::SetJ200Vectors() {
  const telescope::MWA& mwatelescope =
      static_cast<const telescope::MWA&>(GetTelescope());
  // lock, since casacore::Direction is not thread-safe.
  // The lock prevents different MWAPoints to calculate the
  // the station response simultaneously
  std::unique_lock<std::mutex> lock(mutex_);
  casacore::MEpoch time_epoch(casacore::Quantity(GetIntervalMidPoint(), "s"));
  casacore::MeasFrame frame(mwatelescope.GetArrayPosition(), time_epoch);

  const casacore::MDirection::Ref hadec_ref(casacore::MDirection::HADEC, frame);
  const casacore::MDirection::Ref azelgeo_ref(casacore::MDirection::AZELGEO,
                                              frame);
  j2000_ref_ = casacore::MDirection::Ref(casacore::MDirection::J2000, frame);
  j2000_to_hadecref_(j2000_ref_, hadec_ref);
  j2000_to_azelgeoref_(j2000_ref_, azelgeo_ref);
  casacore::MPosition wgs = casacore::MPosition::Convert(
      mwatelescope.GetArrayPosition(), casacore::MPosition::WGS84)();
  arr_latitude_ = wgs.getValue().getLat();
}
}  // namespace pointresponse
}  // namespace everybeam
