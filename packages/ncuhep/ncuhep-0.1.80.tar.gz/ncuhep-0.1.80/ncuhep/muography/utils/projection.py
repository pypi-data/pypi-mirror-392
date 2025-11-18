import numpy as np
import scipy.sparse as sp
import jax.numpy as jnp
from jax.experimental import sparse as jsparse
from jax.scipy.sparse.linalg import cg as jax_cg


def projection(flux, basis, angle_deg=13.0):

    def crop(array, half_angle_deg):
        mrad = int(np.radians(half_angle_deg) * 1000)
        center = array.shape[0] // 2
        return array[center - mrad:center + mrad + 1, center - mrad:center + mrad + 1]

    flux_pred_cropped = crop(flux, angle_deg)

    basis_cropped = np.zeros((basis.shape[0], basis.shape[1], flux_pred_cropped.shape[0], flux_pred_cropped.shape[1]))
    for i in range(basis.shape[0]):
        for j in range(basis.shape[1]):
            basis_cropped[i, j] = crop(basis[i, j], angle_deg) / np.sum(basis[i, j])

    y_pred = flux_pred_cropped.ravel(order="C")

    I, J, h, w = basis_cropped.shape
    m, n = h * w, I * J

    nz = np.nonzero(basis_cropped)
    ii, jj, rr, cc = nz
    data_B = basis_cropped[nz]

    rows = rr.astype(np.int64) * w + cc.astype(np.int64)
    cols = ii.astype(np.int64) * J + jj.astype(np.int64)

    B_coo = sp.coo_matrix((data_B, (rows, cols)), shape=(m, n))
    B_bcoo = jsparse.BCOO.from_scipy_sparse(B_coo.tocsr())

    def B_mv_j(a):
        return B_bcoo @ a

    def BT_mv_j(r):
        return B_bcoo.T @ r

    def ATA_mv_j(v):
        return BT_mv_j(B_mv_j(v))

    y_jax = jnp.asarray(y_pred)

    b_j = BT_mv_j(y_jax)

    cols_j = jnp.asarray(cols)
    diag_j = jnp.zeros(n, dtype=B_bcoo.dtype).at[cols_j].add(jnp.asarray(data_B) ** 2)
    Minv_j = jnp.where(diag_j > 0, 1.0 / diag_j, 1.0)
    M_j = lambda v: Minv_j * v

    a0 = jnp.zeros(n, dtype=y_jax.dtype)
    a_hat_j, info_j = jax_cg(ATA_mv_j, b_j, x0=a0, tol=1e-12, maxiter=1000, M=M_j)

    a_hat = np.array(a_hat_j)
    flux_recon = B_mv_j(a_hat)
    flux_recon = np.array(flux_recon).reshape(flux_pred_cropped.shape, order="C")
    a_recon = a_hat.reshape((basis_cropped.shape[0], basis_cropped.shape[1]), order="C")

    return flux_recon, a_recon
