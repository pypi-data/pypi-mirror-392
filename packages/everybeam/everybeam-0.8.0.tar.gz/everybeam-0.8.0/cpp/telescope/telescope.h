// telescope.h: Base class for computing the Telescope response.
//
// Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_TELESCOPE_TELESCOPE_H_
#define EVERYBEAM_TELESCOPE_TELESCOPE_H_

#include <limits>
#include <memory>

#include <aocommon/coordinatesystem.h>

#include "../options.h"

namespace everybeam {

namespace griddedresponse {
class GriddedResponse;
}

namespace pointresponse {
class PointResponse;
}

namespace telescope {

/**
 * @brief Telescope class, forming the base class for specific telescopes.
 *
 */
class Telescope {
 public:
  virtual ~Telescope(){};

  /**
   * @brief Return the gridded response object
   *
   * @param coordinate_system Coordinate system struct
   * @return GriddedResponse::Ptr
   */
  virtual std::unique_ptr<griddedresponse::GriddedResponse> GetGriddedResponse(
      const aocommon::CoordinateSystem& coordinate_system) const = 0;

  /**
   * @brief Get the Point Response object
   *
   * @param time Time, modified Julian date, UTC, in seconds (MJD(UTC), s).
   * @return std::unique_ptr<pointresponse::PointResponse>
   */
  virtual std::unique_ptr<pointresponse::PointResponse> GetPointResponse(
      double time) const = 0;

  bool GetIsTimeRelevant() const { return is_time_relevant_; };
  std::size_t GetNrStations() const { return n_stations_; };
  Options GetOptions() const { return options_; };

  // Set the time at which the station axes will be
  // precomputed.
  // Setting the time is important if you want to speed up
  // the calculation of many direction at a specific time.
  void SetTime(double time) {
    if (time_ != time) {
      ProcessTimeChange(time);
      time_ = time;
    }
  };
  double GetTime(double time) { return time_; };

 protected:
  /**
   * @brief Construct a new Telescope object
   *
   * @param ms MeasurementSet
   * @param options telescope options
   */
  Telescope(std::size_t n_stations, const Options& options)
      : n_stations_(n_stations), options_(options){};

  void SetIsTimeRelevant(bool is_time_relevant) {
    is_time_relevant_ = is_time_relevant;
  };

  virtual void ProcessTimeChange(double time){};

 private:
  std::size_t n_stations_;
  Options options_;
  bool is_time_relevant_ = true;
  double time_ = std::numeric_limits<double>::min();
};

}  // namespace telescope
}  // namespace everybeam

#endif  // EVERYBEAM_TELESCOPE_TELESCOPE_H_
