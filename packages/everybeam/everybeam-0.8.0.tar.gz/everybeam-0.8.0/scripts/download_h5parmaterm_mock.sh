#!/bin/sh
# Copyright (C) 2020 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

# Author: Jakob Maljaars
# Email: jakob.maljaars_@_stcorp.nl

# Script for downloading a mock h5parm file
# for testing the H5ParmATerms

set -e

H5PARMATERM_MOCK=H5PARMATERM_MOCK.h5
if [ ! -f ${H5PARMATERM_MOCK} ] ; then
    wget -q https://support.astron.nl/software/ci_data/EveryBeam/${H5PARMATERM_MOCK}
fi