# EveryBeam Changelog

## 0.8.0 (2025-11-18)

- Add `CreateTelescope` function for creating `Telescope` objects from metadata, without supplying a Measurement Set. Add a Python `create_telescope` binding for this function. This function currently only supports creating OSKAR telescopes.
- Remove `CorrectionMode` and correctionmode.h. Use `BeamMode` from beammode.h instead.
- Add OskarElementResponseDipoleCos beam model which replaces OskarElementResponseDipoleCos2.
- Drop support for Python 3.8.
- Add SKALowElementResponse.

## 0.7.4 (2025-09-22)

- Replace fixed 1 m dipoles with half-wavelength dipoles in OSKAR dipole model.

## 0.7.3 (2025-09-05)

- Add new point response interface.

## 0.7.2 (2025-07-29)

- Add support for DSA-110 using an Airy beam pattern
- Add OskarElementResponseDipoleCos2 beam model as a placeholder for the SKA Low beam model during early commissioning
- Many small improvements

## 0.7.1 (2025-03-10)

- Add overloads for evaluating multiple frequencies at once.
- Bugfix: Evaluate both dipoles in OSKAR dipole model.

## 0.7.0 (2025-01-23)

- Add EveryBeam design document.
- Add response functions for evaluating the response for a list of frequencies instead of one by one, to allow optimizations.
- EveryBeam now makes use of C++20 and requires Casacore 3.6.0 or higher to compile.
- API Change: Use `double`/`std::complex<double>` instead of `real_t`/`complex_t` type aliases.
- Bugfix: Replace `reinterpret_cast`s which could cause segmentation faults when using AVX.
- Use OSKAR dipole model by default for OSKAR telescope.
- When using EveryBeam from Python, determine the element response model from the Measurement Set by default instead of using 'hamaker' as default model.

## 0.6.2 (2024-11-21)

- Last release without C++20 features.

## 0.6.1 (2024-08-15)

- Avoid conflicts when using the "everybeam" Python module together with other Python module(s) that contain Casacore.
- Do not install XTensor headers when installing EveryBeam.
- Optimize BeamFormer::ComputeGeometricResponse using -ffast-math.

## 0.6.0 (2024-05-16)

- Allow averaging over squared Mueller matrices. This required an API change that affects WSClean, which is why this version has an increased minor version.
- Allow telescope OVRO-LWA with dash.
- Fix an issue with missing cblas functions.
- Remove duplicate LocalResponse overload.

## 0.5.8 (2024-04-11)

- Fix AVX-enabled EveryBeam
- Implement caching for NCP direction, which speeds up computation of e.g. DP3 Predict.

## 0.5.7
- Implement Response function for dish telescopes, to enable usage in DP3.
- EveryBeam no longer indirectly depends on the GSL library, via schaapcommon.
