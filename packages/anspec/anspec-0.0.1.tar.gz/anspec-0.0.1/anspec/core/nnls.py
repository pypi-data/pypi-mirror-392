from typing import Literal, overload

import numpy as np

from anspec.types import (
    Array2D,
    CPUArray2D,
    CUDAArray2D,
    Device,
    DTypeLike,
    NumPyOrCuPy,
)


def projected_lstsq_warmstart(
    A: Array2D, B: Array2D, dtype: DTypeLike | None = None, xp: NumPyOrCuPy = np
) -> Array2D:
    """
    Compute X0 = clip(argmin_X ||A X - B||_F^2, 0, ∞) using a single least-squares solve.
    Uses one factorization of A for all columns of B.
    """
    if dtype is None:
        dtype = xp.result_type(A.dtype, B.dtype)
    A = xp.asarray(A, dtype=dtype)
    B = xp.asarray(B, dtype=dtype)
    # lstsq factors A once for multiple RHS
    X0, *_ = xp.linalg.lstsq(A, B, rcond=None)
    X0 = xp.maximum(X0, 0)
    return X0


def nnls_fista(
    A: Array2D,
    B: Array2D,
    X0: Array2D | None = None,
    L: float | None = None,
    dtype: DTypeLike | None = None,
    max_iters: int = 1000,
    max_tol: float | None = None,
    min_obj: float | None = None,
    verbose: bool = False,
    xp: NumPyOrCuPy = np,
) -> Array2D:
    """
    Plain FISTA for NNLS, allocation-free inner loop.
    """
    m, f = A.shape
    _, n = B.shape

    if dtype is None:
        dtype = xp.result_type(A.dtype, B.dtype)

    A = xp.asarray(A, dtype=dtype)
    B = xp.asarray(B, dtype=dtype)

    if L is None:
        AAT = A @ A.T
        L = float(xp.linalg.eigvalsh(AAT).max())
        if not xp.isfinite(L) or L <= 0:
            L = 1.0
    invL = 1.0 / L

    if X0 is None:
        X = projected_lstsq_warmstart(A, B, dtype=dtype, xp=xp)
    else:
        X = xp.maximum(0, xp.asarray(X0, dtype=dtype).copy())

    Y = X.copy()
    Z = xp.empty_like(X)
    D = xp.empty_like(X)
    R = xp.empty((m, n), dtype=dtype)
    G = xp.empty((f, n), dtype=dtype)

    t = 1.0

    for k in range(max_iters):
        R[:] = A @ Y
        R -= B
        G[:] = A.T @ R

        Z[:] = Y
        Z -= invL * G
        xp.maximum(Z, 0, out=Z)

        t_new = 0.5 * (1.0 + xp.sqrt(1.0 + 4.0 * t * t))
        alpha = (t - 1.0) / t_new

        D[:] = Z
        D -= X
        Y[:] = Z
        Y += alpha * D
        t = t_new

        if max_tol is not None:
            diff_norm = float(xp.linalg.norm(D))
            base_norm = max(1.0, float(xp.linalg.norm(X)))
            if diff_norm <= max_tol * base_norm:
                X, Z = Z, X
                if verbose:
                    print(f"iter {k} | rel_change {diff_norm / base_norm:.3e} | stop")
                break

        if min_obj is not None:
            # Uses R = A @ Y - B already computed; not exactly f(X), but cheap progress metric
            obj_y = float(xp.mean(R * R))
            if obj_y <= min_obj:
                X, Z = Z, X
                if verbose:
                    print(f"iter {k} | f(Y) {obj_y:.6e} | stop")
                break

        if verbose and k == max_iters - 1:
            obj_y = float(xp.mean(R * R))
            print(f"iter {k} | f(Y) {obj_y:.6e} | max_iters reached")

        X, Z = Z, X

    return X


@overload
def nnls(
    A: Array2D,
    B: Array2D,
    *,
    max_iters: int = 1000,
    min_obj: float = 1e-3,
    device: Literal["cpu"] = "cpu",
    dtype: DTypeLike = np.float32,
) -> CPUArray2D: ...
@overload
def nnls(
    A: Array2D,
    B: Array2D,
    *,
    max_iters: int = 1000,
    min_obj: float = 1e-3,
    device: Literal["cuda"] = "cuda",
    dtype: DTypeLike = np.float32,
) -> CUDAArray2D: ...
def nnls(
    A: Array2D,
    B: Array2D,
    *,
    max_iters: int = 1000,
    min_obj: float = 1e-3,
    device: Device = "cpu",
    dtype: DTypeLike = np.float32,
) -> Array2D:
    if device == "cpu":
        return nnls_fista(
            A,
            B,
            max_iters=max_iters,
            min_obj=min_obj,
            xp=np,
            dtype=dtype,
            verbose=False,
        )
    elif device == "cuda":
        try:
            import cupy as cp  # type: ignore
        except ImportError:
            raise ImportError("cupy is required for cuda device")
        return nnls_fista(
            A,
            B,
            max_iters=max_iters,
            min_obj=min_obj,
            xp=cp,
            dtype=dtype,
            verbose=False,
        )
    else:
        raise ValueError(f"Unsupported device: {device}")
