// Copyright (C) 2022 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include <boost/test/unit_test.hpp>

#include "../load.h"
#include "../pointresponse/phasedarraypoint.h"

#include "config.h"

BOOST_AUTO_TEST_SUITE(tphasedarraypoint)

BOOST_AUTO_TEST_CASE(use_local_coordinate_system) {
  everybeam::Options options;
  casacore::MeasurementSet ms(LOFAR_LBA_MOCK_MS);
  std::unique_ptr<everybeam::telescope::Telescope> telescope =
      everybeam::Load(ms, options);
  auto phased_array =
      dynamic_cast<everybeam::telescope::PhasedArray*>(telescope.get());
  BOOST_REQUIRE(phased_array);

  everybeam::pointresponse::PhasedArrayPoint point(*phased_array, 0.0);
  BOOST_CHECK_EQUAL(point.GetUseLocalCoordinateSystem(), false);

  point.SetUseLocalCoordinateSystem(true);
  BOOST_CHECK_EQUAL(point.GetUseLocalCoordinateSystem(), true);

  point.SetUseLocalCoordinateSystem(false);
  BOOST_CHECK_EQUAL(point.GetUseLocalCoordinateSystem(), false);
}

BOOST_AUTO_TEST_SUITE_END()
