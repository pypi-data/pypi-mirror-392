#!/bin/sh
# Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: GPL-3.0-or-later

# Script for downloading and expanding a single compressed file.

set -e

COMPRESSED_FILE_NAME=$1
EXPANDED_FILE_NAME=$2

if [ ! -f $EXPANDED_FILE_NAME ]; then
    if [ ! -f $COMPRESSED_FILE_NAME ]; then
        wget -q https://support.astron.nl/software/ci_data/EveryBeam/$COMPRESSED_FILE_NAME
    fi
    tar -xf $COMPRESSED_FILE_NAME
    rm -f $COMPRESSED_FILE_NAME
fi
