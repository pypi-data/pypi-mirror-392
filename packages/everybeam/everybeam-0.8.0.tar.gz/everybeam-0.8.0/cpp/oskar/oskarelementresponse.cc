// Copyright (C) 2022 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "oskarelementresponse.h"
#include "../common/constants.h"

#include <cassert>
#include <iostream>

#include "ska-sdp-func/utility/sdp_mem.h"
#include <ska-sdp-func/station_beam/sdp_element_dipole.h>
#include <ska-sdp-func/station_beam/sdp_element_spherical_wave_harp.h>

#include "config.h"
#include "oskardatafile.h"

namespace {

constexpr sdp_MemType sdp_complex_double =
    static_cast<sdp_MemType>(SDP_MEM_DOUBLE | SDP_MEM_COMPLEX);

// Translates an sdp_Error code to an exception
void check_sdp_status(sdp_Error status) {
  if (status != SDP_SUCCESS) {
    throw std::runtime_error(
        "Error in call to function in ska-sdp-func. Error code = " +
        std::to_string(status));
  }
}

// Wrapper class to add RAII behaviour to sdp_Mem
class SdpMemory {
 public:
  SdpMemory(void* data, sdp_MemType mem_type, int nr_dimensions,
            const int64_t* shape) {
    sdp_Error status = SDP_SUCCESS;
    sdp_mem_ = sdp_mem_create_wrapper(data, mem_type, SDP_MEM_CPU,
                                      nr_dimensions, shape, nullptr, &status);
    check_sdp_status(status);
  }
  // There is no const version of sdp_mem_create_wrapper in ska-sdp-func
  // Instead, cast the const away and manually set the read_only flag
  // TODO in AST-1435, add a const version of sdp_mem_create_wrapper
  // to the PFL and use it here.
  SdpMemory(const void* data, sdp_MemType mem_type, int nr_dimensions,
            const int64_t* shape)
      : SdpMemory(const_cast<void*>(data), mem_type, nr_dimensions, shape) {
    sdp_mem_set_read_only(sdp_mem_, true);
  }
  ~SdpMemory() { sdp_mem_free(sdp_mem_); }

  // User defined conversion function that enables implicit conversion from
  // SdpMemory to sdp_Mem*. This allows the user to pass SdpMemory
  // objects to functions that expect an sdp_Mem*.
  operator sdp_Mem*() { return sdp_mem_; }

 private:
  sdp_Mem* sdp_mem_;
};

}  // namespace

namespace everybeam {

aocommon::MC2x2 OSKARElementResponseDipole::Response(double frequency,
                                                     double theta,
                                                     double phi) const {
  assert(std::isfinite(frequency) && frequency > 0.0);

  aocommon::MC2x2 response = aocommon::MC2x2::Zero();

  const double wavelength_m = common::c / frequency;
  const double dipole_length_m = 0.5 * wavelength_m;

  const int64_t num_points = 2;
  const std::array<double, 2> theta_array = {theta, theta};
  const std::array<double, 2> phi_array = {phi, phi + M_PI_2};

  // Using a stride of 2 ensures that the result for the first and second points
  // go into the top and bottom row of 'response', respectively.
  const int stride_element_beam = 2;
  const int index_offset_element_beam = 0;

  const std::array<int64_t, 3> data_shape = {num_points, 2, 2};
  SdpMemory theta_mem(theta_array.data(), SDP_MEM_DOUBLE, 1, &num_points);
  SdpMemory phi_mem(phi_array.data(), SDP_MEM_DOUBLE, 1, &num_points);
  SdpMemory response_mem(aocommon::DubiousDComplexPointerCast(response),
                         sdp_complex_double, 3, data_shape.data());
  sdp_Error status = SDP_SUCCESS;

  sdp_element_beam_dipole(num_points, theta_mem, phi_mem, frequency,
                          dipole_length_m, stride_element_beam,
                          index_offset_element_beam, response_mem, &status);
  check_sdp_status(status);

  return response;
}

aocommon::MC2x2 OSKARElementResponseDipoleCos::Response(double frequency,
                                                        double theta,
                                                        double phi) const {
  const aocommon::MC2x2 response =
      OSKARElementResponseDipole::Response(frequency, theta, phi);
  return response * std::cos(theta);
}

OSKARElementResponseSphericalWave::OSKARElementResponseSphericalWave()
    : datafile_(cached_datafile_.lock()) {
  if (!datafile_) {
    datafile_ = std::make_shared<Datafile>(GetPath("oskar.h5"));
    cached_datafile_ = datafile_;
  }
}

OSKARElementResponseSphericalWave::OSKARElementResponseSphericalWave(
    const std::string& filename)
    : datafile_(std::make_shared<Datafile>(filename)) {}

aocommon::MC2x2 OSKARElementResponseSphericalWave::Response(
    [[maybe_unused]] double freq, [[maybe_unused]] double theta,
    [[maybe_unused]] double phi) const {
  // This ElementResponse model is element specific, so an element_id is
  // required to know for what element the response needs to be evaluated A
  // std::invalid_argument exception is thrown although strictly speaking it are
  // not the given arguments that are invalid, but the Response(...) method with
  // a different signature should have been called.
  throw std::invalid_argument(
      "OSKARElementResponseSphericalWave: missing argument element_id");
}

aocommon::MC2x2 OSKARElementResponseSphericalWave::Response(int element_id,
                                                            double freq,
                                                            double theta,
                                                            double phi) const {
  aocommon::MC2x2 response = aocommon::MC2x2::Zero();

  const Dataset& dataset = datafile_->Get(freq);
  const size_t l_max = dataset.GetLMax();

  const Double4C* alpha_ptr = dataset.GetAlphaPtr(element_id);

  int num_points = 1;
  const int64_t data_shape[] = {num_points, 4};
  sdp_Error status = SDP_SUCCESS;

  SdpMemory theta_sdp_mem(&theta, SDP_MEM_DOUBLE, 1, data_shape);

  SdpMemory phi_sdp_mem(&phi, SDP_MEM_DOUBLE, 1, data_shape);

  const int nr_coefficients = l_max * (l_max + 2);
  const int64_t coeffs_shape[] = {nr_coefficients, 4};

  SdpMemory coeffs_sdp_mem(static_cast<const void*>(alpha_ptr),
                           sdp_complex_double, 2, coeffs_shape);

  int index_offset_element_beam = 0;
  SdpMemory element_beam_sdp_mem(aocommon::DubiousDComplexPointerCast(response),
                                 sdp_complex_double, 2, data_shape);

  // TODO: phi_x and phi_y can have different values if there is only one set
  // of coefficients that is is used for both dipoles.
  // In that case it is assumed the Y dipole rotated 90deg with respect
  // to the X dipole, so then phi_y = phi+ M_PI_2.
  // That case needs to be detected when the coefficients are read,
  // and here phi_y needs to be set accordingly.
  sdp_element_beam_spherical_wave_harp(
      num_points, theta_sdp_mem, phi_sdp_mem, phi_sdp_mem, l_max,
      coeffs_sdp_mem, index_offset_element_beam, element_beam_sdp_mem, &status);
  check_sdp_status(status);

  return response;
}

std::weak_ptr<Datafile> OSKARElementResponseSphericalWave::cached_datafile_;

}  // namespace everybeam
