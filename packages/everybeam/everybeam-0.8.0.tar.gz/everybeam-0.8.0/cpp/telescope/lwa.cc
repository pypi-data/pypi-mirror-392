// lwa.cc: Implementation for the OVRO-LWA telescope class
//
// Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "lwa.h"

#include <aocommon/banddata.h>

namespace everybeam::telescope {

namespace {
Options SetTelescopeOptions(const Options& options) {
  Options new_options = options;
  if (options.element_response_model == ElementResponseModel::kDefault) {
    new_options.element_response_model = ElementResponseModel::kLwa;
  }
  return new_options;
}
}  // namespace

Lwa::Lwa(const casacore::MeasurementSet& ms, const Options& options)
    : PhasedArray(ms, SetTelescopeOptions(options)) {
  // Read Field information
  casacore::ScalarMeasColumn<casacore::MDirection> delay_dir_col(
      ms.field(),
      casacore::MSField::columnName(casacore::MSFieldEnums::DELAY_DIR));
  SetDelayDirection(delay_dir_col(0));

  CalculatePreappliedBeamOptions(ms);
}

}  // namespace everybeam::telescope
