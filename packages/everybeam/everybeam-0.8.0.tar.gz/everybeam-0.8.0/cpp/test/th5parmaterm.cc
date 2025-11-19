// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include <boost/test/unit_test.hpp>

#include "config.h"
#include "../aterms/h5parmaterm.h"

#include <aocommon/uvector.h>
#include <aocommon/imagecoordinates.h>
#include <vector>
#include <complex>
#include <math.h>

using everybeam::aterms::H5ParmATerm;
using everybeam::aterms::LagrangePolynomial;
using schaapcommon::h5parm::H5Parm;

std::string h5parmaterm_mock = H5PARMATERM_MOCK_PATH;

BOOST_AUTO_TEST_SUITE(th5parmaterm)
// Explicit, but inefficient evaluation of polynomials, for reference only
double ExplicitPolynomialEvaluation(double x, double y, size_t order,
                                    const std::vector<double>& coeffs) {
  double sol = 0;
  size_t idx = 0;
  for (size_t n = 0; n < order + 1; ++n) {
    for (size_t k = 0; k < n + 1; ++k) {
      sol += coeffs[idx] * pow(x, n - k) * pow(y, k);
      idx += 1;
    }
  }
  return sol;
}

// Convenience method to convert pixel coordinates to lm coordinates
std::pair<std::vector<double>, std::vector<double>> ConvertXYToLM(
    aocommon::CoordinateSystem coord_system) {
  std::pair<std::vector<double>, std::vector<double>> result;
  for (size_t y = 0; y < coord_system.height; ++y) {
    for (size_t x = 0; x < coord_system.width; ++x) {
      double l, m;
      aocommon::ImageCoordinates::XYToLM(x, y, coord_system.dl, coord_system.dm,
                                         coord_system.width,
                                         coord_system.height, l, m);
      result.first.push_back(l);
      result.second.push_back(m);
    }
  }
  return result;
}

/**
 * @brief Compute coefficients that should be stored in the H5PARMATERM_MOCK.h5
 * file. Compute coefficients that should be stored in the H5PARMATERM_MOCK.h5
 * file. flattened, where TOTAL_NR_COEFFS = nstations * ntimes * ncoeffs
 *
 * The (python) script for generating the H5PARMATERM_MOCK.h5 file can be found
 * in the scripts/misc/ directory (scripts/misc/make_h5parmaterm_mock.py).
 *
 * @param porder Polynomial order
 * @param sidx Station index
 * @param tidx Time index
 * @return std::vector<float> Vector of coefficients
 */
std::vector<double> ComputeTestCoeffs(size_t porder, size_t sidx,
                                      hsize_t tidx) {
  size_t nr_coeffs = LagrangePolynomial::ComputeNrCoeffs(porder);
  std::vector<double> x, y;
  LagrangePolynomial polynomial(nr_coeffs, x, y);
  std::vector<double> coeffs(nr_coeffs);
  for (size_t i = 0; i < coeffs.size(); ++i) {
    coeffs[i] = (nr_coeffs * sidx + (i + 1)) * (tidx + 1);
  }
  return coeffs;
}

// Zero order polynomial
BOOST_AUTO_TEST_CASE(test_lagrange_0) {
  std::vector<double> x(1, 20), y(1, 6);

  LagrangePolynomial poly(1, x, y);
  BOOST_CHECK_EQUAL(poly.GetOrder(), 0);

  // Make coefficients for binomial:
  // f(x,y) = 10
  std::vector<double> coeffs = {10};

  double result;
  poly.Evaluate(coeffs.data(), 1, &result);
  double ref =
      ExplicitPolynomialEvaluation(x[0], y[0], poly.GetOrder(), coeffs);
  BOOST_CHECK_EQUAL(result, ref);
}

// First order polynomial
BOOST_AUTO_TEST_CASE(test_lagrange_1) {
  std::vector<double> x(1, 20), y(1, 6);
  LagrangePolynomial poly(3, x, y);
  BOOST_CHECK_EQUAL(poly.GetOrder(), 1);

  // Make coefficients for binomial:
  // f(x,y) = 10 - 4x + 3y
  std::vector<double> coeffs = {10, -4, 3};

  double result;
  poly.Evaluate(coeffs.data(), 1, &result);
  double ref =
      ExplicitPolynomialEvaluation(x[0], y[0], poly.GetOrder(), coeffs);
  BOOST_CHECK_EQUAL(result, ref);
}

// Second order polynomial
BOOST_AUTO_TEST_CASE(test_lagrange_2) {
  // Second order binomial has 6 terms
  std::vector<double> x(1, 20), y(1, 6);
  LagrangePolynomial poly(6, x, y);
  BOOST_CHECK_EQUAL(poly.GetOrder(), 2);

  // Make coefficients for binomial:
  // f(x,y) = 4 + 3x - 2y + 5x^2 - 2xy + 4y^2
  std::vector<double> coeffs = {4, 3, -2, 5, -2, 4};

  double result;
  poly.Evaluate(coeffs.data(), 1, &result);
  double ref =
      ExplicitPolynomialEvaluation(x[0], y[0], poly.GetOrder(), coeffs);
  BOOST_CHECK_EQUAL(result, ref);
}

// Third order polynomial
BOOST_AUTO_TEST_CASE(test_lagrange_3) {
  std::vector<double> x(1, 20), y(1, 6);
  // Third order binomial has 10 terms
  LagrangePolynomial poly(10, x, y);
  BOOST_CHECK_EQUAL(poly.GetOrder(), 3);

  // Make coefficients for binomial:
  // f(x,y) = 10 - x + 2y + 3x^2 + 4xy - 5y^2 + 6x^3 + 0x^2y + 7xy^2 + 8y^3
  std::vector<double> coeffs = {10, -1, 2, 3, 4, -5, 6, 2, 7, 8};

  double result;
  poly.Evaluate(coeffs.data(), 1, &result);
  double ref =
      ExplicitPolynomialEvaluation(x[0], y[0], poly.GetOrder(), coeffs);
  BOOST_CHECK_EQUAL(result, ref);
}

BOOST_AUTO_TEST_CASE(read_h5parmfile) {
  std::vector<std::string> h5parm_files = {h5parmaterm_mock};
  // Names in H5PARMATERM_MOCK.h5 should match Antenna0, Antenna1
  std::vector<std::string> station_names = {"Antenna0", "Antenna1"};

  double frequency = 57812500.;
  double ra(-1.44194878), dec(0.85078091);

  // Properties of grid
  std::size_t width(4), height(4);
  double dl(0.5 * M_PI / 180.), dm(0.5 * M_PI / 180.), shift_l(0.), shift_m(0.);

  aocommon::CoordinateSystem coord_system = {width, height, ra,      dec,
                                             dl,    dm,     shift_l, shift_m};

  H5ParmATerm h5parmaterm(station_names, coord_system);
  h5parmaterm.Open(h5parm_files);

  // Needed for reference solution
  H5Parm h5parm_tmp = H5Parm(h5parm_files[0]);
  std::pair<std::vector<double>, std::vector<double>> image_coords =
      ConvertXYToLM(coord_system);
  LagrangePolynomial diagonal_polynomial(6, image_coords.first,
                                         image_coords.second);
  LagrangePolynomial phase_polynomial(3, image_coords.first,
                                      image_coords.second);

  for (float time = 0; time <= 10; ++time) {
    // Compute solution with H5ParmATerm
    aocommon::UVector<std::complex<float>> h5parm_buffer(
        width * height * station_names.size() * 4);
    h5parmaterm.Calculate(h5parm_buffer.data(), time, frequency, 0, nullptr);
    // Compute reference solution
    hsize_t tindex_ampl =
        h5parm_tmp.GetSolTab("amplitude1_coefficients").GetTimeIndex(time);
    hsize_t tindex_phase =
        h5parm_tmp.GetSolTab("phase_coefficients").GetTimeIndex(time);

    for (size_t i = 0; i < station_names.size(); ++i) {
      std::vector<double> diagonal_coeffs =
          ComputeTestCoeffs(2, i, tindex_ampl);
      std::vector<double> phase_coeffs = ComputeTestCoeffs(1, i, tindex_phase);

      std::vector<double> ampl1_ref(width * height);
      std::vector<double> ampl2_ref(width * height);
      std::vector<double> phase_ref(width * height);
      std::vector<double> slowphase_ref(width * height);

      diagonal_polynomial.Evaluate(diagonal_coeffs.data(), 1, ampl1_ref.data());
      for (double& v : diagonal_coeffs) v += 1.0;
      diagonal_polynomial.Evaluate(diagonal_coeffs.data(), 1, ampl2_ref.data());

      phase_polynomial.Evaluate(phase_coeffs.data(), 1, phase_ref.data());
      for (double& v : diagonal_coeffs) v = 1.0;
      diagonal_polynomial.Evaluate(diagonal_coeffs.data(), 1,
                                   slowphase_ref.data());

      for (size_t j = 0; j < width * height; ++j) {
        const std::complex<float> ref1 = std::complex<float>(
            ampl1_ref[j] * exp(std::complex<double>(0, phase_ref[j])));
        const size_t offset = (i * width * height + j) * 4;
        const std::complex<float> result1 = h5parm_buffer[offset];

        BOOST_CHECK_CLOSE(std::abs(result1), std::abs(ref1), 1e-4);
        BOOST_CHECK_CLOSE(std::arg(result1), std::arg(ref1), 1e-4);

        const std::complex<float> ref2 = std::complex<float>(
            ampl2_ref[j] *
            exp(std::complex<double>(0, phase_ref[j] + slowphase_ref[j])));
        const std::complex<float> result2 = h5parm_buffer[offset + 3];
        BOOST_CHECK_CLOSE(std::abs(result2), std::abs(ref2), 1e-4);
        BOOST_CHECK_CLOSE(std::arg(result2), std::arg(ref2), 1e-4);
      }
    }
  }
}
BOOST_AUTO_TEST_SUITE_END()
