// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "../load.h"

#include <boost/test/data/test_case.hpp>
#include <boost/test/unit_test.hpp>

#include "../common/casautils.h"
#include "../telescope/oskar.h"

using everybeam::ElementResponseModel;

BOOST_AUTO_TEST_SUITE(load)

BOOST_DATA_TEST_CASE(
    create_oskar_telescope,
    boost::unit_test::data::make(ElementResponseModel::kOSKARDipole,
                                 ElementResponseModel::kOSKARSphericalWave,
                                 ElementResponseModel::kOSKARDipoleCos),
    element_response_model) {
  const everybeam::Options options{.element_response_model =
                                       element_response_model};
  const everybeam::StationNode kEmptyStationTree;
  const double kDelayRa = 0.75;
  const double kDelayDec = -0.5;
  const std::vector<std::array<double, 2>> kDelayDirections = {
      {kDelayRa, kDelayDec}};
  const casacore::Vector<double> kDelayDirectionVector =
      everybeam::common::RaDecToDirection(kDelayRa, kDelayDec)
          .getValue()
          .getValue();

  std::unique_ptr<everybeam::telescope::Telescope> telescope =
      everybeam::CreateTelescope(options, kEmptyStationTree, kDelayDirections);

  BOOST_CHECK(telescope->GetOptions().element_response_model ==
              element_response_model);
  BOOST_CHECK_EQUAL(telescope->GetNrStations(), 0);

  auto oskar_telescope =
      dynamic_cast<everybeam::telescope::OSKAR*>(telescope.get());
  BOOST_REQUIRE(oskar_telescope);

  const casacore::Vector<double> oskar_delay_direction_vector =
      oskar_telescope->GetDelayDirection().getValue().getValue();
  BOOST_CHECK_EQUAL_COLLECTIONS(
      oskar_delay_direction_vector.begin(), oskar_delay_direction_vector.end(),
      kDelayDirectionVector.begin(), kDelayDirectionVector.end());
}

BOOST_AUTO_TEST_SUITE_END()
