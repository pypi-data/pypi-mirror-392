// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_MWABEAM_TILEBEAM2016_H_
#define EVERYBEAM_MWABEAM_TILEBEAM2016_H_

#include <complex>
#include <map>
#include <set>
#include <span>

#include "beam2016implementation.h"

#include <aocommon/matrix2x2.h>

#include <casacore/measures/Measures/MEpoch.h>
#include <casacore/measures/Measures/MPosition.h>
#include <casacore/measures/Measures/MDirection.h>
#include <casacore/measures/Measures/MCDirection.h>

namespace everybeam {
namespace mwabeam {

class TileBeam2016 : public Beam2016Implementation {
 public:
  TileBeam2016(const double* delays, bool frequency_interpolation,
               const std::string& coeff_path);

  /**
   * @brief API method for computing MWA array response
   *
   * @param ra right ascension (rad)
   * @param dec declination (rad)
   * @param j2000_ref J2000 ref coordinates
   * @param j2000_to_hadecref HADEC coordinates
   * @param j2000_to_azelgeoref AZELGEO coordinates
   * @param arr_lattitude Lattitude
   * @param frequency Frequency (Hz)
   * @param gain Gain matrix
   */
  void ArrayResponse(double ra, double dec,
                     const casacore::MDirection::Ref& j2000_ref,
                     casacore::MDirection::Convert& j2000_to_hadecref,
                     casacore::MDirection::Convert& j2000_to_azelgeoref,
                     double arr_lattitude, double frequency,
                     aocommon::MC2x2& gain);

  /**
   * Same as above, but calculates for multiple frequencies at once.
   */
  void ArrayResponse(double ra, double dec,
                     const casacore::MDirection::Ref& j2000_ref,
                     casacore::MDirection::Convert& j2000_to_hadecref,
                     casacore::MDirection::Convert& j2000_to_azelgeoref,
                     double arr_lattitude, std::span<const double> frequencies,
                     aocommon::MC2x2* gain);

  /**
   * @brief Compute MWA array response in given zenith/azimuth direction
   *
   * @param zenith_angle Zenith angle (rad)
   * @param azimuth Azimuthal angle (rad)
   * @param frequency Frequency (Hz)
   * @param gain Gain matrix
   */
  void ArrayResponse(double zenith_angle, double azimuth,
                     std::span<const double> frequencies,
                     aocommon::MC2x2* gains) {
    // As yet, this conditional is redundant, see GetInterpolatedResponse().
    if (frequency_interpolation_)
      GetInterpolatedResponse(azimuth, zenith_angle, frequencies, gains);
    else
      GetTabulatedResponse(azimuth, zenith_angle, frequencies, gains);
  }

 private:
  bool frequency_interpolation_;

  /**
   * Get the full Jones matrix response of the tile including the dipole
   * response and array factor incorporating any mutual coupling effects
   * from the impedance matrix. freq in Hz.
   */
  void GetTabulatedResponse(double az, double za,
                            std::span<const double> frequencies,
                            aocommon::MC2x2* results);

  /**
   * Create a few tabulated responses and interpolated over these.
   */
  void GetInterpolatedResponse(double az, double za,
                               std::span<const double> frequencies,
                               aocommon::MC2x2* results) {
    // Not implemented yet: just call normal function
    GetTabulatedResponse(az, za, frequencies, results);
  }
};
}  // namespace mwabeam
}  // namespace everybeam
#endif  // EVERYBEAM_MWABEAM_TILEBEAM2016_H_
