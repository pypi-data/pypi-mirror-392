// Copyright (C) 2022 ASTRON (Netherlands Institute for Radio Astronomy)
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef EVERYBEAM_ANTENNA_H
#define EVERYBEAM_ANTENNA_H

#include <complex>
#include <memory>
#include <iostream>
#include <span>

#include <aocommon/matrix2x2.h>
#include <aocommon/matrix2x2diag.h>

#include "common/types.h"
#include "elementresponse.h"
#include "stationnode.h"

namespace everybeam {

/**
 * @brief Abstract class describing an antenna, and computing the
 * corresponding Response() and ArrayFactor(). \c Element and \c BeamFormer
 * classes - and childs thereof - inherit from this class.
 */
class Antenna {
 public:
  /**
   * @brief Struct containing antenna options
   *
   */
  struct Options {
    std::span<const double>
        reference_freqs;  //!< %Antenna reference frequencies (Hz), one for each
                          //!< channel.
    vector3r_t station0;  //!< Reference direction (ITRF, m)
    vector3r_t tile0;     //!< Tile beam former reference direction (ITRF, m).
    bool rotate;          //!< If paralactic rotation should be applied.
    vector3r_t east;      //!< Eastward pointing unit vector
    vector3r_t north;     //!< Northward pointing unit vector
  };

  /**
   * @brief Construct a new %Antenna object
   *
   */
  Antenna()
      :  // default coordinate system
         // no shift of origin, no rotation
        Antenna(kIdentityCoordinateSystem) {}

  /**
   * @brief Construct a new %Antenna object, given a coordinate system
   *
   * @param coordinate_system
   */
  Antenna(const StationCoordinateSystem& coordinate_system)
      :  // default phase reference system is the origin of the coordinate
         // system
        Antenna(coordinate_system, coordinate_system.origin) {}

  virtual ~Antenna(){};

  /**
   * @brief Construct a new %Antenna object, given a coordinate system and a
   * phase reference position.
   *
   * @param coordinate_system Coordinate system
   * @param phase_reference_position Phase reference position (ITRF, m)
   * @param is_x_enabled Enables or disables the X polarization.
   * @param is_y_enabled Enables or disables the Y polarization.
   */
  Antenna(const StationCoordinateSystem& coordinate_system,
          const vector3r_t& phase_reference_position, bool is_x_enabled = true,
          bool is_y_enabled = true);

  /**
   * @brief Construct a new Antenna object
   *
   * @param phase_reference_position Phase reference position (ITRF, m)
   */
  Antenna(const vector3r_t& phase_reference_position)
      : Antenna(StationCoordinateSystem(phase_reference_position,
                                        StationCoordinateSystem::kIdentityAxes),
                phase_reference_position) {}
  /**
   * @brief Makes a copy of this Antenna object
   *
   * The method is virtual, so that copies can be created from a pointer
   * to the base (Antenna) class.
   * The original remains unchanged, therefore the method is const.
   * The method has no implementation in the Antenna class, because
   * Antenna is abstract, so no copy can be instantiated.
   *
   * This method is used by the ExtractAntenna method of the BeamFormer
   * class to create a copy of one of the Antennas it contains.
   */
  virtual std::shared_ptr<Antenna> Clone() const = 0;

  /**
   * @brief Transform internal coordinate systems and positions
   *
   * @param coordinate_system to apply in the transformation
   *
   * This method is used by BeamFormer::ExtractAntenna to lift
   * an antenna out of the beamformer.
   *
   * The transformation is needed because the coordinate system of
   * an antenna in a beamformer is expressed in terms of
   * the coordinate system of the beamformer.
   * To turn an embedded antenna into a stand-alone antenna,
   * the coordinate system of the beamformer needs to be
   * applied to the coordinate system of the antenna
   */
  void Transform(const StationCoordinateSystem& coordinate_system);

  /**
   * @brief Compute the %Antenna Response
   *
   * @param time Time, modified Julian date, UTC, in seconds (MJD(UTC), s).
   * @param freq Frequency of the plane wave (Hz).
   * @param direction Direction of arrival (ITRF, m).
   * @param options
   */
  virtual void Response(aocommon::MC2x2* result,
                        const ElementResponse& element_response, double time,
                        const std::span<const double>& freqs,
                        const vector3r_t& direction,
                        const Options& options = {}) const {
    // Transform direction and directions in options to local coordinatesystem
    vector3r_t local_direction = TransformToLocalDirection(direction);
    Options local_options;
    local_options.reference_freqs = options.reference_freqs;
    local_options.station0 = TransformToLocalDirection(options.station0);
    local_options.tile0 = TransformToLocalDirection(options.tile0);
    local_options.rotate = options.rotate;
    local_options.east = TransformToLocalDirection(options.east);
    local_options.north = TransformToLocalDirection(options.north);
    LocalResponse(result, element_response, time, freqs, local_direction,
                  local_options);
  }

  /**
   * @brief Compute the array factor of the antenna
   *
   * @param time Time, modified Julian date, UTC, in seconds (MJD(UTC), s).
   * @param freq Frequency of the plane wave (Hz).
   * @param direction Direction of arrival (ITRF, m).
   * @param options
   */
  virtual void ArrayFactor(aocommon::MC2x2Diag* result, double time,
                           const std::span<const double>& freqs,
                           const vector3r_t& direction,
                           const Options& options) const {
    // Transform direction and directions in options to local coordinatesystem
    const vector3r_t local_direction = TransformToLocalDirection(direction);
    Options local_options;
    local_options.reference_freqs = options.reference_freqs;
    local_options.station0 = TransformToLocalDirection(options.station0);
    local_options.tile0 = TransformToLocalDirection(options.tile0);
    LocalArrayFactor(result, time, freqs, local_direction, local_options);
  }

  const StationCoordinateSystem& GetCoordinateSystem() const {
    return coordinate_system_;
  }

  const vector3r_t& GetPhaseReferencePosition() const {
    return phase_reference_position_;
  }

  /**
   * @param i Polarization index: 0 or 1.
   * @return If the requested polarization is enabled.
   */
  bool IsEnabled(std::size_t i) const { return enabled_[i]; }

  /**
   * @param is_x_enabled Enables or disables the X polarization.
   * @param is_y_enabled Enables or disables the Y polarization.
   */
  void SetEnabled(bool is_x_enabled, bool is_y_enabled) {
    enabled_[0] = is_x_enabled;
    enabled_[1] = is_y_enabled;
  }

 protected:
  vector3r_t TransformToLocalDirection(const vector3r_t& direction) const;

 private:
  virtual void LocalResponse(aocommon::MC2x2* result,
                             const ElementResponse& element_response,
                             double time, const std::span<const double>& freqs,
                             const vector3r_t& direction,
                             const Options& options) const = 0;

  virtual void LocalArrayFactor(aocommon::MC2x2Diag* result,
                                [[maybe_unused]] double time,
                                const std::span<const double>& freqs,
                                [[maybe_unused]] const vector3r_t& direction,
                                [[maybe_unused]] const Options& options) const {
    std::fill_n(result, freqs.size(), aocommon::MC2x2Diag::Unity());
  }

  StationCoordinateSystem coordinate_system_;
  vector3r_t phase_reference_position_;
  std::array<bool, 2> enabled_;
};

}  // namespace everybeam
#endif
