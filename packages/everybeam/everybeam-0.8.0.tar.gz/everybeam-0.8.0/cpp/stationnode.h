// Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_STATIONNODE_H_
#define EVERYBEAM_STATIONNODE_H_

#include <array>
#include <cassert>
#include <stdexcept>
#include <vector>

namespace everybeam {

/**
 *  \brief %Station coordinate system.
 *
 *  A right handed, cartesian, local coordinate system with coordinate axes
 *  \p p, \p q, and \p r is associated with each antenna field.
 *
 *  The r-axis is orthogonal to the antenna field, and points towards the
 *  local pseudo zenith.
 *
 *  The q-axis is the northern bisector of the \p X and \p Y dipoles, i.e.
 *  it is the reference direction from which the orientation of the dual
 *  dipole antennae is determined. The q-axis points towards the North at
 *  the core. At remote sites it is defined as the intersection of the
 *  antenna field plane and a plane parallel to the meridian plane at the
 *  core. This ensures the reference directions at all sites are similar.
 *
 *  The p-axis is orthogonal to both other axes, and points towards the East
 *  at the core.
 *
 *  The axes and origin of the antenna field coordinate system are expressed
 *  as vectors in the geocentric, cartesian, ITRF coordinate system, in
 *  meters.
 *
 *  \sa "LOFAR Reference Plane and Reference Direction", M.A. Brentjens,
 *  LOFAR-ASTRON-MEM-248.
 */
struct [[gnu::visibility("default")]] StationCoordinateSystem {
  struct Axes {
    std::array<double, 3> p;
    std::array<double, 3> q;
    std::array<double, 3> r;
  };
  std::array<double, 3> origin = kZeroOrigin;
  Axes axes = kIdentityAxes;

  constexpr static Axes kIdentityAxes =
      Axes{{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}};

  constexpr static std::array<double, 3> kZeroOrigin = {0.0, 0.0, 0.0};
};

constexpr static StationCoordinateSystem kIdentityCoordinateSystem;

/**
 * Tree structure for a station and its elements.
 *
 * Each node holds a list with the positions of its child nodes, relative
 * to the current node.
 *
 * The top-most node in the tree has no position value, since it always
 * has a position of (0, 0, 0) relative to itself.
 */
class [[gnu::visibility("default")]] StationNode {
 public:
  /**
   * Creates an object of the station tree.
   * @param coordinate_system The coordinate system for positions of children
   * of this node. If omitted, use an identity coordinate system.
   * @param name Optional name, which is typically used for nodes representing
   * stations. Some telescopes, e.g., LOFAR, use this name for selecting the
   * correct element response coefficients.
   */
  StationNode(const StationCoordinateSystem& coordinate_system =
                  kIdentityCoordinateSystem,
              const std::string& name = "")
      : children_(),
        child_positions_(),
        child_enabled_(),
        coordinate_system_(coordinate_system),
        name_(name) {}

  /**
   * @brief Adds a child node to an intermedate node in the tree.
   *
   * Calls to both AddChild overloads may not be mixed!
   *
   * @param child The child to add (rvalue reference, will be moved).
   * @param position The (center) position of the child, relative to the current
   * node, in ITRF format: (x, y, z) in meters.
   *
   * @throws std::logic_error If the node is a leaf node, which does not
   * support adding child nodes.
   */
  void AddChild(StationNode && child, std::array<double, 3> position) {
    if (!child_positions_.empty() && children_.empty()) {
      throw std::logic_error(
          "Leaf station node does not support adding child nodes.");
    }
    assert(child_enabled_.empty());
    children_.push_back(std::move(child));
    child_positions_.push_back(std::move(position));
  }

  /**
   * @brief Adds a child to a leaf node in the tree.
   *
   * Calls to both AddChild overloads may not be mixed!
   *
   * @param position The (center) position of the child, relative to the current
   * node, in ITRF format: (x, y, z) in meters.
   * @param is_x_enabled Whether the X polarization is enabled for the child.
   * @param is_y_enabled Whether the Y polarization is enabled for the child.
   *
   * @throws std::logic_error If the node is an intermediate node, which does
   * not support adding children by only specifying the position.
   */
  void AddChild(std::array<double, 3> position, bool is_x_enabled = true,
                bool is_y_enabled = true) {
    if (!children_.empty()) {
      throw std::logic_error(
          "Intermediate station node does not support adding leaf children.");
    }
    child_positions_.push_back(std::move(position));
    child_enabled_.emplace_back(is_x_enabled, is_y_enabled);
  }

  /**
   * @return The element's children. The list is empty if the element is a leaf
   * object in the element tree.
   */
  const std::vector<StationNode>& GetChildren() const { return children_; }

  /**
   * @return The positions of the element's children, relative to the current
   * element.
   */
  const std::vector<std::array<double, 3>>& GetChildPositions() const {
    return child_positions_;
  }

  /**
   * @return The coordinate system for this element, used for child positions.
   */
  const StationCoordinateSystem& GetCoordinateSystem() const {
    return coordinate_system_;
  }

  /** @return The name of the station node. */
  const std::string& GetName() const { return name_; }

  /**
   * @param child Child index, between 0 and GetChildPositions().size() - 1.
   * @return Whether the X polarization is enabled for the given child index.
   */
  bool IsXEnabled(std::size_t child) const {
    return child_enabled_.empty() ? true : child_enabled_[child].first;
  }
  /**
   * @param child Child index, between 0 and GetChildPositions().size() - 1.
   * @return Whether the Y polarization is enabled for the given child index.
   */
  bool IsYEnabled(std::size_t child) const {
    return child_enabled_.empty() ? true : child_enabled_[child].second;
  }

 private:
  /**
   * The child elements of this element.
   * For leaf objects, this vector is empty.
   * For non-leaf objects, the length is equal to child_positions_.
   */
  std::vector<StationNode> children_;

  /**
   * Positions of the element's children, relative to the current object.
   * These positions are in the coordinate_system_ of the current object.
   */
  std::vector<std::array<double, 3>> child_positions_;

  /**
   * Whether the X and Y polarizations are enabled for the children.
   *
   * This vector is only used for leaf nodes, for enabling/disabling the X and Y
   * polarizations of individual elements at the bottom of the StationNode tree.
   *
   * For non-leaf nodes, the vector is always empty. Both polarizations are
   * always enabled at intermediate nodes.
   */
  std::vector<std::pair<bool, bool>> child_enabled_;

  /** The coordinate system for the current object, used for child positions.*/
  StationCoordinateSystem coordinate_system_;

  /**
   * Optional name of the station node. Some telescopes, e.g., LOFAR, use
   * this name for selecting the correct element response coefficients.
   */
  std::string name_;
};

}  // namespace everybeam

#endif
