from os import PathLike as PathABC
from types import ModuleType
from typing import Literal, Protocol, cast

import numpy as np
from numpy.typing import DTypeLike

type CPUArray1D = np.ndarray
type CPUArray2D = np.ndarray


class CUDAArray[T: np.ndarray](np.ndarray):
    def get(self) -> T:
        return cast(T, self)


type CUDAArray1D = CUDAArray[CPUArray1D]
type CUDAArray2D = CUDAArray[CPUArray2D]

type Array1D = CPUArray1D | CUDAArray1D
type Array2D = CPUArray2D | CUDAArray2D

type PathLike = PathABC | str | bytes
type AudioLike = Array1D | PathLike
type Device = Literal["cpu", "cuda"]


class FilterbankFunc(Protocol):
    def __call__(
        self,
        *,
        sr: float,
        n_fft: int,
        n_bins: int,
        fmin: float,
        dtype: DTypeLike,
        device: Device,
    ) -> Array2D: ...


type FilterbankType = Literal["triangular", "rectangular", "lognormal"]
type FilterbankLike = FilterbankType | FilterbankFunc

type NumPyOrCuPy = ModuleType


class STFTFunc(Protocol):
    def __call__(
        self,
        y: Array1D,
        *,
        n_fft: int,
        hop_length: int,
        win_length: int,
        window: Literal["hann"],
        center: bool = True,
        dtype: DTypeLike | None = None,
        pad_mode: Literal["constant"] = "constant",
        out: Array2D | None = None,
    ) -> Array2D: ...


class ISTFTFunc(Protocol):
    def __call__(
        self,
        stft_matrix: Array2D,
        *,
        n_fft: int,
        hop_length: int,
        win_length: int,
        window: Literal["hann"],
        center: bool = True,
        dtype: DTypeLike | None = None,
        length: int | None = None,
        out: Array1D | None = None,
    ) -> Array1D: ...


class GriffinLimFunc(Protocol):
    def __call__(
        self,
        S: Array2D,
        *,
        n_iter: int = 32,
        hop_length: int | None = None,
        win_length: int | None = None,
        n_fft: int | None = None,
        window: Literal["hann"] = "hann",
        center: bool = True,
        dtype: DTypeLike | None = None,
        length: int | None = None,
        pad_mode: Literal["constant"] = "constant",
        momentum: float = 0.99,
        init: str | None = "random",
        random_state: int | np.random.RandomState | np.random.Generator | None = None,
    ) -> Array1D: ...
