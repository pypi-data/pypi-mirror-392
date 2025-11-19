// Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "../stationnode.h"

#include <boost/test/unit_test.hpp>

#include "testcommon.h"

using everybeam::StationCoordinateSystem;
using everybeam::StationNode;
using everybeam::test::CheckCoordinateSystem;

BOOST_AUTO_TEST_SUITE(station_node)

BOOST_AUTO_TEST_CASE(constructor_default) {
  const StationNode node;
  BOOST_CHECK(node.GetChildren().empty());
  BOOST_CHECK(node.GetChildPositions().empty());
  CheckCoordinateSystem(node.GetCoordinateSystem(),
                        everybeam::kIdentityCoordinateSystem);
  BOOST_CHECK_EQUAL(node.GetName(), "");
}

BOOST_AUTO_TEST_CASE(constructor_custom_parameters) {
  const std::array<double, 3> kOrigin{1.0, 2.0, 3.0};
  const StationCoordinateSystem::Axes kAxes{
      {0.5, 1.0, 0.1}, {1.0, -0.1, 0.2}, {0.2, -0.3, -1.0}};
  const StationCoordinateSystem kCoordinateSystem{kOrigin, kAxes};
  const std::string kName = "Custom Name";
  const StationNode node(kCoordinateSystem, kName);
  BOOST_CHECK(node.GetChildren().empty());
  BOOST_CHECK(node.GetChildPositions().empty());
  CheckCoordinateSystem(node.GetCoordinateSystem(), kCoordinateSystem);
  BOOST_CHECK_EQUAL(node.GetName(), kName);
}

BOOST_AUTO_TEST_CASE(add_leaf_children) {
  StationNode leaf;
  std::array<double, 3> kPosition1{1.0, 2.0, 3.0};
  std::array<double, 3> kPosition2{4.0, 5.0, 6.0};
  leaf.AddChild(kPosition1, true, false);
  leaf.AddChild(kPosition2, false, true);
  BOOST_CHECK(leaf.GetChildren().empty());
  BOOST_REQUIRE_EQUAL(leaf.GetChildPositions().size(), 2);
  BOOST_CHECK(leaf.GetChildPositions()[0] == kPosition1);
  BOOST_CHECK(leaf.GetChildPositions()[1] == kPosition2);
  BOOST_CHECK_EQUAL(leaf.IsXEnabled(0), true);
  BOOST_CHECK_EQUAL(leaf.IsYEnabled(0), false);
  BOOST_CHECK_EQUAL(leaf.IsXEnabled(1), false);
  BOOST_CHECK_EQUAL(leaf.IsYEnabled(1), true);
}

BOOST_AUTO_TEST_CASE(add_child_node) {
  StationNode parent;

  const std::array<double, 3> kChildOrigin{1.0, 2.0, 3.0};
  const StationCoordinateSystem::Axes kChildAxes{
      {0.5, 1.0, 0.1}, {1.0, -0.1, 0.2}, {0.2, -0.3, -1.0}};
  const StationCoordinateSystem kChildCoordinateSystem{kChildOrigin,
                                                       kChildAxes};
  const std::array<double, 3> kChildChildPosition{7.0, 8.0, 9.0};

  StationNode child(kChildCoordinateSystem);
  child.AddChild(kChildChildPosition);
  const auto child_position_iterator = child.GetChildPositions().begin();

  const std::array<double, 3> kChildPosition{1.0, 2.0, 3.0};
  parent.AddChild(std::move(child), kChildPosition);
  BOOST_CHECK_EQUAL(parent.GetChildren().size(), 1);
  BOOST_REQUIRE_EQUAL(parent.GetChildPositions().size(), 1);
  BOOST_CHECK(parent.GetChildPositions()[0] == kChildPosition);
  BOOST_CHECK_EQUAL(parent.IsXEnabled(0), true);
  BOOST_CHECK_EQUAL(parent.IsYEnabled(0), true);

  const StationNode& child_in_parent = parent.GetChildren()[0];
  CheckCoordinateSystem(child_in_parent.GetCoordinateSystem(),
                        kChildCoordinateSystem);
  BOOST_REQUIRE_EQUAL(child_in_parent.GetChildPositions().size(), 1);
  BOOST_CHECK(child_in_parent.GetChildPositions()[0] == kChildChildPosition);
  BOOST_CHECK_EQUAL(child_in_parent.IsXEnabled(0), true);
  BOOST_CHECK_EQUAL(child_in_parent.IsYEnabled(0), true);
  // Check move semantics. The child's iterator should remain equal.
  BOOST_CHECK(parent.GetChildren()[0].GetChildPositions().begin() ==
              child_position_iterator);
}

BOOST_AUTO_TEST_CASE(add_child_node_throws_on_leaf) {
  StationNode leaf;
  leaf.AddChild({1.0, 2.0, 3.0});
  StationNode child;
  BOOST_CHECK_THROW(leaf.AddChild(std::move(child), {4.0, 5.0, 6.0}),
                    std::logic_error);
}

BOOST_AUTO_TEST_CASE(add_child_position_throws_on_intermediate) {
  StationNode parent;
  StationNode child;
  parent.AddChild(std::move(child), {1.0, 2.0, 3.0});
  BOOST_CHECK_THROW(parent.AddChild({4.0, 5.0, 6.0}), std::logic_error);
}

BOOST_AUTO_TEST_CASE(multiple_intermediate_children) {
  StationNode parent;
  StationNode child1;
  StationNode child2;
  std::array<double, 3> kPosition1{1.0, 2.0, 3.0};
  std::array<double, 3> kPosition2{4.0, 5.0, 6.0};
  parent.AddChild(std::move(child1), kPosition1);
  parent.AddChild(std::move(child2), kPosition2);
  BOOST_CHECK_EQUAL(parent.GetChildren().size(), 2);
  BOOST_CHECK_EQUAL(parent.GetChildPositions().size(), 2);
  BOOST_CHECK(parent.GetChildPositions()[0] == kPosition1);
  BOOST_CHECK(parent.GetChildPositions()[1] == kPosition2);
}

BOOST_AUTO_TEST_SUITE_END()
