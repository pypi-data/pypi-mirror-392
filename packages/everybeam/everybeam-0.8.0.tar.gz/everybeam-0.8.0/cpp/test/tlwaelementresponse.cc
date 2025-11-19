// Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "../lwa/lwaelementresponse.h"

#include <boost/test/unit_test.hpp>

#include "config.h"

BOOST_AUTO_TEST_SUITE(lwaelementresponse)

BOOST_AUTO_TEST_CASE(get_model) {
  // Verify the element response model of LwaElementResponse.
  everybeam::Options options;
  options.coeff_path = LWA_COEFF_PATH;
  auto lwa_reponse = everybeam::LwaElementResponse::GetInstance(options);
  BOOST_TEST(lwa_reponse->GetModel() == everybeam::ElementResponseModel::kLwa);
}

BOOST_AUTO_TEST_CASE(internal_data) {
  // Verify the consistency of internal data of
  // LwaElementResponse generated from the LWA coefficients file.
  using Coefficients = xt::xtensor<std::complex<double>, 4>;
  using Frequencies = xt::xtensor<double, 1>;
  using Nms = xt::xtensor<int, 2>;

  everybeam::Options options;
  options.coeff_path = LWA_COEFF_PATH;
  auto lwa_response = everybeam::LwaElementResponse::GetInstance(options);
  const Coefficients& lwa_coeff = lwa_response->GetCoefficients();
  const Frequencies& lwa_freq = lwa_response->GetFrequencies();
  const Nms& lwa_nms = lwa_response->GetNms();

  const std::array<size_t, 4> coeff_shape = {2, 91, 1, 966};
  const std::array<size_t, 1> freq_shape = {91};
  const std::array<size_t, 2> nms_shape = {966, 3};

  BOOST_TEST(lwa_coeff.shape() == coeff_shape);
  BOOST_TEST(lwa_freq.shape() == freq_shape);
  BOOST_TEST(lwa_nms.shape() == nms_shape);
}

BOOST_AUTO_TEST_CASE(lwa_response_0) {
  // Compute element response for some
  // input values to verify consistency.
  everybeam::Options options;
  options.coeff_path = LWA_COEFF_PATH;
  auto lwa_response = everybeam::LwaElementResponse::GetInstance(options);
  const int id = 0;
  const double frequency = 10000000.0;
  const double theta = 0.0;
  const double phi = 1.0;
  const aocommon::MC2x2 target_response(
      {-0.00363067367, -0.00429036936}, {-0.00231565972, -0.00273170026},
      {-0.00233455626, -0.00275989118}, {0.00361090657, 0.00426006178});

  aocommon::MC2x2 element_response =
      lwa_response->Response(id, frequency, theta, phi);

  for (size_t i = 0; i != 4; ++i) {
    BOOST_CHECK_CLOSE(element_response.Get(i).real(),
                      target_response.Get(i).real(), 1.0e-4);
    BOOST_CHECK_CLOSE(element_response.Get(i).imag(),
                      target_response.Get(i).imag(), 1.0e-4);
  }
}

BOOST_AUTO_TEST_CASE(lwa_response_1) {
  // Compute element response for some
  // input values to verify consistency.
  everybeam::Options options;
  options.coeff_path = LWA_COEFF_PATH;
  auto lwa_response = everybeam::LwaElementResponse::GetInstance(options);
  const int id = 0;
  const double frequency = 20000000.0;
  const double theta = 0.5;
  const double phi = 0.3;
  const aocommon::MC2x2 target_response(
      {-0.00425486131, -0.01124062027}, {-0.01474458325, -0.03998484366},
      {-0.01356533729, -0.03639320957}, {0.00450749533, 0.01238830873});

  aocommon::MC2x2 element_response =
      lwa_response->Response(id, frequency, theta, phi);

  for (size_t i = 0; i != 4; ++i) {
    BOOST_CHECK_CLOSE(element_response.Get(i).real(),
                      target_response.Get(i).real(), 1.0e-4);
    BOOST_CHECK_CLOSE(element_response.Get(i).imag(),
                      target_response.Get(i).imag(), 1.0e-4);
  }
}

BOOST_AUTO_TEST_SUITE_END()
