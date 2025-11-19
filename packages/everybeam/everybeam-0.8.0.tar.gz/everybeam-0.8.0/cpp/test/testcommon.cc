// Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "testcommon.h"

#include <boost/test/unit_test.hpp>

namespace everybeam::test {

void CheckCoordinateSystem(const StationCoordinateSystem& left,
                           const StationCoordinateSystem& right) {
  CheckElementsClose(left.origin, right.origin, 1.0e-6);
  CheckElementsClose(left.axes.p, right.axes.p, 1.0e-6);
  CheckElementsClose(left.axes.q, right.axes.q, 1.0e-6);
  CheckElementsClose(left.axes.r, right.axes.r, 1.0e-6);
}

}  // namespace everybeam::test
