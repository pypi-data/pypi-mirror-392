#ifndef EVERYBEAM_COMMON_AIRY_PARAMETERS_H_
#define EVERYBEAM_COMMON_AIRY_PARAMETERS_H_

namespace everybeam::common {

struct AiryParameters {
  AiryParameters(double dish_diameter, double blocked_diameter,
                 double max_radius)
      : dish_diameter_in_m(dish_diameter),
        blocked_diameter_in_m(blocked_diameter),
        maximum_radius_arcmin(max_radius) {}
  double dish_diameter_in_m;
  double blocked_diameter_in_m;
  double maximum_radius_arcmin;
};

}  // namespace everybeam::common

#endif
