import math
import warnings
from typing import Literal, Optional, Union, cast

import cupy as cp
import numpy as np  # For dtype, RNG compatibility with existing API
from numpy.typing import DTypeLike

from anspec.core.cupy_stft.util import (
    dtype_c2r,
    dtype_r2c,
    expand_to,
    fix_length,
    frame,
    get_fftlib,
    get_window,
    is_positive_int,
    max_fft_columns,
    max_irfft_columns,
    overlap_add,
    pad_center,
    phasor,
    tiny,
    to_cupy_array,
    valid_audio,
    window_sumsquare,
)
from anspec.types import Array1D, Array2D


def stft(
    y: Array1D,
    *,
    n_fft: int = 2048,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    window: Literal["hann"] = "hann",
    center: bool = True,
    dtype: DTypeLike | None = None,
    pad_mode: Literal["constant"] = "constant",
    out: Optional[Array2D] = None,
    skip_y_validation: bool = False,
) -> Array2D:
    # Default use entire frame
    if win_length is None:
        win_length = n_fft

    if hop_length is None:
        hop_length = int(win_length // 4)
    elif not is_positive_int(hop_length):
        raise ValueError(f"hop_length={hop_length} must be a positive integer")

    # Validate and move to GPU
    if not skip_y_validation:
        # valid_audio function has high runtime cost
        # It is skipped in the griffin-lim function
        valid_audio(y)
    y = to_cupy_array(y)

    fft_window = get_window(window, win_length, fftbins=True)
    fft_window = pad_center(fft_window, size=n_fft)
    fft_window = expand_to(fft_window, ndim=1 + y.ndim, axes=-2)

    # Padding logic (GPU)
    if center:
        if pad_mode in ("wrap", "maximum", "mean", "median", "minimum"):
            raise ValueError(f"pad_mode='{pad_mode}' is not supported by this stft")

        if n_fft > y.shape[-1]:
            warnings.warn(
                f"n_fft={n_fft} is too large for input signal of length={y.shape[-1]}"
            )

        padding = [(0, 0) for _ in range(y.ndim)]

        start_k = int(math.ceil(n_fft // 2 / hop_length))
        tail_k = (y.shape[-1] + n_fft // 2 - n_fft) // hop_length + 1

        if tail_k <= start_k:
            start = 0
            extra = 0
            padding[-1] = (n_fft // 2, n_fft // 2)
            y = cp.pad(y, padding, mode=pad_mode)
        else:
            start = start_k * hop_length - n_fft // 2
            padding[-1] = (n_fft // 2, 0)

            y_pre = cp.pad(
                y[..., : (start_k - 1) * hop_length - n_fft // 2 + n_fft + 1],
                padding,
                mode=pad_mode,
            )
            y_frames_pre = frame(y_pre, frame_length=n_fft, hop_length=hop_length)
            y_frames_pre = y_frames_pre[..., :start_k]
            extra = y_frames_pre.shape[-1]

            if tail_k * hop_length - n_fft // 2 + n_fft <= y.shape[-1] + n_fft // 2:
                padding[-1] = (0, n_fft // 2)
                y_post = cp.pad(
                    y[..., (tail_k) * hop_length - n_fft // 2 :], padding, mode=pad_mode
                )
                y_frames_post = frame(y_post, frame_length=n_fft, hop_length=hop_length)
                extra += y_frames_post.shape[-1]
            else:
                post_shape = list(y_frames_pre.shape)
                post_shape[-1] = 0
                y_frames_post = cp.empty(post_shape, dtype=y_frames_pre.dtype)
    else:
        if n_fft > y.shape[-1]:
            raise ValueError(
                f"n_fft={n_fft} is too large for uncentered analysis of input signal of length={y.shape[-1]}"
            )
        start = 0
        extra = 0

    fft = get_fftlib()

    if dtype is None:
        dtype = dtype_r2c(y.dtype)

    y_frames = frame(y[..., start:], frame_length=n_fft, hop_length=hop_length)

    shape = list(y_frames.shape)
    shape[-2] = 1 + n_fft // 2
    shape[-1] += extra

    if out is None:
        stft_matrix = cp.zeros(shape, dtype=dtype, order="F")
    else:
        # Ensure out has sufficient shape
        if not (
            tuple(out.shape[:-1]) == tuple(shape[:-1]) and out.shape[-1] >= shape[-1]
        ):
            raise ValueError(
                f"Shape mismatch for provided output array out.shape={out.shape} and target shape={shape}"
            )
        if not cp.iscomplexobj(out):
            raise ValueError(f"output with dtype={out.dtype} is not of complex type")
        stft_matrix = out if tuple(out.shape) == tuple(shape) else out[..., : shape[-1]]

    # Warm-up fill for padding edges
    if center and extra > 0:
        off_start = y_frames_pre.shape[-1]
        stft_matrix[..., :off_start] = fft.rfft(fft_window * y_frames_pre, axis=-2)

        off_end = y_frames_post.shape[-1]
        if off_end > 0:
            stft_matrix[..., -off_end:] = fft.rfft(fft_window * y_frames_post, axis=-2)
    else:
        off_start = 0

    n_columns = max_fft_columns(y_frames)

    for bl_s in range(0, y_frames.shape[-1], n_columns):
        bl_t = min(bl_s + n_columns, y_frames.shape[-1])
        stft_matrix[..., bl_s + off_start : bl_t + off_start] = fft.rfft(
            fft_window * y_frames[..., bl_s:bl_t], axis=-2
        )

    return stft_matrix  # type: ignore


def istft(
    stft_matrix: Array2D,
    *,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    n_fft: Optional[int] = None,
    window: Literal["hann"] = "hann",
    center: bool = True,
    dtype: Optional[DTypeLike] = None,
    length: Optional[int] = None,
    out: Optional[Array1D] = None,
) -> Array1D:
    if n_fft is None:
        n_fft = 2 * (stft_matrix.shape[-2] - 1)
    n_fft = cast(int, n_fft)

    if win_length is None:
        win_length = n_fft

    if hop_length is None:
        hop_length = int(win_length // 4)

    ifft_window = get_window(window, win_length, fftbins=True)
    ifft_window = pad_center(ifft_window, size=n_fft)
    ifft_window = expand_to(ifft_window, ndim=stft_matrix.ndim, axes=-2)

    if length:
        if center:
            padded_length = length + 2 * (n_fft // 2)
        else:
            padded_length = length
        n_frames = min(
            stft_matrix.shape[-1], int(math.ceil(padded_length / hop_length))
        )
    else:
        n_frames = stft_matrix.shape[-1]

    if dtype is None:
        dtype = dtype_c2r(stft_matrix.dtype)

    shape = list(stft_matrix.shape[:-2])
    expected_signal_len = n_fft + hop_length * (n_frames - 1)
    if length:
        expected_signal_len = length
    elif center:
        expected_signal_len -= 2 * (n_fft // 2)
    shape.append(expected_signal_len)

    if out is None:
        y = cp.zeros(shape, dtype=dtype)
    else:
        if tuple(out.shape) != tuple(shape):
            raise ValueError(
                f"Shape mismatch for provided output array out.shape={out.shape} != {shape}"
            )
        y = out
        y.fill(0.0)

    fft = get_fftlib()

    if center:
        start_frame = int(math.ceil((n_fft // 2) / hop_length))
        ytmp = ifft_window * fft.irfft(stft_matrix[..., :start_frame], n=n_fft, axis=-2)

        shape_head = list(shape)
        shape_head[-1] = n_fft + hop_length * (start_frame - 1)
        head_buffer = cp.zeros(shape_head, dtype=dtype)
        overlap_add(head_buffer, ytmp, hop_length)

        if y.shape[-1] < shape_head[-1] - n_fft // 2:
            y[..., :] = head_buffer[..., n_fft // 2 : y.shape[-1] + n_fft // 2]
        else:
            y[..., : shape_head[-1] - n_fft // 2] = head_buffer[..., n_fft // 2 :]

        offset = start_frame * hop_length - n_fft // 2
    else:
        start_frame = 0
        offset = 0

    # Determine output real dtype
    r_dtype = np.dtype(dtype) if dtype is not None else dtype_c2r(stft_matrix.dtype)

    # Compute frames to process per batch starting at start_frame
    n_columns = max_irfft_columns(stft_matrix[..., start_frame:], n_fft, r_dtype)

    frame_idx = 0
    for bl_s in range(start_frame, n_frames, n_columns):
        bl_t = min(bl_s + n_columns, n_frames)
        ytmp = ifft_window * fft.irfft(stft_matrix[..., bl_s:bl_t], n=n_fft, axis=-2)
        overlap_add(y[..., frame_idx * hop_length + offset :], ytmp, hop_length)
        frame_idx += bl_t - bl_s

    ifft_window_sum = window_sumsquare(
        window=window,
        n_frames=n_frames,
        win_length=win_length,
        n_fft=n_fft,
        hop_length=hop_length,
        dtype=dtype,
    )

    start = n_fft // 2 if center else 0
    ifft_window_sum = fix_length(ifft_window_sum[..., start:], size=y.shape[-1])

    # approx_nonzero_indices = ifft_window_sum > tiny(ifft_window_sum)
    # y[..., approx_nonzero_indices] /= ifft_window_sum[approx_nonzero_indices]

    # return y

    # Ensure on-device and match y's dtype
    den = cp.asarray(ifft_window_sum, dtype=y.dtype)

    # Build a safe multiplicative inverse with cp.where (widely supported)
    eps = tiny(den)
    one = den.dtype.type(1.0)
    inv = cp.where(den > eps, one / den, one)

    # Broadcast across all leading dims of y
    expand_shape = (1,) * (y.ndim - inv.ndim) + tuple(inv.shape)
    inv_b = inv.reshape(expand_shape)

    # In-place normalization
    y *= inv_b

    return y


def griffinlim(
    S: Array2D,
    *,
    n_iter: int = 32,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    n_fft: Optional[int] = None,
    window: Literal["hann"] = "hann",
    center: bool = True,
    dtype: Optional[DTypeLike] = None,
    length: Optional[int] = None,
    pad_mode: Literal["constant"] = "constant",
    momentum: float = 0.99,
    init: Optional[str] = "random",
    random_state: Optional[
        Union[int, np.random.RandomState, np.random.Generator]
    ] = None,
) -> Array1D:
    if momentum > 1:
        warnings.warn(
            f"Griffin-Lim with momentum={momentum} > 1 can be unstable. "
            "Proceed with caution!",
            stacklevel=2,
        )
    elif momentum < 0:
        raise ValueError(f"griffinlim() called with momentum={momentum} < 0")

    # Move S to GPU
    S_gpu = to_cupy_array(S)

    # Infer n_fft from the spectrogram shape
    if n_fft is None:
        n_fft = 2 * (S_gpu.shape[-2] - 1)
    n_fft = cast(int, n_fft)

    # Infer dtype from S
    angles = cp.empty(S_gpu.shape, dtype=dtype_r2c(S_gpu.dtype))
    eps = tiny(angles)

    if init == "random":
        # To preserve exact reproducibility with your existing API:
        # - If random_state is int or a NumPy RNG, generate on CPU with NumPy and transfer.
        # - Else, generate on GPU with CuPy.
        if random_state is None:
            rnd = cp.random.random(size=S_gpu.shape, dtype=cp.float64)  # type: ignore
        elif isinstance(random_state, int):
            rs = np.random.RandomState(seed=random_state)
            rnd = cp.asarray(rs.random_sample(size=S_gpu.shape), dtype=cp.float64)
        elif isinstance(random_state, (np.random.RandomState, np.random.Generator)):
            rnd = cp.asarray(random_state.random(size=S_gpu.shape), dtype=cp.float64)
        else:
            raise ValueError(f"Unsupported random_state={random_state!r}")

        angles[:] = phasor((2 * cp.pi * rnd))
    elif init is None:
        angles[:] = 1.0
    else:
        raise ValueError(f"init={init} must either None or 'random'")

    rebuilt: Optional[cp.ndarray] = None
    tprev: Optional[cp.ndarray] = None
    inverse: Optional[cp.ndarray] = None

    # Absorb magnitudes into angles
    angles *= S_gpu

    for _ in range(n_iter):
        inverse = istft(
            angles,
            hop_length=hop_length,
            win_length=win_length,
            n_fft=n_fft,
            window=window,
            center=center,
            dtype=dtype,
            length=length,
            out=inverse,
        )

        rebuilt = stft(
            inverse,
            n_fft=n_fft,
            hop_length=hop_length,
            win_length=win_length,
            window=window,
            center=center,
            pad_mode=pad_mode,
            out=rebuilt,
            skip_y_validation=True,
        )

        angles[:] = rebuilt
        if tprev is not None:
            angles -= (momentum / (1 + momentum)) * tprev
        angles /= cp.abs(angles) + eps
        angles *= S_gpu

        rebuilt, tprev = tprev, rebuilt

    return istft(
        angles,
        hop_length=hop_length,
        win_length=win_length,
        n_fft=n_fft,
        window=window,
        center=center,
        dtype=dtype,
        length=length,
        out=inverse,
    )
