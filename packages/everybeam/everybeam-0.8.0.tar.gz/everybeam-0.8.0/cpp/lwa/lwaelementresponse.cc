// Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "lwaelementresponse.h"

#include <charconv>
#include <cmath>
#include <complex>
#include <filesystem>
#include <map>
#include <optional>
#include <string_view>

#include <aocommon/throwruntimeerror.h>
#include <boost/algorithm/string/predicate.hpp>
#include <H5Cpp.h>

#include "../common/mathutils.h"
#include "../common/sphericalharmonics.h"

namespace everybeam {

std::string LwaElementResponse::LwaPath(const Options& options) {
  const std::string lwa_file = "LWA_OVRO.h5";
  const std::filesystem::path search_path =
      options.coeff_path.empty() ? GetPath("lwa")
                                 : std::filesystem::path(options.coeff_path);
  const std::filesystem::path coeff_file_path = search_path / lwa_file;

  return coeff_file_path.string();
}

std::shared_ptr<const LwaElementResponse> LwaElementResponse::GetInstance(
    const Options& options) {
  // Using a single LwaElementResponse object reduces memory
  // usage since the coefficients are only loaded once.
  // Using a static weak pointer ensures that the LwaElementResponse object
  // is deleted when it is no longer used, which saves memory.
  static std::weak_ptr<const LwaElementResponse> permanent_instance;
  std::shared_ptr<const LwaElementResponse> instance =
      permanent_instance.lock();
  if (!instance) {
    instance = std::make_shared<const LwaElementResponse>(options);
    permanent_instance = instance;
  }

  return instance;
}

}  // namespace everybeam
