// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "load.h"

#include <string>
#include <stdexcept>

#include <aocommon/logger.h>

#include <casacore/ms/MeasurementSets/MeasurementSet.h>
#include <casacore/tables/Tables/ScalarColumn.h>

#include "common/casautils.h"

#include "telescope/alma.h"
#include "telescope/dish.h"
#include "telescope/dsa110.h"
#include "telescope/lofar.h"
#include "telescope/lwa.h"
#include "telescope/mwa.h"
#include "telescope/oskar.h"
#include "telescope/skamid.h"

#include "circularsymmetric/atcacoefficients.h"
#include "circularsymmetric/gmrtcoefficients.h"
#include "circularsymmetric/meerkatcoefficients.h"
#include "circularsymmetric/vlacoefficients.h"

namespace everybeam {
TelescopeType GetTelescopeType(const casacore::MeasurementSet& ms) {
  // Read Telescope name and convert to enum
  casacore::ScalarColumn<casacore::String> telescope_name_col(ms.observation(),
                                                              "TELESCOPE_NAME");
  std::string telescope_name = telescope_name_col(0);
  std::for_each(telescope_name.begin(), telescope_name.end(),
                [](char& c) { c = ::toupper(c); });

  if (telescope_name == "AARTFAAC") {
    return kAARTFAAC;
  } else if (telescope_name.compare(0, 4, "ATCA") == 0) {
    return kATCATelescope;
  } else if (telescope_name == "ALMA") {
    return kALMATelescope;
  } else if (telescope_name.compare(0, 4, "DSA_") == 0 ||
             telescope_name == "CARMA") {
    if (telescope_name == "CARMA") {
      aocommon::Logger::Warn
          << "This measurement set has 'CARMA' in the telescope name field. "
             "The CARMA telescope is not supported. Because DSA_110 also uses "
             "'CARMA' in the telescope name field, EveryBeam will calculate "
             "the beam for DSA 110. To get rid of this warning, update the "
             "TELESCOPE_NAME in the OBSERVATION table to 'DSA_110'.\n";
    }
    return kDsa110Telescope;
  } else if (telescope_name.compare(0, 4, "EVLA") == 0) {
    return kVLATelescope;
  } else if (telescope_name == "GMRT") {
    return kGMRTTelescope;
  } else if (telescope_name == "LOFAR") {
    return kLofarTelescope;
  } else if (telescope_name == "MEERKAT") {
    return kMeerKATTelescope;
  } else if (telescope_name == "MID") {
    return kSkaMidTelescope;
  } else if (telescope_name == "MWA") {
    return kMWATelescope;
  } else if (telescope_name.rfind("OSKAR", 0) == 0 ||
             telescope_name == "SKA-LOW") {
    return kOSKARTelescope;
  } else if (telescope_name == "OVRO_MMA" || telescope_name == "OVRO_LWA" ||
             telescope_name == "OVRO-LWA") {
    return kOvroLwaTelescope;
  } else {
    return kUnknownTelescope;
  }
}

std::unique_ptr<telescope::Telescope> Load(const casacore::MeasurementSet& ms,
                                           const Options& options) {
  std::unique_ptr<telescope::Telescope> telescope;
  const TelescopeType telescope_name = GetTelescopeType(ms);
  switch (telescope_name) {
    case kAARTFAAC:
    case kLofarTelescope:
      telescope = std::make_unique<telescope::LOFAR>(ms, options);
      break;
    case kALMATelescope:
      telescope = std::make_unique<telescope::Alma>(ms, options);
      break;
    case kATCATelescope: {
      auto coefs = std::make_unique<circularsymmetric::ATCACoefficients>();
      telescope =
          std::make_unique<telescope::Dish>(ms, std::move(coefs), options);
    } break;
    case kDsa110Telescope: {
      telescope = std::make_unique<telescope::Dsa110>(ms, options);
    } break;
    case kGMRTTelescope: {
      auto coefs = std::make_unique<circularsymmetric::GMRTCoefficients>();
      telescope =
          std::make_unique<telescope::Dish>(ms, std::move(coefs), options);
    } break;
    case kMeerKATTelescope: {
      auto coefs = std::make_unique<circularsymmetric::MeerKATCoefficients>();
      telescope =
          std::make_unique<telescope::Dish>(ms, std::move(coefs), options);
    } break;
    case kMWATelescope:
      telescope = std::make_unique<telescope::MWA>(ms, options);
      break;
    case kOSKARTelescope:
      telescope = std::make_unique<telescope::OSKAR>(ms, options);
      break;
    case kSkaMidTelescope:
      telescope = std::make_unique<telescope::SkaMid>(ms, options);
      break;
    case kVLATelescope: {
      auto coefs = std::make_unique<circularsymmetric::VLACoefficients>("");
      telescope =
          std::make_unique<telescope::Dish>(ms, std::move(coefs), options);
    } break;
    case kOvroLwaTelescope: {
      telescope = std::make_unique<telescope::Lwa>(ms, options);
    } break;
    default:
      casacore::ScalarColumn<casacore::String> telescope_name_col(
          ms.observation(), "TELESCOPE_NAME");
      std::stringstream message;
      message << "The requested telescope type " << telescope_name_col(0)
              << " is not implemented.";
      throw std::runtime_error(message.str());
  }
  return telescope;
}

std::unique_ptr<telescope::Telescope> Load(const std::string& ms_name,
                                           const Options& options) {
  casacore::MeasurementSet ms(ms_name);
  return Load(ms, options);
}

std::unique_ptr<telescope::Telescope> CreateTelescope(
    const Options& options, const StationNode& station_tree,
    const std::vector<std::array<double, 2>>& delay_directions,
    const std::array<double, 2>& tile_beam_direction,
    const std::array<double, 2>& preapplied_beam_direction,
    BeamMode preapplied_beam_mode, const std::vector<double>& dish_diameters,
    double lofar_reference_frequency,
    const std::vector<int>& mwa_delay_factors) {
  switch (options.element_response_model) {
    case ElementResponseModel::kOSKARDipole:
    case ElementResponseModel::kOSKARSphericalWave:
    case ElementResponseModel::kOSKARDipoleCos: {
      if (delay_directions.size() != 1) {
        throw std::invalid_argument(
            "OSKAR telescope requires exactly one delay direction.");
      }
      const std::array<double, 2>& delay_direction = delay_directions[0];
      return std::make_unique<telescope::OSKAR>(
          station_tree,
          common::RaDecToDirection(delay_direction[0], delay_direction[1]),
          options);
    }
    default:
      std::stringstream message;
      message << "Creating a telescope for the '"
              << options.element_response_model
              << "' element response model is not implemented.";
      throw std::runtime_error(message.str());
  }
}

}  // namespace everybeam
