// Copyright (C) 2025 SKAO
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_SKALOW_ELEMENTRESPONSE_H_
#define EVERYBEAM_SKALOW_ELEMENTRESPONSE_H_

#include <memory>
#include <string>
#include <tuple>

#include "../options.h"
#include "../sphericalharmonicsresponse.h"

namespace everybeam {

class SkaLowElementResponse : public SphericalHarmonicsResponse {
 public:
  /**
   * @brief Construct a new SkaLowElementResponse object
   *
   * @param options if options.coeff_path is non-empty it is used to find
   * coefficient files
   */
  SkaLowElementResponse(const std::string& name, const Options& options);

  ElementResponseModel GetModel() const final override {
    return ElementResponseModel::kSkaLowFeko;
  }

  /**
   * @brief Create SkaLowElementResponse
   *
   * @param file_path path to the coefficient file relative to the everybeam
   * DATA_DIR
   * @param options options to compute the response
   */
  static std::shared_ptr<const SkaLowElementResponse> GetInstance(
      const std::string& file_path, const Options& options);
};

}  // namespace everybeam

#endif  // EVERYBEAM_SKALOW_ELEMENTRESPONSE_H_
