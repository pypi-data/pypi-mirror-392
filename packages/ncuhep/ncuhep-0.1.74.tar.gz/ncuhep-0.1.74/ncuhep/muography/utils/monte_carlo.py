import numpy as np
import matplotlib.pyplot as plt
from numba import njit, prange
from coordinates import det2earth, earth2det, cart2projection
from tracking import track_reconstruction
from flux import geometric_factor
import time


@njit
def homogenous_generator(theta_max_deg: float, zenith_boresight_deg: float, azimuth_boresight_deg: float, simulation_half_length_x: float, simulation_half_length_y: float):
    theta_max_rad = np.radians(theta_max_deg)
    cos_theta = np.random.uniform(np.cos(theta_max_rad), 1)
    theta = np.arccos(cos_theta)
    phi = np.random.uniform(0, 2 * np.pi)

    x_pp = np.random.uniform(-simulation_half_length_x, simulation_half_length_x)
    y_pp = np.random.uniform(-simulation_half_length_y, simulation_half_length_y)
    z_pp = 0

    x_dir_det = np.sin(theta) * -np.sin(phi)
    y_dir_det = np.sin(theta) * np.cos(phi)
    z_dir_det = np.cos(theta)

    x_pos_det = 0
    y_pos_det = 0
    z_pos_det = 0

    x_pp, y_pp, z_pp = det2earth(x_pp, y_pp, z_pp, np.radians(zenith_boresight_deg), np.radians(azimuth_boresight_deg))


    x_pos_det += x_pp
    y_pos_det += y_pp
    z_pos_det += z_pp

    x_dir_earth, y_dir_earth, z_dir_earth = det2earth(x_dir_det, y_dir_det, z_dir_det, np.radians(zenith_boresight_deg), np.radians(azimuth_boresight_deg))
    x_pos_earth, y_pos_earth, z_pos_earth = det2earth(x_pos_det, y_pos_det, z_pos_det, np.radians(zenith_boresight_deg), np.radians(azimuth_boresight_deg))

    return x_pos_earth, y_pos_earth, z_pos_earth, x_dir_earth, y_dir_earth, z_dir_earth



@njit
def detection_simulation(layer_z: np.ndarray, pixel_length_x: float, pixel_length_y: float, layer_half_length_x: np.ndarray, layer_half_length_y: np.ndarray, zenith_boresight_deg: float, azimuth_boresight_deg: float, x_pos_earth: float, y_pos_earth: float, z_pos_earth: float, x_dir_earth: float, y_dir_earth: float, z_dir_earth: float, mode: int = 0):

    hits = np.zeros((len(layer_z), 3), dtype=np.float64)

    particle_dir_det = earth2det(x_dir_earth, y_dir_earth, z_dir_earth, np.radians(zenith_boresight_deg), np.radians(azimuth_boresight_deg))
    particle_pos_det = earth2det(x_pos_earth, y_pos_earth, z_pos_earth, np.radians(zenith_boresight_deg), np.radians(azimuth_boresight_deg))

    theta_x = np.arctan2(particle_dir_det[0], particle_dir_det[2])
    theta_y = np.arctan2(particle_dir_det[1], particle_dir_det[2])

    tan_theta_x = np.tan(theta_x)
    tan_theta_y = np.tan(theta_y)

    for i in range(len(layer_z)):
        hits[i, 0] = particle_pos_det[0] + (layer_z[i] - particle_pos_det[2]) * tan_theta_x
        hits[i, 1] = particle_pos_det[1] + (layer_z[i] - particle_pos_det[2]) * tan_theta_y
        hits[i, 2] = layer_z[i]

        if np.abs(hits[i, 0]) > layer_half_length_x[i] or np.abs(hits[i, 1]) > layer_half_length_y[i]:
            return hits, False

        hits[i, 0] = np.floor(hits[i, 0] / pixel_length_x) * pixel_length_x + pixel_length_x / 2
        hits[i, 1] = np.floor(hits[i, 1] / pixel_length_y) * pixel_length_y + pixel_length_y / 2


    if mode == 0:
        pass
    elif mode == 1:
        hits[:, 0] += pixel_length_x / 2
        hits[:, 1] += pixel_length_y / 2
    else:
        raise ValueError("mode must be 0 or 1")

    return hits, True

@njit(cache=True)
def chunked_unique_rounded(arr, chunk_size=10000, scale=1000, decimals=1):
    n = arr.shape[0]
    total_uniques = np.empty(n, dtype=np.float64)
    total_count = 0
    for i in range(0, n, chunk_size):
        chunk = arr[i:i+chunk_size]
        rounded = np.round(chunk * scale, decimals)
        uniques = np.unique(rounded)
        count = uniques.shape[0]
        total_uniques[total_count:total_count+count] = uniques
        total_count += count
    all_uniques = total_uniques[:total_count]
    final_unique = np.unique(all_uniques)
    return final_unique

@njit(parallel=True)
def run_simulation(n_events: int, layer_z: np.ndarray, pixel_length_x: float, pixel_length_y: float, layer_half_length_x: np.ndarray, layer_half_length_y: np.ndarray, zenith_boresight_deg: float, azimuth_boresight_deg: float, theta_max_deg: float, simulation_half_length_x: float, simulation_half_length_y: float):
    all_hits = np.empty((n_events, 4), dtype=np.float64)
    valid_hits = np.zeros(n_events, dtype=np.bool_)

    for i in prange(n_events):
        x_pos_earth, y_pos_earth, z_pos_earth, x_dir_earth, y_dir_earth, z_dir_earth = homogenous_generator(theta_max_deg, zenith_boresight_deg, azimuth_boresight_deg, simulation_half_length_x, simulation_half_length_y)
        hits, hit = detection_simulation(layer_z, pixel_length_x, pixel_length_y, layer_half_length_x, layer_half_length_y, zenith_boresight_deg, azimuth_boresight_deg, x_pos_earth, y_pos_earth, z_pos_earth, x_dir_earth, y_dir_earth, z_dir_earth, mode=1)

        if hit:
            c_x, c_y, theta_x, theta_y = track_reconstruction(hits)
            r, theta_x_incident, theta_y_incident = cart2projection(x_dir_earth, y_dir_earth, z_dir_earth)
            all_hits[i, 0] = theta_x_incident
            all_hits[i, 1] = theta_y_incident
            all_hits[i, 2] = theta_x
            all_hits[i, 3] = theta_y
            valid_hits[i] = True

    return all_hits[valid_hits]




@njit(cache=True, parallel=True)
def compute_basis(hits: np.ndarray, basis=None):
    unique_theta_x = chunked_unique_rounded(hits[:, 2], chunk_size=10000, scale=1000, decimals=1)
    unique_theta_y = chunked_unique_rounded(hits[:, 3], chunk_size=10000, scale=1000, decimals=1)


    basis = None
    angle = 25
    mrad = int(np.radians(angle) * 1000)
    theta_x_mrad = np.arange(-mrad, mrad + 1)
    theta_y_mrad = np.arange(-mrad, mrad + 1)
    reference_unique_theta_x = np.arange(-mrad*10, mrad*10 + 1) / 10
    reference_unique_theta_y = np.arange(-mrad*10, mrad*10 + 1) / 10
    reference_unique_theta_x = np.ones_like(reference_unique_theta_x) * len(unique_theta_x)
    reference_unique_theta_y = np.ones_like(reference_unique_theta_y) * len(unique_theta_y)

    for i, val in enumerate(unique_theta_x):
        val *= 10
        reference_unique_theta_x[int(val)] = i

    for i, val in enumerate(unique_theta_y):
        val *= 10
        reference_unique_theta_y[int(val)] = i



    if basis is None:
        basis = np.zeros((len(unique_theta_x), len(unique_theta_y), len(theta_x_mrad), len(theta_y_mrad)), dtype=np.int32)

    theta_x_measured = np.round(hits[:, 2] * 1000, 1)
    theta_y_measured = np.round(hits[:, 3] * 1000, 1)
    theta_x_incident = np.round(hits[:, 0] * 1000, 0)
    theta_y_incident = np.round(hits[:, 1] * 1000, 0)

    cx = np.amin(theta_x_mrad)
    cy = np.amin(theta_y_mrad)

    for i in prange(hits.shape[0]):

        measured_x8 = np.empty(8, dtype=np.float64)
        measured_y8 = np.empty(8, dtype=np.float64)
        incident_x8 = np.empty(8, dtype=np.float64)
        incident_y8 = np.empty(8, dtype=np.float64)

        measured_x = theta_x_measured[i]
        measured_y = theta_y_measured[i]
        incident_x = theta_x_incident[i]
        incident_y = theta_y_incident[i]


        measured_x8[0], measured_y8[0] = measured_x, measured_y
        incident_x8[0], incident_y8[0] = incident_x, incident_y

        measured_x8[1], measured_y8[1] = -measured_x, measured_y
        incident_x8[1], incident_y8[1] = -incident_x, incident_y

        measured_x8[2], measured_y8[2] = measured_x, -measured_y
        incident_x8[2], incident_y8[2] = incident_x, -incident_y

        measured_x8[3], measured_y8[3] = -measured_x, -measured_y
        incident_x8[3], incident_y8[3] = -incident_x, -incident_y

        measured_x8[4], measured_y8[4] = measured_y, measured_x
        incident_x8[4], incident_y8[4] = incident_y, incident_x

        measured_x8[5], measured_y8[5] = -measured_y, measured_x
        incident_x8[5], incident_y8[5] = -incident_y, incident_x

        measured_x8[6], measured_y8[6] = measured_y, -measured_x
        incident_x8[6], incident_y8[6] = incident_y, -incident_x

        measured_x8[7], measured_y8[7] = -measured_y, -measured_x
        incident_x8[7], incident_y8[7] = -incident_y, -incident_x


        incident_x8 -= cx
        incident_y8 -= cy

        for j in range(8):
            basis[int(reference_unique_theta_x[int(measured_x8[j] * 10)]), int(reference_unique_theta_y[int(measured_y8[j] * 10)]), int(incident_x8[j]), int(incident_y8[j])] += 1

    return basis, unique_theta_x, unique_theta_y, theta_x_mrad, theta_y_mrad



if __name__ == "__main__":
    layer_z = np.array([-750, -250, 250, 750], dtype=np.float64)
    layer_half_length_x = np.array([300, 200, 200, 300], dtype=np.float64)
    layer_half_length_y = np.array([300, 200, 200, 300], dtype=np.float64)

    simulation_half_length_x = 200
    simulation_half_length_y = 200

    pixel_length_x = 50
    pixel_length_y = 50

    zenith_boresight_deg = 0
    azimuth_boresight_deg = 0

    theta_max_deg = 30

    solid_angle = 2 * np.pi * (1 - np.cos(np.radians(theta_max_deg)))
    effective_area = 4 * 200 ** 2 / 1000000
    time_elapsed = 36500 * 24 * 3600
    flux = 1

    n_events = int(flux * effective_area * solid_angle * time_elapsed)

    try:
        old_basis = np.load("9449.npz")
        basis = old_basis["basis"]
    except:
        basis = None

    runs = 1
    geometric_factor_array = None
    while True:
        print(f"Run {runs}")
        for i in range(10):
            start = time.time()
            all_hits = run_simulation(n_events, layer_z, pixel_length_x, pixel_length_y, layer_half_length_x, layer_half_length_y, zenith_boresight_deg, azimuth_boresight_deg, theta_max_deg, simulation_half_length_x, simulation_half_length_y)
            basis_, unique_theta_x, unique_theta_y, theta_x_mrad, theta_y_mrad = compute_basis(all_hits)
            end = time.time()
            print(f"{i} Simulated {len(all_hits)} events for {(end - start) / len(all_hits) * 1_000_000_000:.2f} nanoseconds per events, {(end - start):.2f} seconds in total")

            if basis is None:
                basis = basis_
            else:
                basis += basis_

            image = np.sum(basis, axis=(0, 1))

            counts = np.sum(image)

            if geometric_factor_array is None:
                unique_angles_x, unique_angles_y = np.meshgrid(unique_theta_x, unique_theta_y)
                simulated_angles_x, simulated_angles_y = np.meshgrid(theta_x_mrad, theta_y_mrad)
                geometric_factor_array = geometric_factor(simulated_angles_x / 1000, simulated_angles_y / 1000, layer_z, layer_half_length_x, layer_half_length_y, 1 / 1000, 1 / 1000)

            image[geometric_factor_array > 0] = image[geometric_factor_array > 0] / geometric_factor_array[geometric_factor_array > 0]
            image[geometric_factor_array <= 0] = 0

            mask = (np.abs(simulated_angles_x) <= np.radians(21) * 1000) & (np.abs(simulated_angles_y) <= np.radians(21) * 1000) & (geometric_factor_array > 0)
            mean = np.mean(image[mask])
            std = np.std(image[mask])

            std_over_mean = std / mean

            with open("9449.txt", "a") as f:
                f.write(f"{counts}, {std_over_mean}\n")

            print(f"Total counts: {counts}, std/mean: {std_over_mean}")
        unique_angles_x, unique_angles_y = np.meshgrid(unique_theta_x, unique_theta_y)
        simulated_angles_x, simulated_angles_y = np.meshgrid(theta_x_mrad, theta_y_mrad)
        geometric_factor_array = geometric_factor(simulated_angles_x / 1000, simulated_angles_y / 1000, layer_z, layer_half_length_x, layer_half_length_y, 1 / 1000, 1 / 1000)

        measured_angles = np.array([unique_angles_x, unique_angles_y])
        incident_angles = np.array([simulated_angles_x, simulated_angles_y])



        dictionary = {
            "basis": basis,
            "measured_angles": measured_angles,
            "incident_angles": incident_angles,
            "geometric_factor": geometric_factor_array
        }

        np.savez_compressed("9449.npz", **dictionary)

        runs += 1