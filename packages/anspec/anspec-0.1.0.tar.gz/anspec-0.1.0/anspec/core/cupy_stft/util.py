from typing import Optional, Union, Literal, Sequence, List, Any, Dict, cast
from types import ModuleType
from functools import lru_cache

import numpy as np  # For dtype, RNG compatibility with existing API
import cupy as cp
from cupy.lib.stride_tricks import as_strided
from numpy.typing import DTypeLike, ArrayLike

from anspec.core.cupy_stft.kernel import (
    _overlap_add_f32,
    _overlap_add_f64,
    _wss_f32,
    _wss_f64,
)


def max_fft_columns_(y_frames: cp.ndarray, safety_mb: int = 64) -> int:
    # Approximate memory budget for input+windowed+output batches.
    free_mem, _ = cp.cuda.runtime.memGetInfo()
    budget = max(16 * (1 << 20), free_mem - safety_mb * (1 << 20))  # leave safety_mb MB
    elems_per_col = int(cp.prod(cp.asarray(y_frames.shape[:-1])))
    bytes_per_col = (
        elems_per_col * y_frames.dtype.itemsize * 3
    )  # input, windowed, output
    if bytes_per_col <= 0:
        return y_frames.shape[-1]
    return max(1, min(y_frames.shape[-1], int(budget // bytes_per_col)))


def max_fft_columns(y_frames: cp.ndarray, safety_mb: int = 64) -> int:
    """
    Estimate max number of columns (last axis) to process in one FFT batch,
    budgeting for input + windowed + output (3x).
    """
    # Query memory on the array's device (does not synchronize kernels)
    with cp.cuda.Device(y_frames.device):
        free_mem, _ = cp.cuda.runtime.memGetInfo()

    # Leave safety headroom
    budget = max(16 * (1 << 20), free_mem - safety_mb * (1 << 20))

    T = y_frames.shape[-1]
    if T == 0:
        return 0

    # Elements per column = product of leading dims; use host metadata only
    elems_per_col = y_frames.size // T
    bytes_per_col = (
        elems_per_col * y_frames.dtype.itemsize * 3
    )  # input, windowed, output

    if bytes_per_col <= 0:
        return T

    max_cols = budget // bytes_per_col
    return max(1, min(T, int(max_cols)))


def max_irfft_columns(
    stft_matrix: cp.ndarray, n_fft: int, dtype_out: np.dtype, safety_mb: int = 64
) -> int:
    """
    Compute the max number of time frames (columns) to process in one irfft batch.

    stft_matrix shape: (..., F, T) where F = n_fft//2 + 1
    irfft output per frame: (..., n_fft)
    We budget for:
      - input complex slice (..., F, block_T)
      - irfft output (..., n_fft, block_T)
      - windowed buffer of same size as output
    """
    # Query the correct device's memory (cheap, does not synchronize kernels)
    with cp.cuda.Device(stft_matrix.device):  # or stft_matrix.device.id in older CuPy
        free_mem, _ = cp.cuda.runtime.memGetInfo()

    # Leave safety headroom
    budget = max(16 * (1 << 20), free_mem - safety_mb * (1 << 20))

    shape = stft_matrix.shape
    F = shape[-2]
    T = shape[-1]

    # Host-side product of leading dims (no GPU kernel, no sync)
    leading = shape[:-2]
    batch = (
        np.prod(leading) if leading else 1
    )  # same as np.prod on CPU, but faster to import

    in_bytes_per_frame = batch * F * stft_matrix.dtype.itemsize
    out_bytes_per_frame = batch * n_fft * np.dtype(dtype_out).itemsize

    # Input + output + windowed (same size as output)
    bytes_per_frame = in_bytes_per_frame + 2 * out_bytes_per_frame
    if bytes_per_frame <= 0:
        return T

    max_frames = budget // bytes_per_frame
    return max(1, min(T, int(max_frames)))


def _launch_config(total_elems: int, threads=256):
    blocks = (total_elems + threads - 1) // threads
    return (blocks, 1, 1), (threads, 1, 1)


def get_fftlib() -> ModuleType:
    # Use CuPy FFT (cuFFT backend)
    return cp.fft


@lru_cache
def get_window(
    window: Literal["hann"],
    Nx: int,
    *,
    fftbins: Optional[bool] = True,
) -> cp.ndarray:
    """
    CuPy version: Only supports Hann as per the Literal["hann"] typing.
    Replicates scipy.signal.get_window('hann', Nx, fftbins=fftbins) with float64.
    """
    if window != "hann":
        raise ValueError(
            f"Invalid window specification: {window!r} (only 'hann' supported)"
        )

    if Nx < 0:
        raise ValueError(f"Window length must be non-negative, got {Nx}")

    # SciPy default returns float64 windows
    dtype = cp.float64

    if Nx == 0:
        return cp.asarray([], dtype=dtype)

    n = cp.arange(Nx, dtype=dtype)
    if fftbins:
        # Periodic (sym=False) definition
        # w[n] = 0.5 - 0.5*cos(2*pi*n/Nx), n=0..Nx-1
        # Matches scipy.signal.get_window('hann', Nx, fftbins=True)
        return 0.5 - 0.5 * cp.cos(2.0 * cp.pi * n / Nx)
    else:
        # Symmetric (sym=True) definition
        # w[n] = 0.5 - 0.5*cos(2*pi*n/(Nx-1)), n=0..Nx-1
        if Nx == 1:
            return cp.ones(1, dtype=dtype)
        return 0.5 - 0.5 * cp.cos(2.0 * cp.pi * n / (Nx - 1))


def normalize(
    S: cp.ndarray,
    *,
    norm: Optional[float] = np.inf,
    axis: Optional[int] = 0,
    threshold: Optional[float] = None,
    fill: Optional[bool] = None,
) -> cp.ndarray:
    if threshold is None:
        threshold = tiny(S)  # type: ignore
    elif threshold <= 0:
        raise ValueError(f"threshold={threshold} must be strictly positive")

    if fill not in [None, False, True]:
        raise ValueError(f"fill={fill} must be None or boolean")

    if not cp.all(cp.isfinite(S)):
        raise ValueError("Input must be finite")

    mag = cp.abs(S).astype(
        cp.float64
    )  # operate in float64 to match NumPy/SciPy behavior

    fill_norm = 1

    if norm is None:
        return S

    elif norm == np.inf:
        length = cp.max(mag, axis=axis, keepdims=True)

    elif norm == -np.inf:
        length = cp.min(mag, axis=axis, keepdims=True)

    elif norm == 0:
        if fill is True:
            raise ValueError("Cannot normalize with norm=0 and fill=True")
        length = cp.sum(mag > 0, axis=axis, keepdims=True, dtype=mag.dtype)

    elif np.issubdtype(type(norm), np.number) and norm > 0:
        length = cp.sum(mag**norm, axis=axis, keepdims=True) ** (1.0 / norm)
        if axis is None:
            fill_norm = mag.size ** (-1.0 / norm)
        else:
            fill_norm = mag.shape[axis] ** (-1.0 / norm)
    else:
        raise ValueError(f"Unsupported norm: {repr(norm)}")

    small_idx = length < threshold

    Snorm = cp.empty_like(S)
    if fill is None:
        length = length.copy()
        length[small_idx] = 1.0
        Snorm[:] = S / length

    elif fill:
        length = length.copy()
        length[small_idx] = cp.nan
        Snorm[:] = S / length
        Snorm[cp.isnan(Snorm)] = fill_norm
    else:
        length = length.copy()
        length[small_idx] = cp.inf
        Snorm[:] = S / length

    return Snorm


@lru_cache(maxsize=128)
def _cached_win_sq(
    window: Literal["hann"],
    win_length: int,
    n_fft: int,
    norm: Optional[float],
    dtype: np.dtype,
):
    # Build squared window, padded, in target dtype
    win = get_window(window, win_length, fftbins=True).astype(dtype)
    win = normalize(win, norm=norm)
    win_sq = pad_center(win**2, size=n_fft)
    return win_sq  # cp.ndarray, dtype per caller


def _window_sumsquare(
    *,
    window: Literal["hann"],
    n_frames: int,
    hop_length: int = 512,
    win_length: Optional[int] = None,
    n_fft: int = 2048,
    dtype: Union[np.dtype, type] = np.float32,
    norm: Optional[float] = None,
) -> cp.ndarray:
    if win_length is None:
        win_length = n_fft

    dtype = np.dtype(dtype)
    out_len = n_fft + hop_length * (n_frames - 1)
    x = cp.zeros(out_len, dtype=dtype)

    win_sq = _cached_win_sq(window, win_length, n_fft, norm, dtype)

    total = n_fft * n_frames
    grid, block = _launch_config(total)

    if x.dtype == cp.float32:
        _wss_f32(
            grid,
            block,
            (
                win_sq,
                np.int32(n_fft),
                np.int32(n_frames),
                np.int32(hop_length),
                x,
                np.int32(out_len),
            ),
        )
    else:
        _wss_f64(
            grid,
            block,
            (
                win_sq,
                np.int32(n_fft),
                np.int32(n_frames),
                np.int32(hop_length),
                x,
                np.int32(out_len),
            ),
        )
    return x


@lru_cache
def _wss_cached_impl(
    window: Literal["hann"],
    n_frames: int,
    hop_length: int,
    win_length: int,
    n_fft: int,
    dtype_key: str,
    norm_key: Optional[float],
    device_id: int,
):
    # Recreate dtype and bind to device that matches the key
    dtype = np.dtype(dtype_key)
    with cp.cuda.Device(device_id):
        # Call your fast implementation (atomic kernel or loop-based)
        return _window_sumsquare(
            window=window,
            n_frames=n_frames,
            hop_length=hop_length,
            win_length=win_length,
            n_fft=n_fft,
            dtype=dtype,
            norm=norm_key,
        )


def window_sumsquare(
    *,
    window: str,
    n_frames: int,
    hop_length: int = 512,
    win_length: Optional[int] = None,
    n_fft: int = 2048,
    dtype: DTypeLike = np.float32,
    norm: Optional[float] = None,
) -> cp.ndarray:
    if win_length is None:
        win_length = n_fft
    dev_id = cp.cuda.Device().id

    def _dtype_key(dtype) -> str:
        return np.dtype(dtype).str  # e.g. '<f4' or '<f8'

    def _norm_key(norm):
        if norm is None:
            return None
        return float(norm)

    arr = _wss_cached_impl(
        window,
        int(n_frames),
        int(hop_length),
        int(win_length),
        int(n_fft),
        _dtype_key(dtype),
        _norm_key(norm),
        dev_id,
    )
    # Important: return as-is (read-only convention). Do not modify it downstream.
    return arr


def is_positive_int(x: float) -> bool:
    return isinstance(x, (int, np.integer)) and (x > 0)


def _is_array_floating(arr: Union[np.ndarray, cp.ndarray]) -> bool:
    dt = arr.dtype
    # Both NumPy and CuPy dtypes are compatible with np.issubdtype
    return np.issubdtype(dt, np.floating)


# Define once so it doesn't recompile each call
_CUPY_ISFINITE_ALL = cp.ReductionKernel(
    in_params="T x",
    out_params="bool y",
    map_expr="isfinite(x)",  # true if element is finite
    reduce_expr="a && b",  # logical AND across elements
    post_map_expr="y = a",
    identity="true",
    name="cupy_isfinite_all",
)


def valid_audio(y: Union[np.ndarray, cp.ndarray]) -> bool:
    if not isinstance(y, (np.ndarray, cp.ndarray)):
        raise ValueError("Audio data must be of type numpy.ndarray or cupy.ndarray")

    if not _is_array_floating(y):
        raise ValueError("Audio data must be floating-point")

    if y.ndim == 0:
        raise ValueError(
            f"Audio data must be at least one-dimensional, given y.shape={y.shape}"
        )

    # For CuPy arrays, cp.isfinite; for NumPy, np.isfinite
    if isinstance(y, cp.ndarray):
        if not bool(_CUPY_ISFINITE_ALL(y).item()):
            raise ValueError("Audio buffer is not finite everywhere")
    else:
        if not np.isfinite(y).all():
            raise ValueError("Audio buffer is not finite everywhere")

    return True


def pad_center(
    data: cp.ndarray, *, size: int, axis: int = -1, **kwargs: Any
) -> cp.ndarray:
    kwargs.setdefault("mode", "constant")

    n = data.shape[axis]
    lpad = int((size - n) // 2)

    lengths = [(0, 0)] * data.ndim
    lengths[axis] = (lpad, int(size - n - lpad))

    if lpad < 0:
        raise ValueError(f"Target size ({size:d}) must be at least input size ({n:d})")

    return cp.pad(data, lengths, **kwargs)


def expand_to(
    x: cp.ndarray, *, ndim: int, axes: Union[int, slice, Sequence[int], Sequence[slice]]
) -> cp.ndarray:
    try:
        axes_tup = tuple(axes)  # type: ignore
    except TypeError:
        axes_tup = tuple([axes])  # type: ignore

    if len(axes_tup) != x.ndim:
        raise ValueError(
            f"Shape mismatch between axes={axes_tup} and input x.shape={x.shape}"
        )

    if ndim < x.ndim:
        raise ValueError(
            f"Cannot expand x.shape={x.shape} to fewer dimensions ndim={ndim}"
        )

    shape: List[int] = [1] * ndim
    for i, axi in enumerate(axes_tup):
        shape[int(axi)] = x.shape[i]  # type: ignore

    return x.reshape(shape)


def frame(
    x: cp.ndarray,
    *,
    frame_length: int,
    hop_length: int,
    axis: int = -1,
    writeable: bool = False,
    subok: bool = False,
) -> cp.ndarray:
    x = cp.array(x, copy=False)  # subok ignored in CuPy

    if x.shape[axis] < frame_length:
        raise ValueError(
            f"Input is too short (n={x.shape[axis]:d}) for frame_length={frame_length:d}"
        )

    if hop_length < 1:
        raise ValueError(f"Invalid hop_length: {hop_length:d}")

    out_strides = x.strides + tuple([x.strides[axis]])

    x_shape_trimmed = list(x.shape)
    x_shape_trimmed[axis] -= frame_length - 1

    out_shape = tuple(x_shape_trimmed) + tuple([frame_length])

    xw = as_strided(x, strides=out_strides, shape=out_shape)

    target_axis = axis - 1 if axis < 0 else axis + 1
    xw = cp.moveaxis(xw, -1, target_axis)

    slices = [slice(None)] * xw.ndim
    slices[axis] = slice(0, None, hop_length)
    return xw[tuple(slices)]


def dtype_r2c(
    d: Union[np.dtype, type], *, default: Optional[type] = np.complex64
) -> np.dtype:
    mapping: Dict[np.dtype, type] = {
        np.dtype(np.float32): np.complex64,
        np.dtype(np.float64): np.complex128,
        np.dtype(float): np.dtype(complex).type,
    }
    dt = np.dtype(d)
    if dt.kind == "c":
        return dt
    return np.dtype(mapping.get(dt, default))


def dtype_c2r(
    d: Union[np.dtype, type], *, default: Optional[type] = np.float32
) -> np.dtype:
    mapping: Dict[np.dtype, type] = {
        np.dtype(np.complex64): np.float32,
        np.dtype(np.complex128): np.float64,
        np.dtype(complex): np.dtype(float).type,
    }
    dt = np.dtype(d)
    if dt.kind == "f":
        return dt
    return np.dtype(mapping.get(dt, default))


def fix_length(
    data: cp.ndarray, *, size: int, axis: int = -1, **kwargs: Any
) -> cp.ndarray:
    kwargs.setdefault("mode", "constant")
    n = data.shape[axis]

    if n > size:
        slices = [slice(None)] * data.ndim
        slices[axis] = slice(0, size)
        return data[tuple(slices)]
    elif n < size:
        lengths = [(0, 0)] * data.ndim
        lengths[axis] = (0, size - n)
        return cp.pad(data, lengths, **kwargs)
    return data


def tiny(x: ArrayLike):
    x = cp.asarray(x)
    x = cast(np.ndarray, x)  # Only to satisfy type checker
    if cp.issubdtype(x.dtype, cp.floating) or cp.issubdtype(
        x.dtype, cp.complexfloating
    ):
        dtype = x.dtype
    else:
        dtype = cp.dtype(cp.float32)
    return cp.finfo(dtype).tiny


def phasor(
    angles: cp.ndarray,
    *,
    mag: Optional[cp.ndarray] = None,
) -> cp.ndarray:
    # Use cos+sin to match original behavior
    z = cp.cos(angles) + 1j * cp.sin(angles)
    if mag is not None:
        z = z * mag
    return z


def to_cupy_array(y: Union[np.ndarray, cp.ndarray]) -> cp.ndarray:
    if isinstance(y, cp.ndarray):
        return y
    return cp.asarray(y)


def overlap_add(y: cp.ndarray, ytmp: cp.ndarray, hop_length: int) -> None:
    """
    y: (..., signal_len) real array (float32 or float64)
    ytmp: (..., n_fft, n_frames) real array (may be different dtype than y)
    """
    # Ensure dtypes match the kernel we will call
    if y.dtype not in (cp.float32, cp.float64):
        raise ValueError(f"Unsupported y dtype for overlap-add: {y.dtype}")

    # Cast ytmp to y's dtype to avoid misinterpreting memory in the kernel
    ytmp = ytmp.astype(y.dtype, copy=False)

    # Flatten leading batch dims for a simple per-batch launch
    if y.ndim > 1:
        B = int(np.prod(y.shape[:-1]))
        y2 = y.reshape(B, y.shape[-1])
        ytmp2 = ytmp.reshape(B, ytmp.shape[-2], ytmp.shape[-1])
    else:
        B = 1
        y2 = y.reshape(1, y.shape[-1])
        ytmp2 = ytmp.reshape(1, ytmp.shape[-2], ytmp.shape[-1])

    n_fft = int(ytmp2.shape[-2])
    n_frames = int(ytmp2.shape[-1])
    total = int(n_fft) * int(n_frames)
    grid, block = _launch_config(total)

    # For float64: check atomicAdd(double) support
    needs_fp64_atomic = y.dtype == cp.float64
    if needs_fp64_atomic:
        major, minor = (
            cp.cuda.runtime.getDeviceProperties(cp.cuda.Device().id)["major"],
            cp.cuda.runtime.getDeviceProperties(cp.cuda.Device().id)["minor"],
        )
        cc = major * 10 + minor
        if cc < 60:
            # Fallback: deterministic Python loop (slower but correct on older GPUs)
            n_fft_local = n_fft
            for b in range(B):
                yb = y2[b]
                ytmpb = ytmp2[b]
                # Sequential overlap-add (original logic)
                N = n_fft_local
                for frame_idx in range(n_frames):
                    sample = frame_idx * hop_length
                    N = n_fft_local
                    if N > yb.shape[-1] - sample:
                        N = yb.shape[-1] - sample
                    if N > 0:
                        yb[sample : sample + N] += ytmpb[:N, frame_idx]
            return

    for b in range(B):
        yb = y2[b]
        ytmpb = ytmp2[b]

        # Strides in elements (not bytes) after casting
        itemsize = ytmpb.itemsize
        stride_k = ytmpb.strides[-2] // itemsize
        stride_f = ytmpb.strides[-1] // itemsize

        if y.dtype == cp.float32:
            _overlap_add_f32(
                grid,
                block,
                (
                    ytmpb,
                    np.int64(stride_k),
                    np.int64(stride_f),
                    np.int32(n_fft),
                    np.int32(n_frames),
                    np.int32(hop_length),
                    yb,
                    np.int32(yb.size),
                ),
            )
        else:  # float64
            _overlap_add_f64(
                grid,
                block,
                (
                    ytmpb,
                    np.int64(stride_k),
                    np.int64(stride_f),
                    np.int32(n_fft),
                    np.int32(n_frames),
                    np.int32(hop_length),
                    yb,
                    np.int32(yb.size),
                ),
            )
