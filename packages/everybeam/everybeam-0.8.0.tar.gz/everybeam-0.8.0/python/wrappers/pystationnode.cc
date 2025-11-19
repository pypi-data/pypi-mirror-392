// Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "stationnode.h"

namespace py = pybind11;
using everybeam::kIdentityCoordinateSystem;
using everybeam::StationCoordinateSystem;
using everybeam::StationNode;

namespace {
// Convert Python list of size 3 to std::array<double, 3>
std::array<double, 3> py_to_array3(const py::array_t<double>& pyarray) {
  auto r = pyarray.unchecked<1>();
  if (r.size() != 3) {
    throw std::runtime_error("Array must have size 3, got size " +
                             std::to_string(r.size()));
  }
  return {r[0], r[1], r[2]};
}

}  // namespace

void InitStationNode(py::module& m) {
  // Bind StationCoordinateSystem::Axes
  py::class_<StationCoordinateSystem::Axes>(m, "StationCoordinateSystemAxes",
                                            R"pbdoc(
    Coordinate system axes for a station.

    Contains the p, q, and r axes as 3-element arrays representing unit vectors
    in the geocentric ITRF coordinate system.
  )pbdoc")
      .def(py::init(), "Default constructor")
      .def_property(
          "p", [](const StationCoordinateSystem::Axes& self) { return self.p; },
          [](StationCoordinateSystem::Axes& self, py::array_t<double> p) {
            self.p = py_to_array3(p);
          },
          "p-axis (unit vector in the station plane defining one polarization)")
      .def_property(
          "q", [](const StationCoordinateSystem::Axes& self) { return self.q; },
          [](StationCoordinateSystem::Axes& self, py::array_t<double> q) {
            self.q = py_to_array3(q);
          },
          "q-axis (unit vector in the station plane perpendicular to p-axis)")
      .def_property(
          "r", [](const StationCoordinateSystem::Axes& self) { return self.r; },
          [](StationCoordinateSystem::Axes& self, py::array_t<double> r) {
            self.r = py_to_array3(r);
          },
          "r-axis (unit vector perpendicular to the station plane)")
      .def("__repr__", [](const StationCoordinateSystem::Axes& self) {
        return "<StationCoordinateSystemAxes p=[" + std::to_string(self.p[0]) +
               ", " + std::to_string(self.p[1]) + ", " +
               std::to_string(self.p[2]) + "] " + "q=[" +
               std::to_string(self.q[0]) + ", " + std::to_string(self.q[1]) +
               ", " + std::to_string(self.q[2]) + "] " + "r=[" +
               std::to_string(self.r[0]) + ", " + std::to_string(self.r[1]) +
               ", " + std::to_string(self.r[2]) + "]>";
      });

  // Bind StationCoordinateSystem
  py::class_<StationCoordinateSystem>(m, "StationCoordinateSystem", R"pbdoc(
    Station coordinate system.

    A right-handed, cartesian, local coordinate system with coordinate axes
    p, q, and r associated with each antenna field.

    The r-axis is orthogonal to the antenna field, and points towards the
    local pseudo zenith.

    The q-axis is the northern bisector of the X and Y dipoles, i.e.
    it is the reference direction from which the orientation of the dual
    dipole antennae is determined.

    The p-axis is orthogonal to both other axes, and points towards the East
    at the core.

    The axes and origin are expressed as vectors in the geocentric, cartesian,
    ITRF coordinate system, in meters.
  )pbdoc")
      .def(py::init<>(), "Default constructor with identity coordinate system")
      .def(py::init<std::array<double, 3>, StationCoordinateSystem::Axes>(),
           "Constructor with origin and axes", py::arg("origin"),
           py::arg("axes"))
      .def(py::init([](const py::array_t<double>& py_origin,
                       const py::array_t<double>& py_axes) {
             if (py_origin.ndim() != 1 || py_origin.shape(0) != 3) {
               throw std::invalid_argument(
                   "Origin must be a 1-D array of size 3.");
             }
             if (py_axes.ndim() != 2 || py_axes.shape(0) != 3 ||
                 py_axes.shape(1) != 3) {
               throw std::invalid_argument(
                   "Axes must be a 2-D array of shape (3, 3).");
             }
             auto r = py_axes.unchecked<2>();
             return StationCoordinateSystem{
                 .origin = py_to_array3(py_origin),
                 .axes = {.p = {r(0, 0), r(0, 1), r(0, 2)},
                          .q = {r(1, 0), r(1, 1), r(1, 2)},
                          .r = {r(2, 0), r(2, 1), r(2, 2)}}};
           }),
           "Constructor with origin and coordinate axes in NumPy arrays",
           py::arg("origin"), py::arg("axes"))
      .def_property(
          "origin",
          [](const StationCoordinateSystem& self) { return self.origin; },
          [](StationCoordinateSystem& self, py::array_t<double> origin) {
            self.origin = py_to_array3(origin);
          },
          "Origin of the coordinate system in ITRF coordinates (meters)")
      .def_readwrite("axes", &StationCoordinateSystem::axes,
                     "Coordinate system axes")
      .def_readonly_static("identity_axes",
                           &StationCoordinateSystem::kIdentityAxes,
                           "Identity axes (unit vectors along x, y, z)")
      .def_readonly_static("zero_origin", &StationCoordinateSystem::kZeroOrigin,
                           "Zero origin (0, 0, 0)")
      .def("__repr__", [](const StationCoordinateSystem& self) {
        return "<StationCoordinateSystem origin=[" +
               std::to_string(self.origin[0]) + ", " +
               std::to_string(self.origin[1]) + ", " +
               std::to_string(self.origin[2]) + "], p_axis=[" +
               std::to_string(self.axes.p[0]) + ", " +
               std::to_string(self.axes.p[1]) + ", " +
               std::to_string(self.axes.p[2]) + "], q_axis=[" +
               std::to_string(self.axes.q[0]) + ", " +
               std::to_string(self.axes.q[1]) + ", " +
               std::to_string(self.axes.q[2]) + "], r_axis=[" +
               std::to_string(self.axes.r[0]) + ", " +
               std::to_string(self.axes.r[1]) + ", " +
               std::to_string(self.axes.r[2]) + "]>";
      });

  // Bind the global identity coordinate system
  m.attr("identity_coordinate_system") = py::cast(kIdentityCoordinateSystem);

  // Bind StationNode
  py::class_<StationNode>(m, "StationNode", R"pbdoc(
    Tree structure for a station and its elements.

    Each node holds a list with the positions of its child nodes, relative
    to the current node.

    The top-most node in the tree has no position value, since it always
    has a position of (0, 0, 0) relative to itself.
  )pbdoc")
      .def(py::init<const StationCoordinateSystem&, const std::string&>(),
           "Constructor with coordinate system and name",
           py::arg("coordinate_system") = kIdentityCoordinateSystem,
           py::arg("name") = "")
      .def(
          "add_child_node",
          [](StationNode& self, const StationNode& child,
             py::array_t<double> position) {
            StationNode child_copy =
                child;  // Make a copy since we need to move
            self.AddChild(std::move(child_copy), py_to_array3(position));
          },
          "Add a child node to an intermediate node in the tree",
          py::arg("child"), py::arg("position"))
      .def(
          "add_child_element",
          [](StationNode& self, py::array_t<double> position, bool is_x_enabled,
             bool is_y_enabled) {
            self.AddChild(py_to_array3(position), is_x_enabled, is_y_enabled);
          },
          "Add a child element to a leaf node in the tree", py::arg("position"),
          py::arg("is_x_enabled") = true, py::arg("is_y_enabled") = true)
      .def("get_children", &StationNode::GetChildren,
           "Get the element's children",
           py::return_value_policy::reference_internal)
      .def(
          "get_child_positions",
          [](const StationNode& self) {
            py::list result;
            for (const std::array<double, 3>& pos : self.GetChildPositions()) {
              result.append(pos);
            }
            return result;
          },
          "Get the positions of the element's children, relative to the "
          "current element")
      .def("get_coordinate_system", &StationNode::GetCoordinateSystem,
           "Get the coordinate system for this element, used for child "
           "positions",
           py::return_value_policy::reference_internal)
      .def("get_name", &StationNode::GetName,
           "Get the name of the station node",
           py::return_value_policy::reference_internal)
      .def("is_x_enabled", &StationNode::IsXEnabled,
           "Check if X polarization is enabled for the given child index",
           py::arg("child"))
      .def("is_y_enabled", &StationNode::IsYEnabled,
           "Check if Y polarization is enabled for the given child index",
           py::arg("child"))
      .def(
          "__len__",
          [](const StationNode& self) {
            return self.GetChildPositions().size();
          },
          "Get the number of children")
      .def("__repr__", [](const StationNode& self) {
        return "<StationNode name='" + self.GetName() + "' n_children=" +
               std::to_string(self.GetChildPositions().size()) + ">";
      });
}
