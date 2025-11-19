// Station.cc: Representation of the station beam former.
//
// Copyright (C) 2022 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "station.h"
#include "common/mathutils.h"
#include "beamformerlofar.h"

using namespace everybeam;
using everybeam::coords::ITRFDirection;

constexpr double kInvalidTime = -1;

Station::Station(const std::string& name, const vector3r_t& position,
                 const Options& options)
    : name_(name),
      position_(position),
      phase_reference_(position),
      element_response_(ElementResponse::GetInstance(options, name)),
      time_cache_{kInvalidTime},
      ncp_(vector3r_t{0.0, 0.0, 1.0}),
      ncp_pol0_(vector3r_t{1.0, 0.0, 0.0}) {}

void Station::UpdateTime(double time) {
  if (time_cache_ != time) {
    cached_ncp_ = NCP(time);
    cached_ncp_pol0_ = NCPPol0(time);
    time_cache_ = time;
  }
}

void Station::SetAntenna(std::shared_ptr<Antenna> antenna) {
  antenna_ = antenna;

  // The antenna can be either an Element or a BeamFormer
  // If it is a BeamFormer we recursively extract the first antenna
  // until we have a BeamFormerLofar or an Element.
  //
  // The extraction returns copies so antenna_ remains unchanged.
  // The element that is found is used in ComputeElementResponse to
  // compute the element response.

  while (auto beamformer = std::dynamic_pointer_cast<BeamFormer>(antenna)) {
    antenna = beamformer->ExtractAntenna(0);
  }

  // If we can cast to BeamFormerLofar, then extract the Element - please
  // note that the Element was upcasted from an ElementHamaker into an Element
  // in BeamFormerLofarHBA/LBA::Clone()!- and Transform the Element with the
  // coordinate system of the HBA/LBA beam former.
  if (auto beamformer_lofar = dynamic_cast<BeamFormerLofar*>(antenna.get())) {
    element_ = beamformer_lofar->GetElement();
    element_->Transform(beamformer_lofar->GetCoordinateSystem());
  } else {
    element_ = std::dynamic_pointer_cast<Element>(antenna);
  }
}

// ========================================================
void Station::ComputeElementResponse(aocommon::MC2x2* result, double time,
                                     std::span<const double> freqs,
                                     const vector3r_t& direction, size_t id,
                                     bool is_local, bool rotate) const {
  Antenna::Options options;
  options.rotate = rotate;

  if (rotate) {
    const vector3r_t ncp_t = NCP(time);
    const vector3r_t east = normalize(cross(ncp_t, direction));
    const vector3r_t north = cross(direction, east);
    options.east = east;
    options.north = north;
  }

  if (is_local) {
    element_->LocalResponse(result, *element_response_, time, freqs, direction,
                            id, options);
  } else {
    element_->ResponseID(result, *element_response_, time, freqs, direction, id,
                         options);
  }
}

void Station::ComputeElementResponse(aocommon::MC2x2* result, double time,
                                     std::span<const double> freqs,
                                     const vector3r_t& direction, bool is_local,
                                     bool rotate) const {
  ComputeElementResponse(result, time, freqs, direction,
                         element_->GetElementID(), is_local, rotate);
}

void Station::Response(aocommon::MC2x2* result, double time,
                       std::span<const double> freqs,
                       const vector3r_t& direction,
                       std::span<const double> reference_freqs,
                       const vector3r_t& station0, const vector3r_t& tile0,
                       const bool rotate) const {
  Antenna::Options options;
  options.reference_freqs = reference_freqs;
  options.station0 = station0;
  options.tile0 = tile0;
  options.rotate = rotate;

  if (rotate) {
    const vector3r_t ncp_t = NCP(time);
    const vector3r_t east = normalize(cross(ncp_t, direction));
    const vector3r_t north = cross(direction, east);
    options.east = east;
    options.north = north;
  }

  antenna_->Response(result, *element_response_, time, freqs, direction,
                     options);
}

void Station::Response(aocommon::MC2x2* result, BeamMode mode, double time,
                       std::span<const double> freqs,
                       const vector3r_t& direction,
                       std::span<const double> reference_freqs,
                       const vector3r_t& station0, const vector3r_t& tile0,
                       const bool is_local, const bool rotate) const {
  switch (mode) {
    case BeamMode::kNone:
      std::fill_n(result, freqs.size(), aocommon::MC2x2::Unity());
      break;
    case BeamMode::kFull:
      Response(result, time, freqs, direction, reference_freqs, station0, tile0,
               rotate);
      break;
    case BeamMode::kArrayFactor: {
      std::vector<aocommon::MC2x2Diag> array_factor(freqs.size());
      ArrayFactor(array_factor.data(), time, freqs, direction, reference_freqs,
                  station0, tile0);
      for (size_t f = 0; f < freqs.size(); f++) {
        result[f] = aocommon::MC2x2(array_factor[f]);
      }
    } break;
    case BeamMode::kElement:
      ComputeElementResponse(result, time, freqs, direction, is_local, rotate);
      break;
    default:
      throw std::runtime_error("Invalid mode");
  }
}

void Station::ArrayFactor(aocommon::MC2x2Diag* result, double time,
                          std::span<const double> freqs,
                          const vector3r_t& direction,
                          std::span<const double> reference_freqs,
                          const vector3r_t& station0,
                          const vector3r_t& tile0) const {
  assert(freqs.size() == reference_freqs.size());
  Antenna::Options options;
  options.reference_freqs = reference_freqs;
  options.station0 = station0;
  options.tile0 = tile0;
  antenna_->ArrayFactor(result, time, freqs, direction, options);
}

vector3r_t Station::NCP(double time) const {
  if (time != time_cache_) {
    return ncp_.at(time);
  }
  return cached_ncp_;
}

vector3r_t Station::NCPPol0(double time) const {
  if (time != time_cache_) {
    return ncp_pol0_.at(time);
  }
  return cached_ncp_pol0_;
}
