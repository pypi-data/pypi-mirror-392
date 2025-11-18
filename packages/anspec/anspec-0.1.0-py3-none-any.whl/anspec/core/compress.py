from typing import Literal, overload

import numpy as np

from anspec.core.backend import get_stft_backend, get_xp_backend
from anspec.core.convert import get_filterbank_func
from anspec.types import (
    Array1D,
    Array2D,
    CPUArray2D,
    CUDAArray2D,
    Device,
    DTypeLike,
    FilterbankLike,
)


@overload
def waveform_to_spec(
    y: Array1D,
    *,
    n_fft: int,
    hop_length: int,
    power: float = 2,
    win_length: int | None = None,
    center: bool = True,
    device: Literal["cpu"] = "cpu",
    dtype: DTypeLike | None = np.float32,
    window: Literal["hann"] = "hann",
) -> CPUArray2D: ...
@overload
def waveform_to_spec(
    y: Array1D,
    *,
    n_fft: int,
    hop_length: int,
    power: float = 2,
    win_length: int | None = None,
    center: bool = True,
    device: Literal["cuda"] = "cuda",
    dtype: DTypeLike | None = np.float32,
    window: Literal["hann"] = "hann",
) -> CUDAArray2D: ...
def waveform_to_spec(
    y: Array1D,
    *,
    n_fft: int,
    hop_length: int,
    power: float = 2,
    win_length: int | None = None,
    center: bool = True,
    device: Device = "cpu",
    dtype: DTypeLike | None = np.float32,
    window: Literal["hann"] = "hann",
) -> Array2D:
    if win_length is None:
        win_length = n_fft
    if dtype is not None:
        y = y.astype(dtype, copy=False)
    stft = get_stft_backend(device)
    xp = get_xp_backend(device)
    return (
        xp.abs(
            stft(
                y,
                n_fft=n_fft,
                hop_length=hop_length,
                win_length=win_length,
                center=center,
                window=window,
                pad_mode="constant",
            )
        )
        ** power
    )


@overload
def spec_to_anspec(
    spec: Array2D,
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    filterbank_type: FilterbankLike,
    device: Literal["cpu"] = "cpu",
    dtype: DTypeLike | None = np.float32,
) -> CPUArray2D: ...
@overload
def spec_to_anspec(
    spec: Array2D,
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    filterbank_type: FilterbankLike,
    device: Literal["cuda"] = "cuda",
    dtype: DTypeLike | None = np.float32,
) -> CUDAArray2D: ...
def spec_to_anspec(
    spec: Array2D,
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    filterbank_type: FilterbankLike,
    device: Device = "cpu",
    dtype: DTypeLike | None = np.float32,
) -> Array2D:
    if dtype is not None:
        spec = spec.astype(dtype, copy=False)
    # Build a An filterbank

    filterbank = get_filterbank_func(filterbank_type)(
        sr=sr, n_fft=n_fft, n_bins=n_bins, fmin=fmin, dtype=spec.dtype, device=device
    )
    # xp = get_xp_backend(device)
    # return xp.einsum("...ft,mf->...mt", spec, filterbank, optimize=True)
    return filterbank @ spec


@overload
def waveform_to_anspec(
    y: Array1D,
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    hop_length: int,
    filterbank_type: FilterbankLike,
    power: float = 2,
    center: bool = True,
    device: Literal["cpu"] = "cpu",
    dtype: DTypeLike | None = np.float32,
    window: Literal["hann"] = "hann",
) -> CPUArray2D: ...
@overload
def waveform_to_anspec(
    y: Array1D,
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    hop_length: int,
    filterbank_type: FilterbankLike,
    power: float = 2,
    center: bool = True,
    device: Literal["cuda"] = "cuda",
    dtype: DTypeLike | None = np.float32,
    window: Literal["hann"] = "hann",
) -> CUDAArray2D: ...
def waveform_to_anspec(
    y: Array1D,
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    hop_length: int,
    filterbank_type: FilterbankLike,
    power: float = 2,
    center: bool = True,
    device: Device = "cpu",
    dtype: DTypeLike | None = np.float32,
    window: Literal["hann"] = "hann",
) -> Array2D:
    if dtype is not None:
        y = y.astype(dtype, copy=False)
    spectrogram = waveform_to_spec(
        y=y,
        n_fft=n_fft,
        hop_length=hop_length,
        power=power,
        win_length=n_fft,
        center=center,
        device=device,
        dtype=dtype,
        window=window,
    )
    return spec_to_anspec(
        spectrogram,
        sr=sr,
        n_fft=n_fft,
        n_bins=n_bins,
        fmin=fmin,
        filterbank_type=filterbank_type,
        device=device,
        dtype=dtype,
    )
