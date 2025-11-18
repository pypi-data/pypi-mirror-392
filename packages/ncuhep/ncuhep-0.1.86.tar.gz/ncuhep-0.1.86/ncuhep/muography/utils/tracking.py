import numpy as np
from numba import njit

@njit
def track_reconstruction(hits: np.ndarray):
    x = hits[:, 0]
    y = hits[:, 1]
    z = hits[:, 2]

    mean_x = np.mean(x)
    mean_y = np.mean(y)
    mean_z = np.mean(z)

    sum_zz = np.sum((z - mean_z) ** 2)
    sum_zx = np.sum((z - mean_z) * (x - mean_x))
    sum_zy = np.sum((z - mean_z) * (y - mean_y))

    m_x = sum_zx / sum_zz if sum_zz != 0 else 0.0
    m_y = sum_zy / sum_zz if sum_zz != 0 else 0.0

    c_x = mean_x - m_x * mean_z
    c_y = mean_y - m_y * mean_z

    return c_x, c_y, np.arctan(m_x), np.arctan(m_y)