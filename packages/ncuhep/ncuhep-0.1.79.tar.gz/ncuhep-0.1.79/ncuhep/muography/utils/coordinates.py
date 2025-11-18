import numpy as np
from numba import njit


@njit(cache=True)
def cart2projection(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    theta_x_rad = np.arctan2(x, z)
    theta_y_rad = np.arctan2(y, z)
    return r, theta_x_rad, theta_y_rad


@njit(cache=True)
def projection2cart(r, theta_x_rad, theta_y_rad):
    x_ = np.tan(theta_x_rad)
    y_ = np.tan(theta_y_rad)
    c = r / np.sqrt(1 + x_**2 + y_**2)

    x = x_ * c
    y = y_ * c
    z = c

    return x, y, z


@njit(cache=True)
def cart2spherical(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(z / r)
    phi = np.arctan2(-x, y)

    return r, theta, phi


@njit(cache=True)
def spherical2cart(r, theta_rad, phi_rad):
    x = -r * np.sin(theta_rad) * np.sin(phi_rad)
    y = r * np.sin(theta_rad) * np.cos(phi_rad)
    z = r * np.cos(theta_rad)

    return x, y, z

@njit(cache=True)
def projection2spherical(r, theta_x_rad, theta_y_rad):
    x, y, z = projection2cart(r, theta_x_rad, theta_y_rad)
    return cart2spherical(x, y, z)

@njit(cache=True)
def spherical2projection(r, theta_rad, phi_rad):
    x, y, z = spherical2cart(r, theta_rad, phi_rad)
    return cart2projection(x, y, z)


@njit(cache=True)
def det2earth(x, y, z, zenith_rad, azimuth_rad):
    ca = np.cos(azimuth_rad)
    sa = np.sin(azimuth_rad)
    cz = np.cos(zenith_rad)
    sz = np.sin(zenith_rad)

    x_ = ca * x - sa * cz * y + sa * sz * z
    y_ = sa * x + ca * cz * y - ca * sz * z
    z_ = sz * y + cz * z

    return x_, y_, z_


@njit(cache=True)
def earth2det(x, y, z, zenith_rad, azimuth_rad):

    ca = np.cos(azimuth_rad)
    sa = np.sin(azimuth_rad)
    cz = np.cos(zenith_rad)
    sz = np.sin(zenith_rad)

    x_ = ca * x + sa * y
    y_ = -sa * cz * x + ca * cz * y + sz * z
    z_ = sa * sz * x - ca * sz * y + cz * z

    return x_, y_, z_
@njit(cache=True)
def det2zenith(theta_x_mrad, theta_y_mrad, zenith_rad, azimuth_rad):
    x, y, z = projection2cart(1, theta_x_mrad / 1000, theta_y_mrad / 1000)
    xe, ye, ze = det2earth(x, y, z, zenith_rad, azimuth_rad)
    _, theta_rad, _ = cart2spherical(xe, ye, ze)
    return theta_rad

def mrad2zenith(angle_deg, theta_rad, phi_rad):
    mrad = int(np.radians(angle_deg) * 1000)
    nx = np.arange(-mrad, mrad + 1)
    ny = np.arange(-mrad, mrad + 1)

    X, Y = np.meshgrid(nx, ny)

    zenith_angle_ = np.zeros(X.shape, dtype=np.float64)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            zenith_angle_[i, j] = det2zenith(X[i, j], Y[i, j], theta_rad, phi_rad)

    return zenith_angle_
