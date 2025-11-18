from dataclasses import dataclass
from math import log2
from os import PathLike as PathABC
from typing import Literal, cast, overload

import numpy as np
import soundfile as sf

from anspec.core import anspec_to_waveform, waveform_to_anspec
from anspec.types import (
    Array1D,
    Array2D,
    AudioLike,
    CPUArray1D,
    CPUArray2D,
    CUDAArray1D,
    CUDAArray2D,
    Device,
    FilterbankLike,
    PathLike,
)


@dataclass
class Config:
    sr: int
    n_fft: int
    n_bins: int
    hop_length: int
    fmin: float
    filterbank_type: FilterbankLike = "lognormal"
    window: Literal["hann"] = "hann"
    griffin_lim_iter: int = 32
    nnls_max_iters: int = 1000
    nnls_min_obj: float = 1e-8
    power: float = 2
    audio_duration: float | None = None

    @property
    def time_resolution(self) -> float:
        return self.hop_length / self.sr

    @property
    def fft_freq_resolution(self) -> float:
        return self.sr / self.n_fft

    @property
    def freq_range(self) -> tuple[float, float]:
        return self.fmin, self.sr / 2

    @property
    def n_octaves(self) -> float:
        return log2(self.sr / 2 / self.fmin)

    @property
    def n_bins_per_octave(self) -> float:
        return self.n_bins / self.n_octaves

    @property
    def overlap_ratio(self) -> float:
        return self.n_fft / self.hop_length

    @classmethod
    def from_musical(
        cls,
        *,
        sr: int,
        filterbank_type: FilterbankLike = "lognormal",
        n_octaves: float = 10,
        n_bins_per_octave: float = 12,
        time_resolution: float = 0.05,
        overlap_ratio: float = 4,  # equals n_fft / hop_length
        device: Device = "cpu",
        window: Literal["hann"] = "hann",
        griffin_lim_iter: int = 32,
        nnls_max_iters: int = 1000,
        nnls_min_obj: float = 1e-3,
        power: float = 2,
        audio_duration: float | None = None,
    ) -> "Config":
        hop_length = int(round(sr * time_resolution))
        n_fft = int(round(overlap_ratio * hop_length))
        n_bins = int(round(n_octaves * n_bins_per_octave))
        fmin = sr / 2 / (2**n_octaves)

        return cls(
            sr=sr,
            filterbank_type=filterbank_type,
            n_fft=n_fft,
            n_bins=n_bins,
            hop_length=hop_length,
            fmin=fmin,
            window=window,
            griffin_lim_iter=griffin_lim_iter,
            nnls_max_iters=nnls_max_iters,
            nnls_min_obj=nnls_min_obj,
            power=power,
            audio_duration=audio_duration,
        )


@overload
def audio_to_anspec(
    audio: AudioLike, config: Config, device: Literal["cpu"]
) -> CPUArray2D: ...
@overload
def audio_to_anspec(
    audio: AudioLike, config: Config, device: Literal["cuda"]
) -> CUDAArray2D: ...
def audio_to_anspec(audio: AudioLike, config: Config, device: Device) -> Array2D:
    if isinstance(audio, (PathABC, str, bytes)):
        sr: int
        waveform: Array1D
        waveform, sr = sf.read(audio)
        assert waveform is not None, "Unreachable"
        if waveform.ndim == 2:
            waveform = waveform.mean(axis=1)
        if config.audio_duration is not None:
            waveform = waveform[: int(config.audio_duration * sr)]
        if sr != config.sr:
            from scipy.signal import resample

            target_num_samples = round(len(waveform) * config.sr / sr)
            waveform = resample(waveform, num=target_num_samples)  # type: ignore
    else:
        waveform = audio
    return waveform_to_anspec(
        waveform,
        sr=config.sr,
        n_fft=config.n_fft,
        n_bins=config.n_bins,
        fmin=config.fmin,
        hop_length=config.hop_length,
        filterbank_type=config.filterbank_type,
        power=config.power,
        center=True,
        device=device,
        dtype=np.float32,
    )


@overload
def anspec_to_audio(
    anspec: Array2D,
    config: Config,
    device: Literal["cpu"],
    file: PathLike | None = None,
) -> CPUArray1D: ...
@overload
def anspec_to_audio(
    anspec: Array2D,
    config: Config,
    device: Literal["cuda"],
    file: PathLike | None = None,
) -> CUDAArray1D: ...
def anspec_to_audio(
    anspec: Array2D, config: Config, device: Device, file: PathLike | None = None
) -> Array1D:
    waveform = anspec_to_waveform(
        anspec,
        sr=config.sr,
        n_fft=config.n_fft,
        hop_length=config.hop_length,
        fmin=config.fmin,
        filterbank_type=config.filterbank_type,
        center=True,
        power=config.power,
        device=device,
        griffin_lim_iter=config.griffin_lim_iter,
        nnls_max_iters=config.nnls_max_iters,
        nnls_min_obj=config.nnls_min_obj,
        window=config.window,
        dtype=np.float32,
    )
    if file is not None:
        if hasattr(waveform, "get"):
            # Waveform is a CuPy array, call get() to convert to NumPy array
            waveform = cast(CUDAArray1D, waveform)
            sf.write(file, waveform.get(), config.sr)
        else:
            sf.write(file, waveform, config.sr)
    return waveform


@overload
def reconstruct(
    audio: AudioLike,
    config: Config,
    device: Literal["cpu"],
    file: PathLike | None = None,
) -> tuple[CPUArray1D, CPUArray2D]: ...
@overload
def reconstruct(
    audio: AudioLike,
    config: Config,
    device: Literal["cuda"],
    file: PathLike | None = None,
) -> tuple[CUDAArray1D, CUDAArray2D]: ...
def reconstruct(
    audio: AudioLike,
    config: Config,
    device: Device,
    file: PathLike | None = None,
) -> tuple[Array1D, Array2D]:
    anspec = audio_to_anspec(audio, config, device=device)
    waveform = anspec_to_audio(
        anspec,
        config=config,
        device=device,
        file=file,
    )
    return waveform, anspec
