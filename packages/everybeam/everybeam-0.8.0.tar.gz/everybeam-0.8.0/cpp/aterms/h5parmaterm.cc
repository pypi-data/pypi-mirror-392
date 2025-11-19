#include "h5parmaterm.h"

#include "../common/fftresampler.h"

#include <aocommon/imagecoordinates.h>
#include <cmath>
#include <algorithm>

using schaapcommon::h5parm::AxisInfo;
using schaapcommon::h5parm::H5Parm;
using schaapcommon::h5parm::SolTab;

namespace everybeam {
namespace aterms {

LagrangePolynomial::LagrangePolynomial(size_t nr_coeffs,
                                       const std::vector<double>& l,
                                       const std::vector<double>& m)
    : nr_coeffs_(nr_coeffs),
      nr_pixels_(l.size()),
      basis_(nr_coeffs_ * nr_pixels_, 1.0) {
  order_ = ComputeOrder(nr_coeffs_);
  int k = 0;
  for (int i = 1; i <= int(order_); ++i) {
    for (int j = 0; j < i; ++j) {
      ++k;
      size_t offset_src = (k - i) * nr_pixels_;
      size_t offset_dst = k * nr_pixels_;
      for (int ii = 0; ii < int(nr_pixels_); ++ii) {
        basis_[offset_dst + ii] = basis_[offset_src + ii] * l[ii];
      }
    }
    ++k;
    size_t offset_src = (k - i - 1) * nr_pixels_;
    size_t offset_dst = k * nr_pixels_;
    for (int ii = 0; ii < int(nr_pixels_); ++ii) {
      basis_[offset_dst + ii] = basis_[offset_src + ii] * m[ii];
    }
  }
}

void LagrangePolynomial::Evaluate(const double* coeffs, int stride,
                                  double* output) {
  for (int i = 0; i < int(nr_pixels_); ++i) {
    output[i] = 0.0;
    for (int j = 0; j < int(nr_coeffs_); ++j) {
      output[i] += basis_[j * nr_pixels_ + i] * coeffs[j * stride];
    }
  }
}

size_t LagrangePolynomial::ComputeOrder(size_t nr_coeffs) {
  // Solution to the quadratic expression (order + 1)(order + 2) / 2 =
  // nr_coeffs, for the positive square root of the discriminant
  return (-3 + std::sqrt(1 + 8 * nr_coeffs)) / 2;
}

size_t LagrangePolynomial::ComputeNrCoeffs(size_t order) {
  return (order + 1) * (order + 2) / 2;
}

H5ParmATerm::H5ParmATerm(const std::vector<std::string>& station_names_ms,
                         const aocommon::CoordinateSystem& coordinate_system)
    : station_names_ms_(station_names_ms),
      coordinate_system_(coordinate_system),
      update_interval_(0),
      last_aterm_update_(-1),
      last_ampl_index_(std::numeric_limits<hsize_t>::max()),
      last_phase_index_(std::numeric_limits<hsize_t>::max()),
      amplitude1_cache_(station_names_ms_.size() * coordinate_system_.width *
                        coordinate_system_.height),
      amplitude2_cache_(station_names_ms_.size() * coordinate_system_.width *
                        coordinate_system_.height),
      slowphase1_cache_(station_names_ms_.size() * coordinate_system_.width *
                        coordinate_system_.height),
      slowphase2_cache_(station_names_ms_.size() * coordinate_system_.width *
                        coordinate_system_.height),
      phase_cache_(station_names_ms_.size() * coordinate_system_.width *
                   coordinate_system_.height) {}

void H5ParmATerm::Open(const std::vector<std::string>& filenames) {
  if (filenames.size() > 1) {
    throw std::runtime_error("Multiple h5parm input files not (yet) supported");
  }
  for (auto const& filename : filenames) {
    H5Parm h5parmfile(filename);
    // Fill solution tables
    amplitude1_soltab_.push_back(
        h5parmfile.GetSolTab("amplitude1_coefficients"));
    amplitude2_soltab_.push_back(
        h5parmfile.GetSolTab("amplitude2_coefficients"));
    slowphase1_soltab_.push_back(
        h5parmfile.GetSolTab("slowphase1_coefficients"));
    slowphase2_soltab_.push_back(
        h5parmfile.GetSolTab("slowphase2_coefficients"));
    phase_soltab_.push_back(h5parmfile.GetSolTab("phase_coefficients"));
  }

  std::vector<double> l(coordinate_system_.height * coordinate_system_.width);
  std::vector<double> m(coordinate_system_.height * coordinate_system_.width);

  for (size_t y = 0; y < coordinate_system_.height; ++y) {
    for (size_t x = 0; x < coordinate_system_.width; ++x) {
      aocommon::ImageCoordinates::XYToLM(
          x, y, coordinate_system_.dl, coordinate_system_.dm,
          coordinate_system_.width, coordinate_system_.height,
          l[y * coordinate_system_.width + x],
          m[y * coordinate_system_.width + x]);

      l[y * coordinate_system_.width + x] += coordinate_system_.l_shift;
      m[y * coordinate_system_.width + x] += coordinate_system_.m_shift;
    }
  }

  amplitude1_polynomial_ =
      std::unique_ptr<LagrangePolynomial>(new LagrangePolynomial(
          amplitude1_soltab_.back().GetAxis("dir").size, l, m));
  amplitude2_polynomial_ =
      std::unique_ptr<LagrangePolynomial>(new LagrangePolynomial(
          amplitude2_soltab_.back().GetAxis("dir").size, l, m));
  slowphase1_polynomial_ =
      std::unique_ptr<LagrangePolynomial>(new LagrangePolynomial(
          slowphase1_soltab_.back().GetAxis("dir").size, l, m));
  slowphase2_polynomial_ =
      std::unique_ptr<LagrangePolynomial>(new LagrangePolynomial(
          slowphase2_soltab_.back().GetAxis("dir").size, l, m));
  phase_polynomial_ = std::unique_ptr<LagrangePolynomial>(
      new LagrangePolynomial(phase_soltab_.back().GetAxis("dir").size, l, m));

  // Check that antenna names in h5parm match exactly
  std::vector<std::string> station_names_ampl =
      amplitude1_soltab_.back().GetStringAxis("ant");
  std::vector<std::string> station_names_phase =
      phase_soltab_.back().GetStringAxis("ant");

  if (station_names_phase != station_names_ampl) {
    throw std::runtime_error(
        "Stations in amplitude soltab are not equal to the stations in phase "
        "soltab.");
  }

  for (size_t i = 0; i < station_names_ms_.size(); ++i) {
    ms_to_soltab_station_mapping_.push_back(
        amplitude1_soltab_.back().GetAntIndex(station_names_ms_[i]));
  }
}

bool H5ParmATerm::Calculate(std::complex<float>* buffer, double time,
                            double frequency, size_t, const double*) {
  const bool outdated = std::fabs(time - last_aterm_update_) > update_interval_;
  if (!outdated) return false;

  last_aterm_update_ = time;

  hsize_t time_index_amplitude = amplitude1_soltab_[0].GetTimeIndex(time);
  hsize_t time_index_phase = phase_soltab_[0].GetTimeIndex(time);
  const bool recalculate_diagonal = (time_index_amplitude != last_ampl_index_);
  const bool recalculate_fastphase = (time_index_phase != last_phase_index_);

  if (!recalculate_diagonal && !recalculate_fastphase) return false;

  int amplitude_ant_stride = 0;
  int amplitude_time_stride = 0;
  int amplitude_freq_stride_out = 0;
  int amplitude_pol_stride = 0;
  int amplitude_dir_stride = 0;
  int phase_ant_stride = 0;
  int phase_time_stride = 0;
  int phase_freq_stride_out = 0;
  int phase_pol_stride = 0;
  int phase_dir_stride = 0;

  if (recalculate_diagonal) {
    int ant_count = amplitude1_soltab_.back().GetAxis("ant").size;
    int dir_count = amplitude1_soltab_.back().GetAxis("dir").size;
    std::tie(amplitude_ant_stride, amplitude_time_stride,
             amplitude_freq_stride_out, amplitude_pol_stride,
             amplitude_dir_stride) =
        amplitude1_soltab_.back().GetSubArray(
            "val", 0, ant_count, 1,  // ant_offset, ant_count, ant_stride,
            time_index_amplitude, 1,
            1,                // time_offset, time_count, time_stride,
            0, 1, 1,          // freq_offset, freq_count, freq_stride,
            0, 1, 1,          // pol_offset, pol_count, pol_stride
            0, dir_count, 1,  // dir_offset, dir_count, dir_stride
            amplitude1_coefficients_);
    std::tie(amplitude_ant_stride, amplitude_time_stride,
             amplitude_freq_stride_out, amplitude_pol_stride,
             amplitude_dir_stride) =
        amplitude2_soltab_.back().GetSubArray(
            "val", 0, ant_count, 1,  // ant_offset, ant_count, ant_stride,
            time_index_amplitude, 1,
            1,                // time_offset, time_count, time_stride,
            0, 1, 1,          // freq_offset, freq_count, freq_stride,
            0, 1, 1,          // pol_offset, pol_count, pol_stride
            0, dir_count, 1,  // dir_offset, dir_count, dir_stride
            amplitude2_coefficients_);
    std::tie(amplitude_ant_stride, amplitude_time_stride,
             amplitude_freq_stride_out, amplitude_pol_stride,
             amplitude_dir_stride) =
        slowphase1_soltab_.back().GetSubArray(
            "val", 0, ant_count, 1,  // ant_offset, ant_count, ant_stride,
            time_index_amplitude, 1,
            1,                // time_offset, time_count, time_stride,
            0, 1, 1,          // freq_offset, freq_count, freq_stride,
            0, 1, 1,          // pol_offset, pol_count, pol_stride
            0, dir_count, 1,  // dir_offset, dir_count, dir_stride
            slowphase1_coefficients_);
    std::tie(amplitude_ant_stride, amplitude_time_stride,
             amplitude_freq_stride_out, amplitude_pol_stride,
             amplitude_dir_stride) =
        slowphase2_soltab_.back().GetSubArray(
            "val", 0, ant_count, 1,  // ant_offset, ant_count, ant_stride,
            time_index_amplitude, 1,
            1,                // time_offset, time_count, time_stride,
            0, 1, 1,          // freq_offset, freq_count, freq_stride,
            0, 1, 1,          // pol_offset, pol_count, pol_stride
            0, dir_count, 1,  // dir_offset, dir_count, dir_stride
            slowphase2_coefficients_);
  }
  if (recalculate_fastphase) {
    int ant_count = phase_soltab_.back().GetAxis("ant").size;
    int dir_count = phase_soltab_.back().GetAxis("dir").size;
    std::tie(phase_ant_stride, phase_time_stride, phase_freq_stride_out,
             phase_pol_stride, phase_dir_stride) =
        phase_soltab_.back().GetSubArray(
            "val", 0, ant_count, 1,  // ant_offset, ant_count, ant_stride,
            time_index_phase, 1, 1,  // time_offset, time_count, time_stride,
            0, 1, 1,                 // freq_offset, freq_count, freq_stride,
            0, 1, 1,                 // pol_offset, pol_count, pol_stride
            0, dir_count, 1,         // dir_offset, dir_count, dir_stride
            phase_coefficients_);
  }

  // #pragma omp parallel for
  for (size_t i = 0; i < station_names_ms_.size(); ++i) {
    int ant_index_in_soltab = ms_to_soltab_station_mapping_[i];
    if (recalculate_diagonal) {
      amplitude1_polynomial_->Evaluate(
          &amplitude1_coefficients_[ant_index_in_soltab * amplitude_ant_stride],
          amplitude_dir_stride,
          &amplitude1_cache_[i * coordinate_system_.height *
                             coordinate_system_.width]);
      amplitude2_polynomial_->Evaluate(
          &amplitude2_coefficients_[ant_index_in_soltab * amplitude_ant_stride],
          amplitude_dir_stride,
          &amplitude2_cache_[i * coordinate_system_.height *
                             coordinate_system_.width]);
      slowphase1_polynomial_->Evaluate(
          &slowphase1_coefficients_[ant_index_in_soltab * amplitude_ant_stride],
          amplitude_dir_stride,
          &slowphase1_cache_[i * coordinate_system_.height *
                             coordinate_system_.width]);
      slowphase2_polynomial_->Evaluate(
          &slowphase2_coefficients_[ant_index_in_soltab * amplitude_ant_stride],
          amplitude_dir_stride,
          &slowphase2_cache_[i * coordinate_system_.height *
                             coordinate_system_.width]);
    }
    if (recalculate_fastphase) {
      phase_polynomial_->Evaluate(
          &phase_coefficients_[ant_index_in_soltab * phase_ant_stride],
          phase_dir_stride,
          &phase_cache_[i * coordinate_system_.height *
                        coordinate_system_.width]);
    }

    for (size_t y = 0; y < coordinate_system_.height; ++y) {
      for (size_t x = 0; x < coordinate_system_.width; ++x) {
        // Store output on "diagonal" of Jones matrix
        buffer[i * coordinate_system_.height * coordinate_system_.width * 4 +
               y * coordinate_system_.width * 4 + x * 4] =
            std::complex<float>(
                amplitude1_cache_[i * coordinate_system_.height *
                                      coordinate_system_.width +
                                  y * coordinate_system_.width + x] *
                std::exp(std::complex<double>(
                    0.0,
                    phase_cache_[i * coordinate_system_.height *
                                     coordinate_system_.width +
                                 y * coordinate_system_.width + x] +
                        slowphase1_cache_[i * coordinate_system_.height *
                                              coordinate_system_.width +
                                          y * coordinate_system_.width + x])));
        buffer[i * coordinate_system_.height * coordinate_system_.width * 4 +
               y * coordinate_system_.width * 4 + x * 4 + 1] = 0.0;
        buffer[i * coordinate_system_.height * coordinate_system_.width * 4 +
               y * coordinate_system_.width * 4 + x * 4 + 2] = 0.0;
        buffer[i * coordinate_system_.height * coordinate_system_.width * 4 +
               y * coordinate_system_.width * 4 + x * 4 + 3] =
            std::complex<float>(
                amplitude2_cache_[i * coordinate_system_.height *
                                      coordinate_system_.width +
                                  y * coordinate_system_.width + x] *
                std::exp(std::complex<double>(
                    0.0,
                    phase_cache_[i * coordinate_system_.height *
                                     coordinate_system_.width +
                                 y * coordinate_system_.width + x] +
                        slowphase2_cache_[i * coordinate_system_.height *
                                              coordinate_system_.width +
                                          y * coordinate_system_.width + x])));
      }
    }
  }
  // Update amplitude and phase index to latest
  last_ampl_index_ = time_index_amplitude;
  last_phase_index_ = time_index_phase;
  return true;
}

}  // namespace aterms
}  // namespace everybeam