// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "phasedarraygrid.h"
#include "../telescope/phasedarray.h"

#include <aocommon/lane.h>
#include <aocommon/imagecoordinates.h>
#include <aocommon/system.h>
#include <cmath>
#include <iostream>
namespace everybeam {

using telescope::PhasedArray;

namespace griddedresponse {

PhasedArrayGrid::PhasedArrayGrid(
    const PhasedArray& phased_array,
    const aocommon::CoordinateSystem& coordinate_system)
    : GriddedResponse(&phased_array, coordinate_system),
      PhasedArrayResponse(phased_array) {
  // Compute and set number of threads
  const size_t ncpus = aocommon::system::ProcessorCount();
  const size_t nthreads = std::min(ncpus, phased_array.GetNrStations());
  threads_.resize(nthreads);
}

void PhasedArrayGrid::Response(BeamMode beam_mode, std::complex<float>* buffer,
                               double time, double frequency,
                               size_t station_idx,
                               [[maybe_unused]] size_t field_id) {
  aocommon::Lane<Job> lane(threads_.size());
  lane_ = &lane;

  SetITRFVectors(time);

  inverse_central_gain_.resize(1);
  bool apply_normalisation = CalculateBeamNormalisation(
      beam_mode, time, frequency, station_idx, inverse_central_gain_[0]);

  // Prepare threads
  for (auto& thread : threads_) {
    thread = std::thread(&PhasedArrayGrid::CalcThread, this, beam_mode,
                         apply_normalisation, buffer, time, frequency);
  }

  for (size_t y = 0; y != height_; ++y) {
    lane.emplace(Job(y, station_idx, 0));
  }

  lane.write_end();
  for (auto& thread : threads_) thread.join();
}

void PhasedArrayGrid::ResponseAllStations(BeamMode beam_mode,
                                          std::complex<float>* buffer,
                                          double time, double frequency,
                                          size_t) {
  const PhasedArray& phased_array = GetPhasedArray();
  aocommon::Lane<Job> lane(threads_.size());
  lane_ = &lane;

  SetITRFVectors(time);

  bool apply_normalisation = false;
  inverse_central_gain_.resize(phased_array.GetNrStations());
  for (size_t i = 0; i != phased_array.GetNrStations(); ++i) {
    apply_normalisation = CalculateBeamNormalisation(
        beam_mode, time, frequency, i, inverse_central_gain_[i]);
  }

  // Prepare threads
  for (auto& thread : threads_) {
    thread = std::thread(&PhasedArrayGrid::CalcThread, this, beam_mode,
                         apply_normalisation, buffer, time, frequency);
  }

  for (size_t y = 0; y != height_; ++y) {
    for (size_t antenna_idx = 0; antenna_idx != phased_array.GetNrStations();
         ++antenna_idx) {
      lane.write(Job(y, antenna_idx, antenna_idx));
    }
  }

  lane.write_end();
  for (auto& thread : threads_) thread.join();
}

void PhasedArrayGrid::SetITRFVectors(double time) {
  const PhasedArray& phased_array = GetPhasedArray();

  const coords::ItrfConverter itrf_converter(time);
  station0_ = itrf_converter.ToItrf(phased_array.GetDelayDirection());
  tile0_ = itrf_converter.ToItrf(phased_array.GetTileBeamDirection());

  l_vector_itrf_ = itrf_converter.RaDecToItrf(ra_ + M_PI / 2.0, 0);
  m_vector_itrf_ = itrf_converter.RaDecToItrf(ra_, dec_ + M_PI / 2.0);
  n_vector_itrf_ = itrf_converter.RaDecToItrf(ra_, dec_);
  diff_beam_centre_ =
      itrf_converter.ToItrf(phased_array.GetPreappliedBeamDirection());
}

void PhasedArrayGrid::CalcThread(BeamMode beam_mode, bool apply_normalisation,
                                 std::complex<float>* buffer, double time,
                                 double frequency) {
  const PhasedArray& phased_array = GetPhasedArray();
  const size_t values_per_ant = width_ * height_ * 4;
  const double sb_freq = phased_array.GetOptions().use_channel_frequency
                             ? frequency
                             : phased_array.GetSubbandFrequency();

  Job job;
  while (lane_->read(job)) {
    for (size_t x = 0; x != width_; ++x) {
      double l, m, n;
      aocommon::ImageCoordinates::XYToLM(x, job.y, dl_, dm_, width_, height_, l,
                                         m);
      l += l_shift_;
      m += m_shift_;
      const double sqrt_term = 1.0 - l * l - m * m;
      if (sqrt_term >= 0.0) {
        n = std::sqrt(sqrt_term);
      } else {
        n = -std::sqrt(-sqrt_term);
      }

      const vector3r_t itrf_direction =
          l * l_vector_itrf_ + m * m_vector_itrf_ + n * n_vector_itrf_;

      std::complex<float>* base_buffer = buffer + (x + job.y * width_) * 4;

      std::complex<float>* ant_buffer_ptr =
          base_buffer + job.buffer_offset * values_per_ant;

      aocommon::MC2x2F gain_matrix(phased_array.GetStation(job.antenna_idx)
                                       .Response(beam_mode, time, frequency,
                                                 itrf_direction, sb_freq,
                                                 station0_, tile0_));

      if (apply_normalisation) {
        gain_matrix = inverse_central_gain_[job.buffer_offset] * gain_matrix;
      }
      gain_matrix.AssignTo(ant_buffer_ptr);
    }
  }
}
}  // namespace griddedresponse
}  // namespace everybeam
