// Copyright (C) 2024 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include <boost/test/unit_test.hpp>

#include "config.h"
#include "../everybeam.h"
#include "../telescope.h"
#include "../load.h"
#include "../options.h"
#include "../pointresponse/dishpoint.h"
#include "../telescope/dish.h"
#include "../coords/itrfconverter.h"
#include "Eigen/src/Core/util/Macros.h"
#include "xtensor/xadapt.hpp"

namespace everybeam {
namespace {
// First time stamp in mock ms"
const double kTime = 5068498314.005126;
const double kFrequency = 8.56313e+08;
const double kRa = 0.90848969;
const double kDec = -0.48149271;

}  // namespace

BOOST_AUTO_TEST_SUITE(dish)

BOOST_AUTO_TEST_CASE(load_dish) {
  everybeam::Options options;

  casacore::MeasurementSet ms(DISH_MOCK_PATH);

  std::unique_ptr<everybeam::telescope::Telescope> telescope =
      everybeam::Load(ms, options);

  // Check that we have an Dish pointer.
  const everybeam::telescope::Dish* dish_telescope =
      dynamic_cast<const everybeam::telescope::Dish*>(telescope.get());
  BOOST_REQUIRE(dish_telescope);

  // Assert if correct number of stations
  BOOST_CHECK_EQUAL(dish_telescope->GetNrStations(), size_t{62});

  // Assert that we have a dish point response
  std::unique_ptr<everybeam::pointresponse::PointResponse> point_response =
      dish_telescope->GetPointResponse(kTime);
  everybeam::pointresponse::DishPoint* dish_point_response =
      dynamic_cast<everybeam::pointresponse::DishPoint*>(point_response.get());
  BOOST_REQUIRE(dish_point_response);

  const std::vector<std::vector<std::complex<float>>> kReferenceResponse = {
      {{1.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {1.0, 0.0}},
      {{0.382599, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.382599, 0.0}}};

  const coords::ItrfConverter itrf_converter(kTime);

  std::vector<std::pair<double, double>> offsets = {{0.0, 0.0}, {0.01, -0.02}};

  for (size_t j = 0; j < offsets.size(); j++) {
    // Check the two response functions
    const double ra = kRa + offsets[j].first;
    const double dec = kDec + offsets[j].second;
    const size_t kStationId = 0;
    const size_t kFieldId = 0;

    std::array<std::complex<float>, 4> point_response_buffer;
    dish_point_response->Response(everybeam::BeamMode::kFull,
                                  point_response_buffer.data(), ra, dec,
                                  kFrequency, kStationId, kFieldId);

    for (std::size_t i = 0; i < 4; ++i) {
      BOOST_CHECK_CLOSE(point_response_buffer[i], kReferenceResponse[j][i],
                        2.0e-4);
    }

    const vector3r_t direction = itrf_converter.RaDecToItrf(ra, dec);

    const aocommon::MC2x2 response = dish_point_response->Response(
        everybeam::BeamMode::kFull, kStationId, kFrequency, direction);

    for (std::size_t i = 0; i < 4; ++i) {
      BOOST_CHECK_CLOSE(response.Get(i),
                        std::complex<double>(kReferenceResponse[j][i]), 2.0e-4);
    }
  }
}

BOOST_AUTO_TEST_CASE(dish_multi_freq_compare) {
  // Setup.
  casacore::MeasurementSet ms(DISH_MOCK_PATH);

  std::unique_ptr<everybeam::telescope::Telescope> telescope =
      everybeam::Load(ms, Options());
  std::unique_ptr<everybeam::pointresponse::PointResponse> point_response =
      telescope->GetPointResponse(kTime);
  const std::vector<double> frequency_list({kFrequency, kFrequency + 200000});

  std::vector<aocommon::MC2x2F> multi_buffer(frequency_list.size());
  std::vector<aocommon::MC2x2F> single_buffer(frequency_list.size());

  point_response->Response(everybeam::BeamMode::kFull, multi_buffer.data(),
                           kRa + 0.01, kDec, frequency_list, 0, 0);

  // Check full response.
  for (size_t f = 0; f < frequency_list.size(); f++) {
    point_response->Response(everybeam::BeamMode::kFull, single_buffer.data(),
                             kRa + 0.01, kDec, std::span(&frequency_list[f], 1),
                             0, 0);

    for (size_t i = 0; i != 4; ++i) {
      BOOST_CHECK_CLOSE(multi_buffer[f].Get(i), single_buffer[0].Get(i), 1e-6);
    }
  }
}

BOOST_AUTO_TEST_CASE(new_interface_J2000) {
  // Setup
  const casacore::MeasurementSet ms(DISH_MOCK_PATH);

  const Telescope telescope = everybeam::Load(ms);

  const std::vector<std::vector<std::complex<float>>> kReferenceResponse = {
      {{1.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {1.0, 0.0}},
      {{0.382599, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.382599, 0.0}}};

  std::vector<double> frequencies = {kFrequency};
  std::vector<double> times = {kTime};
  std::vector<std::pair<double, double>> directions = {
      {kRa, kDec}, {kRa + 0.01, kDec - 0.02}};

  aocommon::UVector<aocommon::MC2x2F> single_station_response_buffer(
      directions.size());

  everybeam::SingleStationResponse(
      everybeam::BeamMode::kFull, single_station_response_buffer.data(),
      telescope, times, directions, frequencies, 0, 0);

  // Compare single station response to a precomputed reference.
  for (size_t channel = 0; channel < kReferenceResponse.size(); channel++) {
    const aocommon::MC2x2F response = single_station_response_buffer[channel];
    for (size_t i = 0; i < 4; ++i) {
      BOOST_CHECK_CLOSE(response.Get(i), kReferenceResponse[channel][i],
                        2.0e-4);
    }
  }

  // Setup
  aocommon::UVector<aocommon::MC2x2F> all_station_response_buffer(
      directions.size() * 62);

  everybeam::AllStationResponse(everybeam::BeamMode::kFull,
                                all_station_response_buffer.data(), telescope,
                                times, directions, frequencies, 0);
  const auto x_array = xt::adapt(all_station_response_buffer, {62, 2});

  // Compare multiple single station responses to an all station response.
  for (size_t station = 0; station < 62; ++station) {
    everybeam::SingleStationResponse(
        everybeam::BeamMode::kFull, single_station_response_buffer.data(),
        telescope, times, directions, frequencies, 0, station);

    for (size_t channel = 0; channel < kReferenceResponse.size(); channel++) {
      const aocommon::MC2x2F single_station_response =
          single_station_response_buffer[channel];
      const aocommon::MC2x2F all_station_response = x_array(station, channel);
      for (size_t i = 0; i < 4; ++i) {
        BOOST_CHECK_CLOSE(single_station_response.Get(i),
                          all_station_response.Get(i), 2.0e-4);
      }
    }
  }
}

BOOST_AUTO_TEST_CASE(new_interface_ITRF) {
  // Setup
  const casacore::MeasurementSet ms(DISH_MOCK_PATH);

  const Telescope telescope = everybeam::Load(ms);

  const std::vector<std::vector<std::complex<float>>> kReferenceResponse = {
      {{1.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {1.0, 0.0}},
      {{0.382599, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {0.382599, 0.0}}};

  std::vector<double> frequencies = {kFrequency};
  std::vector<double> times = {kTime};
  std::vector<std::pair<double, double>> directions = {
      {kRa, kDec}, {kRa + 0.01, kDec - 0.02}};
  std::vector<vector3r_t> itrf_directions;
  const coords::ItrfConverter itrf_converter(kTime);

  for (std::pair<double, double> direction : directions) {
    itrf_directions.push_back(
        itrf_converter.RaDecToItrf(direction.first, direction.second));
  }

  aocommon::UVector<aocommon::MC2x2F> single_station_response_buffer(
      directions.size());

  everybeam::SingleStationResponse(
      everybeam::BeamMode::kFull, single_station_response_buffer.data(),
      telescope, times, itrf_directions, frequencies, 0, 0);

  // Compare single station response to a precomputed reference.
  for (size_t channel = 0; channel < kReferenceResponse.size(); channel++) {
    const aocommon::MC2x2F response = single_station_response_buffer[channel];
    for (std::size_t i = 0; i < 4; ++i) {
      BOOST_CHECK_CLOSE(response.Get(i), kReferenceResponse[channel][i],
                        2.0e-4);
    }
  }

  // Setup
  aocommon::UVector<aocommon::MC2x2F> all_station_response_buffer(
      directions.size() * 62);

  everybeam::AllStationResponse(everybeam::BeamMode::kFull,
                                all_station_response_buffer.data(), telescope,
                                times, itrf_directions, frequencies, 0);
  const auto x_array = xt::adapt(all_station_response_buffer, {62, 2});

  // Compare multiple single station responses to an all station response.
  for (size_t station = 0; station < 62; ++station) {
    everybeam::SingleStationResponse(
        everybeam::BeamMode::kFull, single_station_response_buffer.data(),
        telescope, times, itrf_directions, frequencies, 0, station);

    for (size_t channel = 0; channel < kReferenceResponse.size(); channel++) {
      const aocommon::MC2x2F single_station_response =
          single_station_response_buffer[channel];
      const aocommon::MC2x2F all_station_response = x_array(station, channel);
      for (size_t i = 0; i < 4; ++i) {
        BOOST_CHECK_CLOSE(single_station_response.Get(i),
                          all_station_response.Get(i), 2.0e-4);
      }
    }
  }
}

BOOST_AUTO_TEST_SUITE_END()

}  // namespace everybeam
