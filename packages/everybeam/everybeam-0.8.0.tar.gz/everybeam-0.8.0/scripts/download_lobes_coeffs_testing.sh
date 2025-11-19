#!/bin/sh
# Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

# Script for downloading and extracting the LOBES coefficients into
# the current directory. When invoked from within CMake, CMake should set
# the proper WORKING_DIRECTORY.
set -e
# Download the h5 coefficient files in case they're not present (-nc option) in the coeffs/lobes directory
echo "Start downloading LOBES coefficients needed for unit tests (~2.5 GB)"

# Download all the required coefficients for AARTFAAC-12 and other unit tests.
wget --progress=dot:giga -r -nc -nH -nd --no-parent -A 'LOBES_CS302LBA.h5,LOBES_CS001LBA.h5,
LOBES_CS002LBA.h5,LOBES_CS003LBA.h5,LOBES_CS004LBA.h5,LOBES_CS005LBA.h5,LOBES_CS006LBA.h5,
LOBES_CS007LBA.h5,LOBES_CS011LBA.h5,LOBES_CS013LBA.h5,LOBES_CS017LBA.h5,LOBES_CS021LBA.h5,
LOBES_CS032LBA.h5' https://support.astron.nl/software/lobes/

echo "Finished downloading LOBES coefficients"