import os

import h5py
import numpy as np

import everybeam

DATA_DIR = os.environ["DATA_DIR"]


def test_lwa_values():
    """Test that the E-fields calculated by Everybeam for LWA using spherical harmonics fitting is equal to the E-fields in the simulations file"""

    lwa = everybeam.ElementResponse.create("lwa")

    # Create a theta-phi grid containing some of the points in the
    # simulation file, so that the processing is faster
    phi_deg = [0, 18, 36, 54, 72, 90]
    theta_deg = [0, 40, 80, 120, 160, 200, 240, 280, 320, 360]
    phi = np.radians(phi_deg)
    theta = np.radians(theta_deg)
    phigrid, thetagrid = np.meshgrid(theta, phi)
    phi_plot = phigrid.flatten()
    theta_plot = thetagrid.flatten()

    # Pick only 3 frequencies to ensure a reasonable processing time
    freqs = np.array([1.0e07, 5.0e07, 1.0e08])

    pol_1_everybeam = np.zeros(
        (2, len(freqs), len(phi), len(theta)), dtype=complex
    )
    pol_2_everybeam = np.zeros(
        (2, len(freqs), len(phi), len(theta)), dtype=complex
    )

    station_id = np.full((len(phi) * len(theta), 1), 0)
    for freq_idx in np.arange(len(freqs)):
        freq_array = np.full((len(phi) * len(theta), 1), freqs[freq_idx])

        x = lwa.response(
            station_id.flatten(),
            freq_array.flatten(),
            theta_plot.flatten(),
            phi_plot.flatten(),
        )

        x_reshaped = x.reshape((len(phi), len(theta), 2, 2))

        pol_1_everybeam[0, freq_idx, :, :] = x_reshaped[:, :, 0, 0]
        pol_1_everybeam[1, freq_idx, :, :] = x_reshaped[:, :, 0, 1]
        pol_2_everybeam[0, freq_idx, :, :] = x_reshaped[:, :, 1, 0]
        pol_2_everybeam[1, freq_idx, :, :] = x_reshaped[:, :, 1, 1]

    data_path = os.path.join(DATA_DIR, "OVRO_LWA_FEKO_TEST.h5")
    h5 = h5py.File(data_path, "r")

    X_pol_e_theta = np.array(h5["X-pol_Efields/etheta"])
    X_pol_e_phi = np.array(h5["X-pol_Efields/ephi"])
    Y_pol_e_theta = np.array(h5["Y-pol_Efields/etheta"])
    Y_pol_e_phi = np.array(h5["Y-pol_Efields/ephi"])

    # Select the points in the simulation file corresponding to the phi-theta
    # grid used in everybeam
    X_pol_e_theta = X_pol_e_theta[:, phi_deg, :][:, :, theta_deg]
    X_pol_e_phi = X_pol_e_phi[:, phi_deg, :][:, :, theta_deg]
    Y_pol_e_theta = Y_pol_e_theta[:, phi_deg, :][:, :, theta_deg]
    Y_pol_e_phi = Y_pol_e_phi[:, phi_deg, :][:, :, theta_deg]

    pol_1_simulation = np.stack((X_pol_e_theta, X_pol_e_phi))
    pol_2_simulation = np.stack((Y_pol_e_theta, Y_pol_e_phi))

    np.testing.assert_allclose(
        pol_1_everybeam, pol_1_simulation, rtol=1e-10, atol=0.0015
    )
    np.testing.assert_allclose(
        pol_2_everybeam, pol_2_simulation, rtol=1e-10, atol=0.0016
    )
