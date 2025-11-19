// Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_LWA_ELEMENTRESPONSE_H_
#define EVERYBEAM_LWA_ELEMENTRESPONSE_H_

#include "../options.h"
#include "../sphericalharmonicsresponse.h"

namespace everybeam {

//! Implementation of the LWA response model
class LwaElementResponse : public SphericalHarmonicsResponse {
 public:
  LwaElementResponse(const Options& options)
      : SphericalHarmonicsResponse(LwaPath(options)) {}

  ElementResponseModel GetModel() const override {
    return ElementResponseModel::kLwa;
  }

  [[gnu::visibility(
      "default")]] static std::shared_ptr<const LwaElementResponse>
  GetInstance(const Options& options);

 private:
  static std::string LwaPath(const Options& options);
};
}  // namespace everybeam
#endif