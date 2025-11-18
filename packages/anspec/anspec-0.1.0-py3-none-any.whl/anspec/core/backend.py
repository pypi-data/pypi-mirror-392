from functools import cache

import numpy as np

from anspec.types import Device, GriffinLimFunc, ISTFTFunc, NumPyOrCuPy, STFTFunc


@cache
def check_and_return_cupy() -> NumPyOrCuPy:
    try:
        import cupy as cp  # type: ignore # noqa

        if not cp.is_available():
            raise RuntimeError(
                "No CUDA-capable device is detected. Make sure your system has a CUDA-capable GPU and you installed the correct CUDA-specific CuPy build (e.g., cupy-cuda12x)"
            )
    except ImportError:
        raise ImportError(
            "GPU / CUDA backend not available. Install CuPy: `https://docs.cupy.dev/en/stable/install.html`"
        )
    return cp


@cache
def check_librosa():
    try:
        import librosa  # type: ignore # NOQA
    except ImportError:
        raise ImportError(
            "Librosa not available. Install librosa: `https://librosa.org/doc/latest/install.html`"
        )


@cache
def get_stft_backend(
    device: Device = "cpu",
) -> STFTFunc:
    if device == "cpu":
        check_librosa()
        from librosa.core.spectrum import stft  # type: ignore

        return stft
    elif device == "cuda":
        check_and_return_cupy()
        from anspec.core.cupy_stft import stft

        return stft
    else:
        raise ValueError(f"Invalid device: {device}")


@cache
def get_istft_backend(
    device: Device = "cpu",
) -> ISTFTFunc:
    if device == "cpu":
        check_librosa()
        from librosa.core.spectrum import istft  # type: ignore

        return istft
    elif device == "cuda":
        check_and_return_cupy()
        from anspec.core.cupy_stft import istft

        return istft
    else:
        raise ValueError(f"Invalid device: {device}")


@cache
def get_griffin_lim_backend(
    device: Device = "cpu",
) -> GriffinLimFunc:
    if device == "cpu":
        check_librosa()
        from librosa.core.spectrum import griffinlim  # type: ignore

        return griffinlim
    elif device == "cuda":
        check_and_return_cupy()
        from anspec.core.cupy_stft import griffinlim

        return griffinlim
    else:
        raise ValueError(f"Invalid device: {device}")


@cache
def get_xp_backend(device: Device = "cpu") -> NumPyOrCuPy:
    if device == "cpu":
        return np
    elif device == "cuda":
        return check_and_return_cupy()
    else:
        raise ValueError(f"Invalid device: {device}")
