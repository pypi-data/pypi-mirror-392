// Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "../circularsymmetric/voltagepattern.h"

#include <aocommon/imagecoordinates.h>
#include <casacore/measures/Measures/MeasMath.h>
#include <boost/test/unit_test.hpp>

BOOST_AUTO_TEST_SUITE(tvoltagepattern)

BOOST_AUTO_TEST_CASE(voltagepattern) {
  // Setup
  const aocommon::UVector<double> kCoefficients = {
      1.0, -0.3514e-03, 0.5600e-07, -0.0474e-10, 0.00078e-13, 0.00019e-16};
  const double kMaxRadiusArcMin = 71;
  const double kReferenceFrequency = 1.278e9;
  const double kFrequency = 8.56313e+08;
  const double kRa = 0.90848969;
  const double kDec = -0.48149271;
  const double kDirRa = kRa + 0.01;
  const double kDirDec = kDec - 0.02;
  const std::vector<std::complex<float>> kReferenceResponse = {
      {0.382599, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.382599, 0.0}};

  everybeam::circularsymmetric::VoltagePattern vp({kFrequency},
                                                  kMaxRadiusArcMin);
  vp.EvaluatePolynomial(kCoefficients, kReferenceFrequency, false);

  std::vector<std::complex<float>> buffer(4);
  vp.Render(buffer.data(), kRa, kDec, kDirRa, kDirDec, kFrequency);

  // Compare response to reference.
  for (size_t i = 0; i < buffer.size(); ++i) {
    BOOST_CHECK_CLOSE(buffer[i], kReferenceResponse[i], 2.0e-4);
  }

  double angle =
      aocommon::ImageCoordinates::AngularDistance(kRa, kDec, kDirRa, kDirDec);
  const aocommon::MC2x2Diag response =
      vp.Render(std::span(&angle, 1), kFrequency).front();

  // Compare response to reference.
  BOOST_CHECK_CLOSE(response.Get(0), kReferenceResponse[0], 2.0e-4);
  BOOST_CHECK_CLOSE(response.Get(1), kReferenceResponse[3], 2.0e-4);
}

BOOST_AUTO_TEST_SUITE_END()