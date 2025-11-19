#!/bin/bash
#
# This script should be called by `cibuildwheel` in the `before-build` stage.

set -euo pipefail
pip install --upgrade pip
pip install oldest-supported-numpy
