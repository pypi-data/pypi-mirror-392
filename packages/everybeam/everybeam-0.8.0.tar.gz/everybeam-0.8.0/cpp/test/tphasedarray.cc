// Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "../telescope/phasedarray.h"

#include <boost/test/unit_test.hpp>

using everybeam::Station;
using everybeam::telescope::PhasedArray;

namespace {
const std::vector<std::string> kStationNames{"station0", "station1"};
const std::vector<everybeam::vector3r_t> kStationPositions{{1.0, 2.0, 3.0},
                                                           {4.0, 5.0, 6.0}};
const everybeam::Options kOptions{
    .element_response_model = everybeam::ElementResponseModel::kOSKARDipole,
};

std::vector<std::unique_ptr<Station>> CreateStations() {
  std::vector<std::unique_ptr<Station>> stations;
  stations.push_back(std::make_unique<Station>(kStationNames[0],
                                               kStationPositions[0], kOptions));
  stations.push_back(std::make_unique<Station>(kStationNames[1],
                                               kStationPositions[1], kOptions));
  return stations;
}
}  // namespace

BOOST_AUTO_TEST_SUITE(phased_array)

BOOST_AUTO_TEST_CASE(constructor_stations) {
  PhasedArray phased_array(CreateStations(), kOptions);

  BOOST_REQUIRE_EQUAL(phased_array.GetNrStations(), kStationNames.size());
  BOOST_CHECK_EQUAL(phased_array.GetStation(0).GetName(), kStationNames[0]);
  BOOST_CHECK_EQUAL(phased_array.GetStation(1).GetName(), kStationNames[1]);
  BOOST_CHECK(phased_array.GetStation(0).GetPosition() == kStationPositions[0]);
  BOOST_CHECK(phased_array.GetStation(1).GetPosition() == kStationPositions[1]);
}

BOOST_AUTO_TEST_CASE(process_time_change) {
  /** PhasedArray subclass which exposes ProcessTimeChange for testing. */
  class TestPhasedArray : public PhasedArray {
   public:
    using PhasedArray::PhasedArray;
    using PhasedArray::ProcessTimeChange;
  };

  TestPhasedArray phased_array(CreateStations(), kOptions);
  for (std::size_t i = 0; i < kStationPositions.size(); ++i) {
    BOOST_CHECK_LT(phased_array.GetStation(i).GetTime(), 0.0);
  }

  const double kTime = 42.0;
  phased_array.ProcessTimeChange(kTime);
  for (std::size_t i = 0; i < kStationPositions.size(); ++i) {
    BOOST_CHECK_EQUAL(phased_array.GetStation(i).GetTime(), kTime);
  }
}

BOOST_AUTO_TEST_SUITE_END()
