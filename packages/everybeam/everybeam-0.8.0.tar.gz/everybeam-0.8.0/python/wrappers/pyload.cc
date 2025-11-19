// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include <memory>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <casacore/ms/MeasurementSets/MeasurementSet.h>

#include "load.h"
#include "options.h"

using casacore::MeasurementSet;

using everybeam::BeamMode;
using everybeam::BeamNormalisationMode;
using everybeam::CreateTelescope;
using everybeam::GetTelescopeType;
using everybeam::Load;
using everybeam::StationNode;
using everybeam::telescope::Telescope;

namespace py = pybind11;

namespace {
// Converts a 1D or 2D numpy array with (ra, dec) direction values.
std::vector<std::array<double, 2>> ConvertDirections(
    const py::array_t<double>& py_array, const std::string& parameter_name) {
  std::vector<std::array<double, 2>> directions;
  if (py_array.ndim() == 1 && py_array.shape(0) == 2) {
    auto r = py_array.unchecked<1>();
    // Single direction given as 1D array with two elements
    directions.push_back({r(0), r(1)});
  } else if (py_array.ndim() == 2 && py_array.shape(1) == 2) {
    auto r = py_array.unchecked<2>();
    // Multiple directions given as 2D array with shape (N, 2)
    directions.reserve(py_array.shape(0));
    for (py::ssize_t i = 0; i < py_array.shape(0); ++i) {
      directions.push_back({r(i, 0), r(i, 1)});
    }
  } else {
    throw std::invalid_argument(parameter_name +
                                " must be a 1D array with two elements or a 2D "
                                "array with shape (N, 2)");
  }
  return directions;
}
}  // namespace

// Wrapper around the everybeam::Load method
std::unique_ptr<Telescope> pyload_telescope(
    const std::string& name, const std::string& data_column,
    BeamNormalisationMode beam_normalisation_mode, bool use_channel_frequency,
    const std::string& element_response_model, const std::string& coeff_path) {
  // Load measurement set
  MeasurementSet ms(name);

  const everybeam::TelescopeType telescope_type =
      everybeam::GetTelescopeType(ms);

  switch (telescope_type) {
    case everybeam::TelescopeType::kAARTFAAC:
    case everybeam::TelescopeType::kLofarTelescope:
    case everybeam::TelescopeType::kOSKARTelescope:
    case everybeam::TelescopeType::kSkaMidTelescope:
      break;
    default:
      throw std::runtime_error(
          "Currently the python bindings only support AARTFAAC (LBA), LOFAR, "
          "OSKAR (SKALA40) and SKA-MID observations");
  }

  // Fill everybeam options
  everybeam::Options options;

  options.element_response_model =
      everybeam::ElementResponseModelFromString(element_response_model);

  options.data_column_name = data_column;
  options.beam_normalisation_mode = beam_normalisation_mode;
  options.use_channel_frequency = use_channel_frequency;
  options.coeff_path = coeff_path;

  return Load(ms, options);
}

void init_load(py::module& m) {
  m.def(
      "load_telescope",
      [](const std::string& name, const std::string& data_column,
         bool use_differential_beam, bool use_channel_frequency,
         const std::string& element_response_model,
         const std::string& coeff_path = "") -> std::unique_ptr<Telescope> {
        BeamNormalisationMode beam_normalisation_mode =
            use_differential_beam ? BeamNormalisationMode::kPreApplied
                                  : BeamNormalisationMode::kNone;
        return pyload_telescope(name, data_column, beam_normalisation_mode,
                                use_channel_frequency, element_response_model,
                                coeff_path);
      },
      R"pbdoc(
        Load telescope from measurement set (MS)

        This version has a simple on/off toggle for beam normalisation through
        the use_differential_beam parameter

        Parameters
        ----------
        name: str
            Path to MS
        data_column: str, optional
            Data column that should
        use_differential_beam: bool, optional
            Use differential beam? Defaults to False
        use_channel_frequency: bool, optional
            Use channel frequency? Defaults to True.
        element_response_model: str
            Specify the element response model, should be any of
            ["default", "hamaker", "lobes", "oskar_dipole", "skala40_wave"]
            Please note that the SKALA40 Wave model is
            currently named OSKAR Spherical Wave in the EveryBeam internals.
            This will be refactored to SKALA40_WAVE in the future.

        Returns
        -------
        Telescope object
       )pbdoc",
      py::arg("name"), py::arg("data_column") = "DATA",
      py::arg("use_differential_beam") = false,
      py::arg("use_channel_frequency") = true,
      py::arg("element_response_model") = "default",
      py::arg("coeff_path") = "");

  m.def("load_telescope", &pyload_telescope, R"pbdoc(
        Load telescope from measurement set (MS)

        This version allows more fine grained control over the normalisation
        of the beam through the beam_normalisation_mode parameter.
        (needed by the DP3 python step implemented in idgcaldpstep.py in the IDG library)

        Parameters
        ----------
        name: str
            Path to MS
        data_column: str, optional
            Data column that should
        beam_normalisation_mode : BeamNormalisationMode, optional
            Defaults to BeamNormalisationMode.none (no normalisation)
            see BeamNormalisationMode enum
        use_channel_frequency: bool, optional
            Use channel frequency? Defaults to True.
        element_response_model: str
            Specify the element response model, should be any of
            ["default", "hamaker", "lobes", "oskar_dipole", "skala40_wave"]
            Please note that the SKALA40 Wave model is
            currently named OSKAR Spherical Wave in the EveryBeam internals.
            This will be refactored to SKALA40_WAVE in the future.

        Returns
        -------
        Telescope object
       )pbdoc",
        py::arg("name"), py::arg("data_column") = "DATA",
        py::arg("beam_normalisation_mode") = BeamNormalisationMode::kNone,
        py::arg("use_channel_frequency") = true,
        py::arg("element_response_model") = "default",
        py::arg("coeff_path") = "");

  m.def(
      "create_telescope",
      [](const everybeam::Options& options, const StationNode& station_tree,
         const py::array_t<double>& py_delay_directions,
         const std::array<double, 2>& tile_beam_direction,
         const std::array<double, 2>& preapplied_beam_direction,
         BeamMode preapplied_beam_mode,
         const std::vector<double>& dish_diameters, double reference_frequency,
         const std::vector<int>& mwa_delay_factors)
          -> std::unique_ptr<Telescope> {
        std::vector<std::array<double, 2>> delay_directions =
            ConvertDirections(py_delay_directions, "delay_directions");

        return CreateTelescope(options, station_tree, delay_directions,
                               tile_beam_direction, preapplied_beam_direction,
                               preapplied_beam_mode, dish_diameters,
                               reference_frequency, mwa_delay_factors);
      },
      R"pbdoc(
        Create a Telescope object from specified metadata

        This function creates a Telescope from the specified metadata without
        requiring a measurement set. The element_response_model in the Options
        object determines the telescope type and may not be ElementResponseModel.default.

        Parameters
        ----------
        options : everybeam.Options
            Configuration options for the telescope. The element_response_model
            element of this Options object determines the telescope type. It may
            thus not be ElementResponseModel.default.
        station_tree : everybeam.StationNode
            Station tree which recursively specifies the coordinate system and
            position of each station and its child elements. The tree structure
            should be appropriate for the requested telescope type.
        delay_directions : numpy.ndarray of float, optional
            Array with ra, dec coordinates (in radians), specifying the delay
            direction for each field. EveryBeam uses the J2000 reference frame.
            The shape should be (N, 2) with N the number of fields.
            When there is only one field (e.g. for LOFAR), using a 1D array
            with two elements is also supported.
            Defaults to empty array.
        tile_beam_direction : list of float, optional
            List with ra, dec coordinates (in radians), specifying the tile
            beam pointing direction. EveryBeam uses the J2000 reference frame.
            Defaults to [0.0, 0.0].
        preapplied_beam_direction : list of float, optional
            List with ra, dec coordinates (in radians), specifying the
            preapplied beam pointing direction. EveryBeam uses the J2000
            reference frame. Only used for phased array telescopes.
            Defaults to [0.0, 0.0].
        preapplied_beam_mode : BeamMode, optional
            Describes the corrections that have been applied to the preapplied
            beam.
            Only used for phased array telescopes. Defaults to BeamMode.none.
        dish_diameters : list of float, optional
            List with dish diameters (in meters) for each station. Only used
            for dish-based telescopes. Defaults to empty list.
        reference_frequency : float, optional
            Reference frequency used for beamforming (Hz). Defaults to 0.0.
            When options.use_channel_frequency is true, this value is ignored.
        mwa_delay_factors : list of int, optional
            Delay factors for the 16 elements of an MWA tile, in multiples of
            435 ps. Only used for MWA telescope. Defaults to empty list.

        Returns
        -------
        Telescope object

        Raises
        ------
        RuntimeError
            If creating a telescope for the given element response model is not
            supported.
        ValueError
            If one of the arguments does not meet the telescope requirements.
            For example, if the station tree shape is inappropriate.
       )pbdoc",
      py::arg("options"), py::arg("station_tree"),
      py::arg("delay_directions") = py::array_t<double>(),
      py::arg("tile_beam_direction") = std::array<double, 2>{0.0, 0.0},
      py::arg("preapplied_beam_direction") = std::array<double, 2>{0.0, 0.0},
      py::arg("preapplied_beam_mode") = BeamMode::kNone,
      py::arg("dish_diameters") = std::vector<double>(),
      py::arg("reference_frequency") = 0.0,
      py::arg("mwa_delay_factors") = std::vector<int>());
}
