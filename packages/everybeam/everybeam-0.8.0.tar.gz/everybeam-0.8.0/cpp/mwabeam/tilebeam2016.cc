// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "tilebeam2016.h"

#include <casacore/measures/Measures/MDirection.h>
#include <casacore/measures/Measures/MCPosition.h>
#include <casacore/measures/Measures/MeasConvert.h>

namespace everybeam {
namespace mwabeam {

TileBeam2016::TileBeam2016(const double* delays, bool frequency_interpolation,
                           const std::string& coeff_path)
    : Beam2016Implementation(delays, nullptr, coeff_path),
      frequency_interpolation_(frequency_interpolation) {}

void TileBeam2016::ArrayResponse(
    double ra, double dec, const casacore::MDirection::Ref& j2000_ref,
    casacore::MDirection::Convert& j2000_to_hadec,
    casacore::MDirection::Convert& j2000_to_azelgeo, double arr_lattitude,
    double frequency, aocommon::MC2x2& gain) {
  static const casacore::Unit rad_unit("rad");
  const casacore::MDirection image_dir(
      casacore::MVDirection(casacore::Quantity(ra, rad_unit),    // RA
                            casacore::Quantity(dec, rad_unit)),  // DEC
      j2000_ref);

  // convert ra, dec to ha
  const casacore::MDirection hadec = j2000_to_hadec(image_dir);
  const double ha = hadec.getValue().get()[0];
  const double sin_lat = std::sin(arr_lattitude),
               cos_lat = std::cos(arr_lattitude);
  const double sin_dec = std::sin(dec), cos_dec = std::cos(dec);
  const double cos_ha = std::cos(ha);
  const double zenith_distance =
      std::acos(sin_lat * sin_dec + cos_lat * cos_dec * cos_ha);
  const casacore::MDirection azel = j2000_to_azelgeo(image_dir);
  const double azimuth = azel.getValue().get()[0];
  ArrayResponse(zenith_distance, azimuth, std::span(&frequency, 1), &gain);
}

void TileBeam2016::ArrayResponse(
    double ra, double dec, const casacore::MDirection::Ref& j2000_ref,
    casacore::MDirection::Convert& j2000_to_hadec,
    casacore::MDirection::Convert& j2000_to_azelgeo, double arr_lattitude,
    std::span<const double> frequencies, aocommon::MC2x2* gains) {
  static const casacore::Unit rad_unit("rad");
  const casacore::MDirection image_dir(
      casacore::MVDirection(casacore::Quantity(ra, rad_unit),    // RA
                            casacore::Quantity(dec, rad_unit)),  // DEC
      j2000_ref);

  // convert ra, dec to ha
  const casacore::MDirection hadec = j2000_to_hadec(image_dir);
  const double ha = hadec.getValue().get()[0];
  const double sin_lat = std::sin(arr_lattitude),
               cos_lat = std::cos(arr_lattitude);
  const double sin_dec = std::sin(dec), cos_dec = std::cos(dec);
  const double cos_ha = std::cos(ha);
  const double zenith_distance =
      std::acos(sin_lat * sin_dec + cos_lat * cos_dec * cos_ha);
  const casacore::MDirection azel = j2000_to_azelgeo(image_dir);
  const double azimuth = azel.getValue().get()[0];
  ArrayResponse(zenith_distance, azimuth, frequencies, gains);
}

/**
 * Get the full Jones matrix response of the tile including the dipole
 * response and array factor incorporating any mutual coupling effects
 * from the impedance matrix. freq in Hz.
 */
void TileBeam2016::GetTabulatedResponse(double az, double za,
                                        std::span<const double> frequencies,
                                        aocommon::MC2x2* results) {
  // input are radians -> convert to degrees as implementation class expects :
  double az_deg = az * (180.00 / M_PI);
  double za_deg = za * (180.00 / M_PI);
  CalcJones(results, az_deg, za_deg, frequencies, true);
}
}  // namespace mwabeam
}  // namespace everybeam
