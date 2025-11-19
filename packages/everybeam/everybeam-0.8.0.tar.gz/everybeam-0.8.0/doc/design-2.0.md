# EveryBeam design

## Outline

1. Intro - audience - Problem statement
2. Use cases
3. Requirements and principles
4. Problems with the structure
5. Solution Outline

## 1. Intro

EveryBeam grew out of the old package LOFARBeam, and included models for many other telescopes. Some of the design decisions for LOFARBeam were not incorporated into EveryBeam, and the use cases have changed over time. Therefore, it is time to reconsider the design of EveryBeam.

Beam evaluation is a substantial part of the LOFAR pipelines (and also of future SKA pipelines), so performance should be considered in the design.

There is friction between generalization and optimization.

## 2. Use Cases
- DP3
- wsclean, facets, aterms
- filter skymodel (python)
- commissioning
- algorithm development


## 3. Requirements

- EveryBeam should have C++ and Python interface that are extremely similar (i.e. no domain logic in wrappers).
- Performance: EveryBeam should use system resources efficiently:
  - Use vectorization where possible
  - Use `--fastmath` where useful and possible
  - Enable usage of multithreading:
    - be thread safe (i.e. everybeam gets called from multiple threads)
    - use multithreading (i.e. everybeam makes multiple threads)
- EveryBeam should be extendable:
  - It should be easy to add new element models
  - It should be possible to add alternative (not purely geometric) beamformers
  - EveryBeam should support different types of telescope mounts (Alt-azimuth, earth-bound, equatorial, Naysmith, ...)
  - It should be possible to add new elements and beamformers without touching the rest of the code
- It should be possible to construct EveryBeam objects from scratch, or from a MeasurementSet
- Clean design: no code duplication between types of telescopes
- Polarization should be correctly handled, with optional fixing of the polarization coordinate frame over multiple evaluations.
- EveryBeam should take care of coordinate conversions between the element model and the requested evaluation direction(s). It should support at least J2000, ITRF and element local coordinates.
- OPTIONAL? Can X and Y be flagged independently.
- OPTIONAL? Evaluate only the Array Factor or only the Element response.


## 4. Problems with the current structure

* Performance:
  * Too much freedom to change the structure afterwards: Initially it was possible to choose a different ElementResponse.
  * Top down, depth first evaluation

* Coordinate system per Antenna

* Dish based telescopes, with different coordinate systems, were added afterwards and have their own interface.

* Specific types of telescopes have different classes with different interfaces

* Different optimizations led to different functions, which basically do the same thing but changing the order of loops.

* In principle, in the current design, only ElementResponse should be specific to an instrument, but specializations were made all over the code.

* The python interface is different than the C++ interface. Some optimizations happen in the Python interface.

* The flags `rotate` anb `is_local` are ad hoc, with a proper design these should not be necessary.


## 5. Solution Outline

### Main idea

**Composable**: Response for various telescopes can be built from standard components, e.g.
* Elements
* BeamFormers
* Mount
* ElementResponse

SphericalHarmonics can be a reusable class for many element responses, with a datafile specific for the instrument.


### Possible optimizations

* Evaluating Spherical Harmonics basis functions is expensive and should be reused where possible.
* Many LOFAR core stations use the same coordinate system, which could be used to reduce evaluations of:
  1. The element model (Hamaker)
  2. The spherical harmonic basis functions.
* Bottom-up evalutation or flattening of 'beam-former-tree' could enable vectorization.

### Interface

During construction of the EveryBeam object, the total setup of the system (including the element response model) should be known so that possible optimizations can be prepared.

There could be only one call for evaluating the beam response, where each of the axes can be length one or a vector. The axes are:
- Time
- Frequency
- Station
- Direction

Options for this call are:
- Fixing the polarization frame over directions
- Specify the coordinate system of direction (how??)

This function should have intelligence to find an efficient evaluation.

Design ideas:
* No implicit caching: explicit is better than implicit
* Tell upfront what you are doing, make large requests and let EveryBeam optimize




### New design

* Construction
  - Composition from basic elements
  - Add be coordinate system(s) that allow dish based telescopes to be
  treated on equal footing to (fixed to earth) phased array
* Planning / Optimization
  - Aggregate elements in the same coordinate system in groups
  - Flatten beamformer hierarchy
* Evaluation
  - Bottom up, starting at the elements
  - const function, thread safe, no caching


* Optimizations
  - beamformer identical elements
  - array factor
  - skip computation of beamformer weights
  - beamform basefunctions (order of matrix multiplications)