"""Tests for StationCoordinateSystem and StationNode Python bindings"""

import numpy as np
import pytest

import everybeam


class TestStationCoordinateSystem:
    """Tests for StationCoordinateSystem bindings"""

    def test_default_constructor(self):
        """Test default constructor creates identity coordinate system"""
        coord_sys = everybeam.StationCoordinateSystem()

        # Check origin is at zero.
        origin = coord_sys.origin
        np.testing.assert_array_equal(origin, [0.0, 0.0, 0.0])

        # Check axes have identity values.
        np.testing.assert_array_equal(coord_sys.axes.p, [1.0, 0.0, 0.0])
        np.testing.assert_array_equal(coord_sys.axes.q, [0.0, 1.0, 0.0])
        np.testing.assert_array_equal(coord_sys.axes.r, [0.0, 0.0, 1.0])

    def test_custom_constructor(self):
        """Test constructor with custom origin and axes."""
        origin = np.array([1.0e6, 2.0e6, 3.0e6])
        axes = everybeam.StationCoordinateSystemAxes()
        axes.p = np.array([0.0, 1.0, 0.0])
        axes.q = np.array([0.0, 0.0, 1.0])
        axes.r = np.array([1.0, 0.0, 0.0])

        coord_sys = everybeam.StationCoordinateSystem(origin, axes)

        # Verify origin.
        np.testing.assert_array_equal(coord_sys.origin, origin)

        # Verify axes.
        np.testing.assert_array_equal(coord_sys.axes.p, [0.0, 1.0, 0.0])
        np.testing.assert_array_equal(coord_sys.axes.q, [0.0, 0.0, 1.0])
        np.testing.assert_array_equal(coord_sys.axes.r, [1.0, 0.0, 0.0])

    def test_numpy_constructor(self):
        """Test constructor with numpy arrays for origin and axes."""
        origin = np.array([1.0e6, 2.0e6, 3.0e6])
        axes = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]])
        coord_sys = everybeam.StationCoordinateSystem(origin, axes)

        # Verify origin.
        np.testing.assert_array_equal(coord_sys.origin, origin)

        # Verify axes.
        np.testing.assert_array_equal(coord_sys.axes.p, [0.0, 1.0, 0.0])
        np.testing.assert_array_equal(coord_sys.axes.q, [0.0, 0.0, 1.0])
        np.testing.assert_array_equal(coord_sys.axes.r, [1.0, 0.0, 0.0])

    def test_axes_properties(self):
        """Test setting and getting axes properties"""
        axes = everybeam.StationCoordinateSystemAxes()

        # Set axes
        p_axis = np.array([0.0, 0.0, 1.0])
        q_axis = np.array([1.0, 0.0, 0.0])
        r_axis = np.array([0.0, 1.0, 0.0])

        axes.p = p_axis
        axes.q = q_axis
        axes.r = r_axis

        # Verify axes
        np.testing.assert_array_equal(axes.p, p_axis)
        np.testing.assert_array_equal(axes.q, q_axis)
        np.testing.assert_array_equal(axes.r, r_axis)

    def test_static_members(self):
        """Test access to static members"""
        identity_axes = everybeam.StationCoordinateSystem.identity_axes
        np.testing.assert_array_equal(identity_axes.p, [1.0, 0.0, 0.0])
        np.testing.assert_array_equal(identity_axes.q, [0.0, 1.0, 0.0])
        np.testing.assert_array_equal(identity_axes.r, [0.0, 0.0, 1.0])

        zero_origin = everybeam.StationCoordinateSystem.zero_origin
        np.testing.assert_array_equal(zero_origin, [0.0, 0.0, 0.0])

    def test_global_identity_coordinate_system(self):
        """Test access to global identity coordinate system"""
        identity_coord_sys = everybeam.identity_coordinate_system

        # Check origin
        np.testing.assert_array_equal(
            identity_coord_sys.origin, [0.0, 0.0, 0.0]
        )

        # Check axes
        np.testing.assert_array_equal(
            identity_coord_sys.axes.p, [1.0, 0.0, 0.0]
        )
        np.testing.assert_array_equal(
            identity_coord_sys.axes.q, [0.0, 1.0, 0.0]
        )
        np.testing.assert_array_equal(
            identity_coord_sys.axes.r, [0.0, 0.0, 1.0]
        )

    def test_invalid_array_size(self):
        """Test that invalid array sizes raise exceptions"""
        axes = everybeam.StationCoordinateSystemAxes()

        # Should raise exception for wrong array size
        with pytest.raises(RuntimeError, match="Array must have size 3"):
            axes.p = np.array([1.0, 0.0])  # Only 2 elements

        with pytest.raises(RuntimeError, match="Array must have size 3"):
            axes.q = np.array([1.0, 0.0, 0.0, 0.0])  # 4 elements


class TestStationNode:
    """Test cases for StationNode bindings"""

    def test_default_constructor(self):
        """Test default constructor"""
        node = everybeam.StationNode()

        assert node.get_name() == ""
        assert len(node) == 0
        assert len(node.get_children()) == 0
        assert len(node.get_child_positions()) == 0

    def test_named_constructor(self):
        """Test constructor with name"""
        node = everybeam.StationNode(name="TestStation")

        assert node.get_name() == "TestStation"
        assert len(node) == 0

    def test_coordinate_system_constructor(self):
        """Test constructor with coordinate system"""
        origin = np.array([1000.0, 2000.0, 3000.0])
        coord_sys = everybeam.StationCoordinateSystem(
            origin, everybeam.StationCoordinateSystem.identity_axes
        )

        node = everybeam.StationNode(coord_sys, "TestStation")

        assert node.get_name() == "TestStation"
        retrieved_coord_sys = node.get_coordinate_system()
        np.testing.assert_array_equal(retrieved_coord_sys.origin, origin)

    def test_add_child_elements(self):
        """Test adding child elements to leaf node"""
        node = everybeam.StationNode(name="LeafNode")

        # Add elements with different polarization settings
        node.add_child_element(
            np.array([0.0, 0.0, 0.0]), True, True
        )  # Both enabled
        node.add_child_element(
            np.array([1.0, 0.0, 0.0]), True, False
        )  # X only
        node.add_child_element(
            np.array([0.0, 1.0, 0.0]), False, True
        )  # Y only
        node.add_child_element(
            np.array([1.0, 1.0, 0.0])
        )  # Default both enabled

        assert len(node) == 4
        assert len(node.get_children()) == 0  # No child nodes, just elements

        positions = node.get_child_positions()
        assert len(positions) == 4

        # Check positions
        np.testing.assert_array_equal(positions[0], [0.0, 0.0, 0.0])
        np.testing.assert_array_equal(positions[1], [1.0, 0.0, 0.0])
        np.testing.assert_array_equal(positions[2], [0.0, 1.0, 0.0])
        np.testing.assert_array_equal(positions[3], [1.0, 1.0, 0.0])

        # Check polarizations
        assert node.is_x_enabled(0) == True and node.is_y_enabled(0) == True
        assert node.is_x_enabled(1) == True and node.is_y_enabled(1) == False
        assert node.is_x_enabled(2) == False and node.is_y_enabled(2) == True
        assert node.is_x_enabled(3) == True and node.is_y_enabled(3) == True

    def test_add_child_nodes(self):
        """Test adding child nodes to intermediate node"""
        parent = everybeam.StationNode(name="Parent")

        # Create child nodes
        child1 = everybeam.StationNode(name="Child1")
        child2 = everybeam.StationNode(name="Child2")

        # Add some elements to children
        child1.add_child_element(np.array([0.0, 0.0, 0.0]))
        child2.add_child_element(np.array([0.0, 0.0, 0.0]))
        child2.add_child_element(np.array([1.0, 0.0, 0.0]))

        # Add children to parent
        parent.add_child_node(child1, np.array([10.0, 0.0, 0.0]))
        parent.add_child_node(child2, np.array([20.0, 0.0, 0.0]))

        assert len(parent) == 2
        children = parent.get_children()
        assert len(children) == 2
        assert children[0].get_name() == "Child1"
        assert children[1].get_name() == "Child2"

        positions = parent.get_child_positions()
        np.testing.assert_array_equal(positions[0], [10.0, 0.0, 0.0])
        np.testing.assert_array_equal(positions[1], [20.0, 0.0, 0.0])

    def test_mixed_add_child_error(self):
        """Test that mixing add_child_node and add_child_element raises errors"""
        node = everybeam.StationNode(name="TestNode")

        # First add an element
        node.add_child_element(np.array([0.0, 0.0, 0.0]))

        # Now trying to add a child node should fail
        child = everybeam.StationNode(name="Child")
        with pytest.raises(
            RuntimeError,
            match="Leaf station node does not support adding child nodes",
        ):
            node.add_child_node(child, np.array([1.0, 1.0, 1.0]))

        # Test the reverse: add child node first, then try to add element
        node2 = everybeam.StationNode(name="TestNode2")
        child2 = everybeam.StationNode(name="Child2")
        node2.add_child_node(child2, np.array([0.0, 0.0, 0.0]))

        with pytest.raises(
            RuntimeError,
            match="Intermediate station node does not support adding leaf children",
        ):
            node2.add_child_element(np.array([1.0, 1.0, 1.0]))

    def test_hierarchical_structure(self):
        """Test creating and accessing a multi-level hierarchy"""
        # Create station
        station = everybeam.StationNode(name="Station")

        # Create fields
        field1 = everybeam.StationNode(name="Field1")
        field2 = everybeam.StationNode(name="Field2")

        # Add elements to fields
        for i in range(3):
            field1.add_child_element(np.array([i * 1.0, 0.0, 0.0]))
            field2.add_child_element(np.array([i * 2.0, 0.0, 0.0]))

        # Add fields to station
        station.add_child_node(field1, np.array([0.0, 0.0, 0.0]))
        station.add_child_node(field2, np.array([50.0, 0.0, 0.0]))

        # Verify structure
        assert len(station) == 2  # 2 fields
        assert len(field1) == 3  # 3 elements each
        assert len(field2) == 3

        # Verify we can navigate the hierarchy
        fields = station.get_children()
        assert fields[0].get_name() == "Field1"
        assert fields[1].get_name() == "Field2"

        field1_positions = fields[0].get_child_positions()
        assert len(field1_positions) == 3
        np.testing.assert_array_equal(field1_positions[0], [0.0, 0.0, 0.0])
        np.testing.assert_array_equal(field1_positions[1], [1.0, 0.0, 0.0])
        np.testing.assert_array_equal(field1_positions[2], [2.0, 0.0, 0.0])

    def test_string_representation(self):
        """Test string representation of objects"""
        node = everybeam.StationNode(name="TestRepr")
        node.add_child_element(np.array([0.0, 0.0, 0.0]))

        repr_str = repr(node)
        assert "TestRepr" in repr_str
        assert "children=1" in repr_str
