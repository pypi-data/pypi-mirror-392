// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#include "airygrid.h"
#include "../telescope/alma.h"
#include "../circularsymmetric/voltagepattern.h"

using aocommon::HMC4x4;
using aocommon::UVector;

namespace everybeam {
namespace griddedresponse {

void AiryGrid::Response([[maybe_unused]] BeamMode beam_mode,
                        std::complex<float>* buffer,
                        [[maybe_unused]] double time, double frequency,
                        size_t station_idx, size_t field_id) {
  // TODO merge this implementation with the SkaMidTelescope class, which
  // also implements an Airy disc (see also AST-1376).

  const double pdir_ra = directions_[field_id].first;
  const double pdir_dec = directions_[field_id].second;
  const common::AiryParameters& parameters = airy_parameters_[station_idx];
  circularsymmetric::VoltagePattern vp({frequency},
                                       parameters.maximum_radius_arcmin);
  vp.EvaluateAiryDisk(parameters.dish_diameter_in_m,
                      parameters.blocked_diameter_in_m);
  vp.Render(buffer, width_, height_, dl_, dm_, ra_, dec_, pdir_ra, pdir_dec,
            l_shift_, m_shift_, frequency);
}

void AiryGrid::ResponseAllStations(BeamMode beam_mode,
                                   std::complex<float>* buffer, double time,
                                   double frequency, size_t field_id) {
  if (is_homogeneous_)
    HomogeneousAllStationResponse(beam_mode, buffer, time, frequency, field_id);
  else
    InhomogeneousAllStationResponse(beam_mode, buffer, time, frequency,
                                    field_id);
}

}  // namespace griddedresponse
}  // namespace everybeam
