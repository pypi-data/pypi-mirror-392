#include "dsa110.h"

#include "../griddedresponse/airygrid.h"
#include "../pointresponse/airypoint.h"
#include "../common/casautils.h"

#include <casacore/measures/TableMeasures/ArrayMeasColumn.h>

using everybeam::griddedresponse::AiryGrid;
using everybeam::griddedresponse::GriddedResponse;
using everybeam::pointresponse::AiryPoint;
using everybeam::pointresponse::PointResponse;

namespace everybeam::telescope {

Dsa110::Dsa110(const casacore::MeasurementSet& ms,
               const everybeam::Options& options)
    : Telescope(ms.antenna().nrow(), options) {
  directions_ = common::ReadDelayDirections(ms.field(), ms.antenna());

  casacore::MSAntenna antenna_table = ms.antenna();
  const size_t n_antennas = ms.antenna().nrow();
  // From information from Erwin de Blok:
  // The dish is 4.65 meter, and has a blocked aperture of 16 inches (40.64 cm).
  // At 1.4 GHz, the FWHM of the primary beam is 2.9 degrees, so at 1.0 GHz it
  // is 4.1 degrees. The lowest usable frequency is 500 MHz. Because the FWHM at
  // 1 GHz is at 4.1 degrees. The beam can be trimmed at 8 degrees.
  const common::AiryParameters dsa_parameters{4.65, 0.4064, 8.0 * 60.0};
  parameters_.assign(n_antennas, dsa_parameters);

  SetIsTimeRelevant(false);
}

std::unique_ptr<GriddedResponse> Dsa110::GetGriddedResponse(
    const aocommon::CoordinateSystem& coordinate_system) const {
  return std::make_unique<AiryGrid>(this, coordinate_system, parameters_,
                                    directions_, true);
}

std::unique_ptr<PointResponse> Dsa110::GetPointResponse(double time) const {
  return std::make_unique<AiryPoint>(this, time, parameters_, directions_,
                                     true);
}

}  // namespace everybeam::telescope
