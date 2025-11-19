// Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "../common/casautils.h"

#include <boost/test/unit_test.hpp>

BOOST_AUTO_TEST_SUITE(casa_utils)

BOOST_AUTO_TEST_CASE(ra_dec_to_direction) {
  const double kRa = 1.0;
  const double kDec = -0.5;
  const std::array<double, 3> kExpectedValue = {
      0.4741598817790379, 0.73846026260412878, -0.47942553860420301};

  const casacore::MDirection direction =
      everybeam::common::RaDecToDirection(kRa, kDec);

  const casacore::Vector<double> value = direction.getValue().getValue();
  BOOST_REQUIRE_EQUAL(value.size(), kExpectedValue.size());
  for (std::size_t i = 0; i < kExpectedValue.size(); ++i) {
    BOOST_CHECK_CLOSE(value[i], kExpectedValue[i], 1.0e-6);
  }
  BOOST_CHECK(direction.getRef().getType() == casacore::MDirection::J2000);
}

BOOST_AUTO_TEST_SUITE_END()
