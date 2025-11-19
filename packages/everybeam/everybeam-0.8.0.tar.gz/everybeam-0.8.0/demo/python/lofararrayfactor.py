#!/usr/bin/env python3
# Copyright (C) 2021 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

import astropy.units as u
import casacore.tables as pt
import numpy as np
from astropy.coordinates import ITRS, SkyCoord
from astropy.time import Time

import everybeam as eb


def radec_to_xyz(ra, dec, time):
    """
    Convert RA and Dec ICRS coordinates to ITRS cartesian coordinates.

    Args:
        ra (astropy.coordinates.Angle): Right ascension
        dec (astropy.coordinates.Angle): Declination
        time (float): MJD time in seconds

    Returns:
        pointing_xyz (ndarray): NumPy array containing the ITRS X, Y and Z coordinates
    """
    obstime = Time(time / 3600 / 24, scale="utc", format="mjd")
    dir_pointing = SkyCoord(ra, dec)
    dir_pointing_itrs = dir_pointing.transform_to(ITRS(obstime=obstime))
    return np.asarray(dir_pointing_itrs.cartesian.xyz.transpose())


# Set path to LOFAR LBA MS and load telescope
ms_path = os.path.join(os.environ["DATA_DIR"], "LOFAR_LBA_MOCK.ms")

telescope = eb.load_telescope(ms_path)
assert type(telescope) == eb.LOFAR

# Time slots at which to evaluate the beam response.
ms_times = pt.taql("SELECT DISTINCT TIME FROM {ms:s}".format(ms=ms_path))
times = ms_times.getcol("TIME")

# Frequencies at which to evaluate the beam response.
ms_freqs = pt.taql(
    "SELECT CHAN_FREQ FROM {ms:s}::SPECTRAL_WINDOW".format(ms=ms_path)
)
freqs = ms_freqs.getcol("CHAN_FREQ").squeeze()

# Obtain the reference direction from the Measurement Set.
ms_dirs = pt.taql("SELECT REFERENCE_DIR FROM {ms:s}::FIELD".format(ms=ms_path))
ra_ref, dec_ref = ms_dirs.getcol("REFERENCE_DIR").squeeze()

# Choose three random directions (units in radians), and create separate RA and DEC arrays.
ra, dec = list(zip((1.34, 1.56), (0.78, -0.14), (-0.57, 0.38)))

# ITRF coordinates of the reference direction.
reference_xyz = radec_to_xyz(ra_ref * u.rad, dec_ref * u.rad, times[0])

# ITRF coordinates of the phase centre to correct the array factor for.
phase_xyz = radec_to_xyz(ra * u.rad, dec * u.rad, times[0])

# Station IDs for which we want to calculate the array factor.
station_ids = [0, 3, 6, 14, 23]

# Compute the array factor response
array_factor = telescope.array_factor(
    times[0], station_ids, freqs, phase_xyz, reference_xyz
)
print(
    f"\n******** array_factor {array_factor.shape} ********\n\n{array_factor}\n"
)

# Create an empty 6-dim complex numpy array to hold the array factor for each time slot
timeslices = np.empty(
    (len(times), len(station_ids), len(freqs), len(ra), 2, 2),
    dtype=np.complex128,
)
for idx, time in enumerate(times):
    reference_xyz = radec_to_xyz(ra_ref * u.rad, dec_ref * u.rad, time)
    phase_xyz = radec_to_xyz(ra * u.rad, dec * u.rad, time)
    beam = telescope.array_factor(
        time, station_ids, freqs, phase_xyz, reference_xyz
    )
    timeslices[idx] = beam
print(f"\n******** timeslices {timeslices.shape} ********\n\n{timeslices}\n")

print(
    f"timeslices[0].all() == array_factor.all(): {timeslices[0].all() == array_factor.all()}"
)
