.. _lofardemoarrayfactor:

LOFAR telescope: correcting for the array factor in a given direction
=====================================================================

The EveryBeam Python bindings can be used to evaluate the station response in an arbitrary equatorial direction. This demo illustrates in a step-by-step manner how to do this. The complete code is shown at the bottom of this page.

It all starts with importing the ``everybeam`` python module, along with any other libraries that are needed for your project, and by specifying a path to the Measurement Set that will be used:

.. code-block:: python

    from astropy.coordinates import AltAz, EarthLocation, ITRS, SkyCoord
    from astropy.time import Time

    import astropy.units as u
    import everybeam as eb
    import numpy as np

    # Set path to LOFAR LBA MS and load telescope
    ms_path = "/path/to/my.ms"

The telescope can now be loaded with ``eb.load_telescope``. This should return an instance of a  ``LOFAR`` telescope.

.. code-block:: python

    telescope = eb.load_telescope(ms_path)
    assert type(telescope) == eb.LOFAR

Please note that since no optional arguments were passed to ``load_telescope``, no differential beam will applied and the default element response model (``"Hamaker"``) will be used.

In order to evaluate the array factor, we need to pass some user input. This includes a time, station index, frequency, the direction for which we want to know the array factor, and the reference direction (where the array factor is unity). For the ``array_factor`` method these coordinates need to be in ITRF coordinates. We therefore also need to convert from equatorial IRCS (J2000) coordinates to ITRF coordinates.

First, let's read observation time, frequency and pointing direction information from the Measurement Set.

.. code-block:: python

    import casacore.tables as pt
    # Time slots at which to evaluate the beam response.
    ms_times = pt.taql('SELECT DISTINCT TIME FROM {ms:s}'.format(ms=ms_path))
    times = ms_times.getcol('TIME')

    # Frequencies at which to evaluate the beam response.
    ms_freqs = pt.taql('SELECT CHAN_FREQ FROM {ms:s}::SPECTRAL_WINDOW'.format(ms=ms_path))
    freqs = ms_freqs.getcol('CHAN_FREQ').squeeze()

    # Obtain the reference direction from the Measurement Set.
    ms_dirs = pt.taql('SELECT REFERENCE_DIR FROM {ms:s}::FIELD'.format(ms=ms_path))
    ra_ref, dec_ref = ms_dirs.getcol('REFERENCE_DIR').squeeze()


Next, define a few (phase) directions for which we would like to calculate the array factor. We need two separate arrays for RA and Dec. The directions should also be in ICRS (J2000) in units of radians.

.. code-block:: python

    # Choose three random directions (units in radians), and create separate RA and DEC arrays.
    ra, dec = list(zip((1.34, 1.56), (0.78, -0.14), (-0.57, 0.38)))

Now that we have our initial information we can calculate the ITRF coordinates. We use AstroPy's coordinate transformations to obtain the coordinates as cartesian coordinates in ITRS. Let's define a function for this, because we will need it more often.

.. code-block:: python

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
        obstime = Time(time/3600/24, scale='utc', format='mjd')
        dir_pointing = SkyCoord(ra, dec)
        dir_pointing_itrs = dir_pointing.transform_to(ITRS(obstime=obstime))
        return np.asarray(dir_pointing_itrs.cartesian.xyz.transpose())

.. note::

    Our ``radec_to_xyz`` function can take arrays of RA and Dec, and an array of times, but `not` simultaneously. So, either calculate the ITRF coordinates for a `single` direction for an array of MJD times, or calculate the ITRF coordinates for an array of directions for a `single` MJD time.

Next, convert the reference direction and our (phase) directions of interest to ITRF. Note that the coordinates in ITRF are time-dependent, due to the rotation of the earth. So let's use the first time slot, and select five stations.

.. code-block:: python

    # ITRF coordinates of the reference direction.
    reference_xyz = radec_to_xyz(ra_ref * u.rad, dec_ref * u.rad, times[0])
    # ITRF coordinates of the phase centre to correct the array factor for.
    phase_xyz = radec_to_xyz(ra * u.rad, dec * u.rad, times[0])
    # Station IDs for which we want to calculate the array factor.
    station_ids = [0, 3, 6, 14, 23]

We're all set now to compute the array factor response using the ``array_factor`` method. Let's calculate it for the given station ID and the first time slot:

.. code-block:: python

    array_factor = telescope.array_factor(times[0], station_ids, freqs, phase_xyz, reference_xyz)

This returns a 5-dimensional array. The outermost (first) dimension is the station ID (``len(station_ids)``), the second is the frequency (``len(freqs)``), the third is the array of phase directions (``len(ra)`` or ``len(dec)``), and the two innermost (fourth and fifth) are a 2x2 array with the response of the XX, XY, YX and YY.

.. note::

    ``array_factor`` will always return a squeezed array, if you use scalar values for ``station_ids``, ``freqs``, or ``phase_xyz``. Hence, it will return a 2-dimensional array if you calculate the array factor for a single station, for a single frequency, for a single phase direction.


Since EveryBeam's methods do not take arrays of time, you will need to calculate the array factor for the full time range using a loop:

.. code-block:: python

    # Create an empty 6-dim complex numpy array to hold the array factor for each time slot
    timeslices = np.empty((len(times), len(station_ids), len(freqs), len(ra), 2, 2), dtype=np.complex128)
    for idx, time in enumerate(times):
        reference_xyz = radec_to_xyz(ra_ref * u.rad, dec_ref * u.rad, time)
        phase_xyz = radec_to_xyz(ra * u.rad, dec * u.rad, time)
        beam = telescope.array_factor(time, station_ids, freqs, phase_xyz, reference_xyz)
        timeslices[idx] = beam

.. caution::

    The code above merely serves an educational purpose, demonstrating how one can collect all the desired information in one big NumPy array. In practice, you will neither want to calculate the array factor for every time slot in the Measurement Set, nor for every frequency channel. The array factor will change slowly over time and frequency. Hence, calculating it once every 15 minutes or so, for just a couple of frequencies, usually suffices in practice.

A complete overview of the code is shown below:

.. literalinclude:: ../../../demo/python/lofararrayfactor.py
