// Copyright (C) 2024 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "dishpoint.h"

#include <algorithm>
#include <cmath>

#include <aocommon/uvector.h>

#include "../telescope/dish.h"
#include "../circularsymmetric/voltagepattern.h"
#include "../circularsymmetric/vlacoefficients.h"
#include "./../coords/itrfdirection.h"
#include "./../coords/itrfconverter.h"
#include "../common/mathutils.h"

namespace everybeam {
namespace pointresponse {

DishPoint::DishPoint(const telescope::Dish& dish, double time)
    : PointResponse(&dish, time),
      dish_(dish),
      pointing_(dish_.GetFieldPointingMDirection().at(0)){};

void DishPoint::Response(BeamMode /* beam_mode */, std::complex<float>* buffer,
                         double ra, double dec, double freq,
                         size_t /* station_idx */, size_t field_id) {
  double pdir_ra;
  double pdir_dec;
  std::tie(pdir_ra, pdir_dec) = dish_.GetFieldPointing()[field_id];
  const double max_radius_arc_min =
      dish_.GetDishCoefficients()->MaxRadiusInArcMin();
  const double reference_frequency =
      dish_.GetDishCoefficients()->ReferenceFrequency();

  // The computation below is ineffecient just a single point,
  // see https://git.astron.nl/RD/EveryBeam/-/merge_requests/335#note_88457
  circularsymmetric::VoltagePattern vp(
      dish_.GetDishCoefficients()->GetFrequencies(freq), max_radius_arc_min);
  const aocommon::UVector<double> coefs_vec =
      dish_.GetDishCoefficients()->GetCoefficients(freq);
  vp.EvaluatePolynomial(coefs_vec, reference_frequency,
                        dish_.GetDishCoefficients()->AreInverted());
  vp.Render(buffer, ra, dec, pdir_ra, pdir_dec, freq);
}

aocommon::MC2x2 DishPoint::Response(BeamMode beam_mode, size_t station_idx,
                                    double freq, const vector3r_t& direction,
                                    std::mutex* mutex) {
  std::complex<float> buffer[4];

  if (HasTimeUpdate()) {
    // Compute ITRF pointing
    {
      std::unique_lock<std::mutex> lock(*(mutex ? mutex : &mutex_));
      const coords::ItrfConverter itrf_converter(GetIntervalMidPoint());
      pointing_itrf_ = itrf_converter.ToItrf(pointing_);
    }
    ClearTimeUpdate();
  }

  // Compute pointing_direction_angle
  double pointing_direction_angle =
      acos(std::max(std::min(dot(pointing_itrf_, direction), 1.0), -1.0));

  const double max_radius_arc_min =
      dish_.GetDishCoefficients()->MaxRadiusInArcMin();
  const double reference_frequency =
      dish_.GetDishCoefficients()->ReferenceFrequency();

  // The computation below is ineffecient just a single point,
  // see https://git.astron.nl/RD/EveryBeam/-/merge_requests/335#note_88457
  circularsymmetric::VoltagePattern vp(
      dish_.GetDishCoefficients()->GetFrequencies(freq), max_radius_arc_min);
  const aocommon::UVector<double> coefs_vec =
      dish_.GetDishCoefficients()->GetCoefficients(freq);
  vp.EvaluatePolynomial(coefs_vec, reference_frequency,
                        dish_.GetDishCoefficients()->AreInverted());

  // Because the voltage pattern is circular symmetric, the result
  // depends only on the angle between the pointing and the requested direction
  // Calling Render with direction_ra=pointing_direction_angle,
  // direction_dec=0.0 and pointing_ra=0.0, pointing_ra=dec=0.0 yields the
  // correct result

  vp.Render(buffer, pointing_direction_angle, 0.0, 0.0, 0.0, freq);

  return aocommon::MC2x2(aocommon::MC2x2F(buffer));
}

void DishPoint::ResponseAllStations(BeamMode beam_mode,
                                    std::complex<float>* buffer, double ra,
                                    double dec, double freq, size_t field_id) {
  Response(beam_mode, buffer, ra, dec, freq, 0u, field_id);

  // Just repeat nstations times
  for (size_t i = 1; i != GetTelescope().GetNrStations(); ++i) {
    std::copy_n(buffer, 4, buffer + i * 4);
  }
}
}  // namespace pointresponse
}  // namespace everybeam
