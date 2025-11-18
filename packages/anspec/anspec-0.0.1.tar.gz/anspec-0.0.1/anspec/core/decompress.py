from typing import Literal, overload

import numpy as np

from anspec.core.backend import get_griffin_lim_backend, get_xp_backend
from anspec.core.convert import get_filterbank_func
from anspec.core.nnls import nnls
from anspec.types import (
    Array1D,
    Array2D,
    CPUArray1D,
    CPUArray2D,
    CUDAArray1D,
    CUDAArray2D,
    Device,
    DTypeLike,
    FilterbankLike,
)


@overload
def anspec_to_spec(
    anspec: Array2D,
    *,
    sr: float,
    n_fft: int,
    fmin: float,
    filterbank_type: FilterbankLike,
    device: Literal["cpu"] = "cpu",
    dtype: DTypeLike | None = np.float32,
    max_iters: int = 1000,
    min_obj: float = 1e-3,
) -> CPUArray2D: ...
@overload
def anspec_to_spec(
    anspec: Array2D,
    *,
    sr: float,
    n_fft: int,
    fmin: float,
    filterbank_type: FilterbankLike,
    device: Literal["cuda"] = "cuda",
    dtype: DTypeLike | None = np.float32,
    max_iters: int = 1000,
    min_obj: float = 1e-3,
) -> CUDAArray2D: ...
def anspec_to_spec(
    anspec: Array2D,
    *,
    sr: float,
    n_fft: int,
    fmin: float,
    filterbank_type: FilterbankLike,
    device: Device = "cpu",
    dtype: DTypeLike | None = np.float32,
    max_iters: int = 1000,
    min_obj: float = 1e-3,
) -> Array2D:
    if dtype is not None:
        anspec = anspec.astype(dtype, copy=False)
    # Construct a mel basis with dtype matching the input data
    mel_basis = get_filterbank_func(filterbank_type)(
        sr=sr,
        n_fft=n_fft,
        n_bins=anspec.shape[-2],
        dtype=anspec.dtype,
        fmin=fmin,
        device=device,
    )

    # Find the non-negative least squares solution
    inverse = nnls(
        A=mel_basis,
        B=anspec,
        max_iters=max_iters,
        min_obj=min_obj,
        device=device,
        dtype=dtype,
    )
    return inverse


@overload
def spec_to_waveform(
    spec: Array2D,
    *,
    n_fft: int,
    hop_length: int,
    power: float = 2,
    center: bool = True,
    device: Literal["cpu"] = "cpu",
    n_iter: int = 32,
    window: Literal["hann"] = "hann",
) -> CPUArray1D: ...
@overload
def spec_to_waveform(
    spec: Array2D,
    *,
    n_fft: int,
    hop_length: int,
    power: float = 2,
    center: bool = True,
    device: Literal["cuda"] = "cuda",
    n_iter: int = 32,
    window: Literal["hann"] = "hann",
) -> CUDAArray1D: ...
def spec_to_waveform(
    spec: Array2D,
    *,
    n_fft: int,
    hop_length: int,
    power: float = 2,
    center: bool = True,
    device: Device = "cpu",
    n_iter: int = 32,
    window: Literal["hann"] = "hann",
) -> Array1D:
    xp = get_xp_backend(device)
    spec = xp.power(spec, 1.0 / power)
    griffinlim = get_griffin_lim_backend(device)
    waveform = griffinlim(
        spec,
        n_iter=n_iter,
        hop_length=hop_length,
        win_length=n_fft,
        n_fft=n_fft,
        window=window,
        center=center,
        length=None,
        pad_mode="constant",
    )
    return waveform


@overload
def anspec_to_waveform(
    anspec: Array2D,
    *,
    sr: float,
    n_fft: int,
    hop_length: int,
    fmin: float,
    filterbank_type: FilterbankLike,
    center: bool = True,
    power: float = 2,
    device: Literal["cpu"] = "cpu",
    griffin_lim_iter: int = 32,
    nnls_max_iters: int = 1000,
    nnls_min_obj: float = 1e-3,
    dtype: DTypeLike | None = np.float32,
    window: Literal["hann"] = "hann",
) -> CPUArray1D: ...
@overload
def anspec_to_waveform(
    anspec: Array2D,
    *,
    sr: float,
    n_fft: int,
    hop_length: int,
    fmin: float,
    filterbank_type: FilterbankLike,
    center: bool = True,
    power: float = 2,
    device: Literal["cuda"] = "cuda",
    griffin_lim_iter: int = 32,
    nnls_max_iters: int = 1000,
    nnls_min_obj: float = 1e-3,
    dtype: DTypeLike | None = np.float32,
    window: Literal["hann"] = "hann",
) -> CUDAArray1D: ...
def anspec_to_waveform(
    anspec: Array2D,
    *,
    sr: float,
    n_fft: int,
    hop_length: int,
    fmin: float,
    filterbank_type: FilterbankLike,
    center: bool = True,
    power: float = 2,
    device: Device = "cpu",
    griffin_lim_iter: int = 32,
    nnls_max_iters: int = 1000,
    nnls_min_obj: float = 1e-3,
    dtype: DTypeLike | None = np.float32,
    window: Literal["hann"] = "hann",
) -> Array1D:
    if dtype is not None:
        anspec = anspec.astype(dtype, copy=False)
    spec = anspec_to_spec(
        anspec,
        sr=sr,
        n_fft=n_fft,
        fmin=fmin,
        filterbank_type=filterbank_type,
        device=device,
        dtype=dtype,
        max_iters=nnls_max_iters,
        min_obj=nnls_min_obj,
    )
    waveform = spec_to_waveform(
        spec,
        n_fft=n_fft,
        hop_length=hop_length,
        power=power,
        center=center,
        device=device,
        n_iter=griffin_lim_iter,
        window=window,
    )

    return waveform
