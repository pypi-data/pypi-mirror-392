// Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "everybeam.h"

#include "pointresponse/phasedarraypoint.h"
#include "pointresponse/pointresponse.h"
#include "telescope/phasedarray.h"
#include "load.h"
#include <aocommon/uvector.h>
#include <xtensor/xview.hpp>
#include <xtensor/xadapt.hpp>

namespace everybeam {

Telescope Load(const casacore::MeasurementSet& ms) {
  Telescope telescope;
  telescope.old_telescope = Load(ms, Options());
  return telescope;
}

void AllStationResponse(BeamMode beam_mode, aocommon::MC2x2F* buffer,
                        const Telescope& telescope,
                        std::span<const double> times,
                        std::span<const std::pair<double, double>> directions,
                        std::span<const double> frequencies, size_t field_id) {
  const telescope::Telescope* old_telescope = telescope.old_telescope.get();
  const size_t n_stations = old_telescope->GetNrStations();
  const size_t n_directions = directions.size();
  const size_t n_frequencies = frequencies.size();
  const size_t n_times = times.size();
  const size_t total_size = n_stations * n_directions * n_frequencies * n_times;

  const std::array shape = {n_stations, n_times, n_directions, n_frequencies};

  // Adapt the output buffer into an xtensor adaptor.
  xt::xtensor_adaptor output_buffer =
      xt::adapt(buffer, total_size, xt::no_ownership(), shape);

  aocommon::UVector<aocommon::MC2x2F> response_buffer(n_stations *
                                                      n_frequencies);

  for (size_t time_index = 0; time_index < n_times; ++time_index) {
    const std::unique_ptr<pointresponse::PointResponse> point_response =
        old_telescope->GetPointResponse(times[time_index]);

    for (size_t dir_index = 0; dir_index < n_directions; ++dir_index) {
      point_response->ResponseAllStations(
          beam_mode, response_buffer.data(), directions[dir_index].first,
          directions[dir_index].second, frequencies, field_id);

      // Adapt the response buffer into an x array and copy it to the output
      // buffer in the correct location.
      xt::view(output_buffer, xt::all(), time_index, dir_index, xt::all()) =
          xt::adapt(response_buffer, {n_stations, n_frequencies});
    }
  }
}

void AllStationResponse(BeamMode beam_mode, aocommon::MC2x2F* buffer,
                        const Telescope& telescope,
                        std::span<const double> times,
                        std::span<const vector3r_t> directions,
                        std::span<const double> frequencies, size_t field_id) {
  const telescope::Telescope* old_telescope = telescope.old_telescope.get();
  const size_t n_stations = old_telescope->GetNrStations();
  const size_t n_directions = directions.size();
  const size_t n_frequencies = frequencies.size();
  const size_t n_times = times.size();
  const size_t total_size = n_stations * n_directions * n_frequencies * n_times;

  const std::array shape = {n_stations, n_times, n_directions, n_frequencies};

  // Adapt the output buffer into an xtensor adaptor.
  xt::xtensor_adaptor output_buffer =
      xt::adapt(buffer, total_size, xt::no_ownership(), shape);

  aocommon::UVector<aocommon::MC2x2> response_buffer(n_frequencies);

  for (size_t time_index = 0; time_index < n_times; ++time_index) {
    const std::unique_ptr<pointresponse::PointResponse> point_response =
        old_telescope->GetPointResponse(times[time_index]);

    for (size_t station_index = 0; station_index < n_stations;
         ++station_index) {
      for (size_t dir_index = 0; dir_index < n_directions; ++dir_index) {
        point_response->Response(response_buffer.data(), beam_mode,
                                 station_index, frequencies,
                                 directions[dir_index]);

        for (size_t freq_index = 0; freq_index < n_frequencies; ++freq_index) {
          output_buffer(station_index, time_index, dir_index, freq_index) =
              aocommon::MC2x2F(response_buffer[freq_index]);
        }
      }
    }
  }
}

void SingleStationResponse(
    BeamMode beam_mode, aocommon::MC2x2F* buffer, const Telescope& telescope,
    std::span<const double> times,
    std::span<const std::pair<double, double>> directions,
    std::span<const double> frequencies, size_t field_id, size_t station_id) {
  const telescope::Telescope* old_telescope = telescope.old_telescope.get();
  const size_t n_directions = directions.size();
  const size_t n_frequencies = frequencies.size();
  const size_t n_times = times.size();
  const size_t total_size = n_directions * n_frequencies * n_times;

  const std::array shape = {n_times, n_directions, n_frequencies};

  // Adapt the output buffer into an xtensor adaptor.
  xt::xtensor_adaptor output_buffer =
      xt::adapt(buffer, total_size, xt::no_ownership(), shape);

  aocommon::UVector<aocommon::MC2x2F> response_buffer(n_frequencies);

  for (size_t time_index = 0; time_index < n_times; ++time_index) {
    const std::unique_ptr<pointresponse::PointResponse> point_response =
        old_telescope->GetPointResponse(times[time_index]);

    for (size_t dir_index = 0; dir_index < n_directions; ++dir_index) {
      point_response->Response(
          beam_mode, response_buffer.data(), directions[dir_index].first,
          directions[dir_index].second, frequencies, station_id, field_id);

      // Adapt the response buffer into an x array and copy it to the output
      // buffer in the correct location.
      xt::view(output_buffer, time_index, dir_index, xt::all()) =
          xt::adapt(response_buffer);
    }
  }
}

void SingleStationResponse(BeamMode beam_mode, aocommon::MC2x2F* buffer,
                           const Telescope& telescope,
                           std::span<const double> times,
                           std::span<const vector3r_t> directions,
                           std::span<const double> frequencies, size_t field_id,
                           size_t station_id) {
  const telescope::Telescope* old_telescope = telescope.old_telescope.get();
  const size_t n_directions = directions.size();
  const size_t n_frequencies = frequencies.size();
  const size_t n_times = times.size();
  const size_t total_size = n_directions * n_frequencies * n_times;

  const std::array shape = {n_times, n_directions, n_frequencies};

  // Adapt the output buffer into an xtensor adaptor.
  xt::xtensor_adaptor output_buffer =
      xt::adapt(buffer, total_size, xt::no_ownership(), shape);

  aocommon::UVector<aocommon::MC2x2> response_buffer(n_frequencies);

  for (size_t time_index = 0; time_index < n_times; ++time_index) {
    const std::unique_ptr<pointresponse::PointResponse> point_response =
        old_telescope->GetPointResponse(times[time_index]);
    for (size_t dir_index = 0; dir_index < n_directions; ++dir_index) {
      point_response->Response(response_buffer.data(), beam_mode, station_id,
                               frequencies, directions[dir_index]);

      for (size_t freq_index = 0; freq_index < n_frequencies; ++freq_index) {
        output_buffer(time_index, dir_index, freq_index) =
            aocommon::MC2x2F(response_buffer[freq_index]);
      }
    }
  }
}

void SpecificElementResponse(
    aocommon::MC2x2F* buffer, const Telescope& telescope,
    std::span<const double> times,
    std::span<const std::pair<double, double>> directions,
    std::span<const double> frequencies, size_t field_id, size_t station_id,
    size_t element_id) {
  throw std::runtime_error(
      "EveryBeam: SpecificElementResponse with J2000 directions is not yet "
      "implemented.");
}

void SpecificElementResponse(aocommon::MC2x2F* buffer,
                             const Telescope& telescope,
                             std::span<const double> times,
                             std::span<const vector3r_t> directions,
                             std::span<const double> frequencies,
                             size_t field_id, size_t station_id,
                             size_t element_id) {
  auto phased_array_pointer = dynamic_cast<const telescope::PhasedArray*>(
      telescope.old_telescope.get());
  if (!phased_array_pointer) {
    throw std::runtime_error(
        "EveryBeam: SpecificElementResponse only supports phased array "
        "telescopes.");
  }

  const size_t n_directions = directions.size();
  const size_t n_frequencies = frequencies.size();
  const size_t n_times = times.size();
  const size_t total_size = n_directions * n_frequencies * n_times;

  const std::array shape = {n_times, n_directions, n_frequencies};

  // Adapt the output buffer into an xtensor adaptor.
  xt::xtensor_adaptor output_buffer =
      xt::adapt(buffer, total_size, xt::no_ownership(), shape);

  aocommon::UVector<aocommon::MC2x2> response_buffer(n_frequencies);

  for (size_t time_index = 0; time_index < n_times; ++time_index) {
    const pointresponse::PhasedArrayPoint point_response(*phased_array_pointer,
                                                         times[time_index]);

    for (size_t dir_index = 0; dir_index < n_directions; ++dir_index) {
      point_response.ElementResponse(response_buffer.data(), station_id,
                                     frequencies, directions[dir_index],
                                     element_id);

      for (size_t freq_index = 0; freq_index < n_frequencies; ++freq_index) {
        output_buffer(time_index, dir_index, freq_index) =
            aocommon::MC2x2F(response_buffer[freq_index]);
      }
    }
  }
}

}  // namespace everybeam
