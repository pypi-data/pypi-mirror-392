// Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

// Common utility functions for EveryBeam tests.
#ifndef EVERYBEAM_TESTCOMMON_H_
#define EVERYBEAM_TESTCOMMON_H_

#include <boost/test/unit_test.hpp>

#include "../stationnode.h"

namespace everybeam::test {

template <typename T>
void CheckElementsClose(const T& left, const T& right, double tolerance) {
  BOOST_REQUIRE_EQUAL(left.size(), right.size());
  for (std::size_t i = 0; i < left.size(); ++i) {
    BOOST_CHECK_CLOSE(left[i], right[i], tolerance);
  }
}

void CheckCoordinateSystem(const StationCoordinateSystem& left,
                           const StationCoordinateSystem& right);

}  // namespace everybeam::test

#endif  // EVERYBEAM_TESTCOMMON_H_
