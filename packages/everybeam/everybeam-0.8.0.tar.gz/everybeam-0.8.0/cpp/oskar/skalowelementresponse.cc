// Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "skalowelementresponse.h"

#include <filesystem>
#include <optional>

#include "../common/sphericalharmonics.h"
#include "config.h"

namespace {

std::string GetCoefficientsPath(const std::string& file_path,
                                const everybeam::Options& options) {
  const std::filesystem::path search_path =
      options.coeff_path.empty() ? everybeam::GetDataDirectory() / "ska"
                                 : std::filesystem::path(options.coeff_path);

  const std::filesystem::path coeff_file_path = search_path / file_path;
  if (!std::filesystem::exists(coeff_file_path)) {
    const std::string exception_message =
        "Cannot find coeffients at " + coeff_file_path.string();
    throw std::invalid_argument(exception_message);
  }

  return coeff_file_path.string();
}
}  // namespace

namespace everybeam {

SkaLowElementResponse::SkaLowElementResponse(const std::string& name,
                                             const Options& options)
    : SphericalHarmonicsResponse(GetCoefficientsPath(name, options)){};

std::shared_ptr<const SkaLowElementResponse> SkaLowElementResponse::GetInstance(
    const std::string& file_path, const Options& options) {
  // Cache the instance of the coefficients so that only one instance per
  // coefficient.
  static std::map<std::string, std::weak_ptr<const SkaLowElementResponse>>
      name_response_map;
  std::shared_ptr<const SkaLowElementResponse> instance;

  auto entry = name_response_map.find(file_path);
  if (entry == name_response_map.end()) {
    instance =
        std::make_shared<const SkaLowElementResponse>(file_path, options);
    name_response_map.insert({file_path, instance});
  } else {
    instance = entry->second.lock();
    if (!instance) {
      instance =
          std::make_shared<const SkaLowElementResponse>(file_path, options);
      entry->second = instance;
    }
  }
  return instance;
}

}  // namespace everybeam
