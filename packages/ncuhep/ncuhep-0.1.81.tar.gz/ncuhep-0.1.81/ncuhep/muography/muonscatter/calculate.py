import numpy as np
import matplotlib.pyplot as plt
from .constructor import params_array
from numba import cuda
from ..utils.coordinates import det2zenith
from .flux_model import differential_flux
from .gpu import splat_kernels
from .constants import sigma_window_ratio_lower, sigma_window_ratio_upper
import cv2
from ..profiler import Profiler, print_profile
from typing import Optional


def params_array_wrapper(energy, L, THX, THY, PhiE, window_size, flatten=True):
    idx = np.arange(THX.shape[0])
    idy = np.arange(THY.shape[1])
    IDX, IDY = np.meshgrid(idx, idy, indexing='ij')
    params = params_array(energy, L, THX, THY, IDX, IDY, PhiE, window_size)
    if flatten:
        params = params.reshape(-1, params.shape[-1])
    return params


def crop(THX, THY, OUTPUT, angle):
    mrad = int(np.round(np.radians(angle) * 1000))

    thx = THX[:, 0]
    thy = THY[0, :]

    idx_min = np.argmin(np.abs(thx + mrad * 0.001))
    idx_max = np.argmin(np.abs(thx - mrad * 0.001))
    idy_min = np.argmin(np.abs(thy + mrad * 0.001))
    idy_max = np.argmin(np.abs(thy - mrad * 0.001))

    if idx_min > idx_max:
        idx_min, idx_max = idx_max, idx_min
    if idy_min > idy_max:
        idy_min, idy_max = idy_max, idy_min

    THX_ = THX[idx_min:idx_max + 1, idy_min:idy_max + 1]
    THY_ = THY[idx_min:idx_max + 1, idy_min:idy_max + 1]
    OUTPUT_ = OUTPUT[idx_min:idx_max + 1, idy_min:idy_max + 1]
    return THX_, THY_, OUTPUT_




def calculate(
    path,
    density_map,
    crop_angle,
    window_size=20.0,
    bins=128,
    *,
    profiler: Optional[Profiler] = None,
    profile: bool = False,
):
    """
    Run the full simulation (thickness NPZ → flux map), with optional profiling.

    Parameters
    ----------
    path : str
        Path to thickness NPZ (must contain L, THX_rad, THY_rad, THX_mrad, THY_mrad, meta).
    density_map : ndarray or None
        Optional density field to scale thickness (same shape as cropped THX/THY).
        If None, a uniform map (2.3 g/cc) is assumed.
    crop_angle : float
        Half-angle (deg) for cropping FOV around 0,0.
    window_size : float
        Splat window size (same units as pixel_size; passed to splat_kernels).
    bins : int
        Number of bins used in GPU splat kernels.
    profiler : Profiler or None
        Optional existing Profiler; if None, a new one is created.
    profile : bool
        If True, print a timing summary at the end.

    Returns
    -------
    THX, THY, RESULT, density_map
    """
    prof = profiler if profiler is not None else Profiler()

    # ---------------- I/O: load NPZ & metadata ----------------
    with prof.section("io:load_npz"):
        data = np.load(path, allow_pickle=True)
        meta = data["meta"].item()
        THX = data['THX_rad']
        THY = data['THY_rad']
        THX_mrad = data['THX_mrad']
        THY_mrad = data['THY_mrad']

    # ---------------- Setup: pixel size & kernels ----------------
    with prof.section("setup:kernels"):
        x_ = THX[:, 0]
        y_ = THX[0, :]

        dx_ = np.abs(x_[1] - x_[0])
        dy_ = np.abs(y_[1] - y_[0])

        pixel_size = np.max([dx_, dy_])  # in rad

        splat1_kernel, splat2_kernel, splat3_kernel = splat_kernels(
            pixel_size, window_size, bins
        )

    # ---------------- Density map prepare / pad ----------------
    with prof.section("density:prepare"):
        if density_map is None:
            density_map = np.ones_like(THX, dtype=np.float32) * 2.65
        else:
            THX_cropped, THY_cropped, _ = crop(THX, THY, np.zeros_like(THX), crop_angle)

            density_map = cv2.resize(
                density_map,
                (THX_cropped.shape[1], THX_cropped.shape[0]),
                interpolation=cv2.INTER_AREA,
            )

            pad_y = THX.shape[0] - density_map.shape[0]
            pad_x = THX.shape[1] - density_map.shape[1]

            pad_width = (
                (pad_y // 2, pad_y - pad_y // 2),
                (pad_x // 2, pad_x - pad_x // 2),
            )

            density_map = np.pad(density_map, pad_width, mode='edge')

    # ---------------- Thickness scaling & zenith angles ----------------
    with prof.section("thickness:scale_and_zenith"):
        L = data['L'] / 2.65 * density_map
        L = np.clip(L, 20, 1000)  # limit max thickness to 1000 m
        zenith = det2zenith(
            THX_mrad,
            -THY_mrad,
            np.radians(meta["angle_deg"]),
            0,
        )

    # ---------------- Allocate result buffers ----------------
    with prof.section("setup:result_buffers"):
        RESULT0 = np.zeros(THX.shape, dtype=np.float32)
        RESULT1 = np.zeros(THX.shape, dtype=np.float32)
        RESULT2 = np.zeros(THX.shape, dtype=np.float32)
        RESULT3 = np.zeros(THX.shape, dtype=np.float32)

    # ---------------- Energy grid & parameter building ----------------
    with prof.section("loop:build_all_params"):
        energies = np.logspace(np.log10(10), np.log10(4000), 101)  # GeV
        dE = energies[1:] - energies[:-1]
        energies_mid = 0.5 * (energies[1:] + energies[:-1])

        params = None
        for i, energy in enumerate(energies_mid):
            PhiE = differential_flux(zenith, energy) * dE[i]
            params_ = params_array_wrapper(
                energy, L, THX, THY, PhiE, pixel_size, flatten=True
            )
            # filter out samples with non-positive sr
            params_ = params_[params_[:, 7] > 0]

            if params_ is None or params_.size == 0:
                continue

            if params is None:
                params = params_
            else:
                params = np.concatenate((params, params_), axis=0)

    if params is None or params.shape[0] == 0:
        # No contributions at all
        if profile:
            print_profile("simulate()", prof)
        return THX, THY, np.zeros_like(THX, dtype=np.float32), density_map

    # ---------------- Sort & split params by sigma-scale ----------------
    with prof.section("params:sort_and_split"):
        argsort = np.argsort(params[:, 1])
        params = params[argsort]
        sigma_ps = params[:, 1] / pixel_size

        mask0 = sigma_ps < sigma_window_ratio_lower
        mask1 = (sigma_ps > sigma_window_ratio_lower) & (sigma_ps < 1)
        mask2 = (sigma_ps >= 1) & (sigma_ps < sigma_window_ratio_upper)
        mask3 = sigma_ps >= sigma_window_ratio_upper

        params0 = params[mask0]
        params1 = params[mask1]
        params2 = params[mask2]
        params3 = params[mask3]

    # ---------------- Branch 0: direct accumulate (tiny sigma) ----------------
    with prof.section("splat:direct_accumulate"):
        if params0.shape[0] > 0:
            for p in params0:
                (
                    _A, _sigma, _s2, _s3, _n, _f1, _f2, sr,
                    thx, thy, idx, idy, _window, PhiE, _dummy1, _dummy2
                ) = p
                RESULT0[int(idx), int(idy)] += PhiE * sr

    # ---------------- Branch 1: GPU splat1_kernel ----------------
    with prof.section("splat:kernel1"):
        if params1.shape[0] > 0:
            params_device = cuda.to_device(params1)
            OUTPUT_device = cuda.to_device(RESULT1)
            threads_per_block = 32
            blocks_per_grid = params1.shape[0]
            splat1_kernel[blocks_per_grid, threads_per_block](params_device, OUTPUT_device)
            cuda.synchronize()
            params_device.copy_to_host(params1)
            OUTPUT_device.copy_to_host(RESULT1)

    # ---------------- Branch 2: GPU splat2_kernel ----------------
    with prof.section("splat:kernel2"):
        if params2.shape[0] > 0:
            params_device = cuda.to_device(params2)
            OUTPUT_device = cuda.to_device(RESULT2)
            threads_per_block = 32
            blocks_per_grid = params2.shape[0]  # one block per sample
            splat2_kernel[blocks_per_grid, threads_per_block](params_device, OUTPUT_device)
            cuda.synchronize()
            params_device.copy_to_host(params2)
            OUTPUT_device.copy_to_host(RESULT2)

    # ---------------- Branch 3: GPU splat3_kernel ----------------
    with prof.section("splat:kernel3"):
        if params3.shape[0] > 0:
            params_device = cuda.to_device(params3)
            OUTPUT_device = cuda.to_device(RESULT3)

            threads_per_block = 256
            blocks_per_grid = params3.shape[0]  # one block per sample
            splat3_kernel[blocks_per_grid, threads_per_block](params_device, OUTPUT_device)
            cuda.synchronize()
            OUTPUT_device.copy_to_host(RESULT3)
            params_device.copy_to_host(params3)

    # ---------------- Crop & combine ----------------
    with prof.section("post:crop_and_combine"):
        _, _, RESULT0_c = crop(THX, THY, RESULT0, crop_angle)
        _, _, RESULT1_c = crop(THX, THY, RESULT1, crop_angle)
        _, _, RESULT2_c = crop(THX, THY, RESULT2, crop_angle)
        THX_c, THY_c, RESULT3_c = crop(THX, THY, RESULT3, crop_angle)

        RESULT = RESULT0_c + RESULT1_c + RESULT2_c + RESULT3_c

    if profile:
        print_profile("simulate()", prof)

    return THX_c, THY_c, RESULT, density_map
