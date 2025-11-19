// Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include <iostream>

#include <boost/test/unit_test.hpp>
#include <boost/test/tools/floating_point_comparison.hpp>

#include "config.h"
#include "../msreadutils.h"

using everybeam::AartfaacElement;
using everybeam::Element;
using everybeam::MakeLocalEastNorthUpElement;
using everybeam::vector3r_t;

void check_vector(const vector3r_t& vec1, const vector3r_t& vec2,
                  double tolerance) {
  BOOST_CHECK(std::fabs(vec1[0] - vec2[0]) < tolerance);
  BOOST_CHECK(std::fabs(vec1[1] - vec2[1]) < tolerance);
  BOOST_CHECK(std::fabs(vec1[2] - vec2[2]) < tolerance);
}

BOOST_AUTO_TEST_SUITE(tmsreadutils)

BOOST_AUTO_TEST_CASE(make_local_east_north_up_element) {
  // MakeLocalEastNorthUp creates an element with a coordinate system (east,
  // north, up) based on the position found the MS AartfaacElement reads de
  // coordinate system from the MS The coordinate system in the MS is not
  // necessarily exactly the same as the local east, north, up, because the
  // ground plane can be slightly tilted to make it parallel to the ground plane
  // of a nearby station. The difference is small, so to check that
  // DefaultElement creates a reasonable coordinate system, the coordinate
  // system created for an Aartfaac element is compared to the coordinate system
  // in the Aartfaac ms.

  casacore::MeasurementSet ms(AARTFAAC_6_LBA_MOCK_MS);

  const size_t station_id = 0;
  const size_t element_id = 0;
  std::shared_ptr<Element> aartfaac_element =
      AartfaacElement(ms, station_id, element_id);
  std::shared_ptr<Element> local_east_north_up_element =
      MakeLocalEastNorthUpElement(ms, station_id);

  const double tolerance = 1e-2;

  check_vector(aartfaac_element->GetCoordinateSystem().origin,
               local_east_north_up_element->GetCoordinateSystem().origin,
               tolerance);

  check_vector(aartfaac_element->GetCoordinateSystem().axes.p,
               local_east_north_up_element->GetCoordinateSystem().axes.p,
               tolerance);

  check_vector(aartfaac_element->GetCoordinateSystem().axes.q,
               local_east_north_up_element->GetCoordinateSystem().axes.q,
               tolerance);

  check_vector(aartfaac_element->GetCoordinateSystem().axes.r,
               local_east_north_up_element->GetCoordinateSystem().axes.r,
               tolerance);
}

BOOST_AUTO_TEST_SUITE_END()
