import warnings
from functools import lru_cache
from math import ceil, floor

import numpy as np
from scipy.optimize import brentq
from scipy.special import erf
from scipy.stats import norm

from anspec.core.backend import get_xp_backend
from anspec.types import (
    Array1D,
    Array2D,
    Device,
    DTypeLike,
    FilterbankFunc,
    FilterbankLike,
)


def fft_frequencies(*, sr: float, n_fft: int, device: Device = "cpu") -> Array1D:
    xp = get_xp_backend(device)
    return xp.fft.rfftfreq(n=n_fft, d=1.0 / sr)


def hz_to_an[T: float | np.ndarray](hz: T, device: Device = "cpu") -> T:
    xp = get_xp_backend(device)
    return xp.log2(hz)  # type: ignore


def an_to_hz[T: float | np.ndarray](an: T) -> T:
    return 2**an  # type: ignore


def an_frequencies(
    *,
    n_bins: int,
    fmin: float,
    fmax: float,
    device: Device = "cpu",
) -> Array1D:
    # 'Center freqs' of mel bands - uniformly spaced between limits
    min_mel = hz_to_an(fmin, device=device)
    max_mel = hz_to_an(fmax, device=device)

    xp = get_xp_backend(device)

    mels = xp.linspace(min_mel, max_mel, n_bins)

    hz = an_to_hz(mels)
    return hz


def an_filterbank_triangular(
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    dtype: DTypeLike,
    device: Device = "cpu",
) -> Array2D:
    return _an_filterbank_triangular_impl_cached(
        sr=sr,
        n_fft=n_fft,
        n_bins=n_bins,
        fmin=fmin,
        dtype=dtype,  # type: ignore
        device=device,
    )


@lru_cache
def _an_filterbank_triangular_impl_cached(
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    dtype: DTypeLike,
    device: Device = "cpu",
) -> Array2D:
    xp = get_xp_backend(device)
    assert fmin >= 1, "fmin must be greater than 1"
    fmax = float(sr) / 2

    # Initialize the weights
    n_bins = int(n_bins)
    weights = xp.zeros((n_bins, int(1 + n_fft // 2)), dtype=dtype)

    # Center freqs of each FFT bin
    # Shape: (n_fft / 2 + 1, ), values from 0 to sr/2
    fftfreqs = fft_frequencies(sr=sr, n_fft=n_fft, device=device)

    # 'Center freqs' of mel bands - uniformly spaced between limits
    # Shape: (n_bins + 2, ), values from fmin to sr/2
    # Log-spaced in numeric values (linear-spaced in `an` scale)
    mel_f = an_frequencies(n_bins=n_bins + 2, fmin=fmin, fmax=fmax, device=device)

    fdiff = xp.diff(mel_f)
    ramps = xp.subtract.outer(mel_f, fftfreqs)
    # Creates a 2D matrix where ramps[i, j] = mel_f[i] - fftfreqs[j]
    # Shape: (n_bins + 2, n_fft / 2 + 1)

    for i in range(n_bins):
        # lower and upper slopes for all bins
        lower = -ramps[i] / fdiff[i]
        upper = ramps[i + 2] / fdiff[i + 1]

        # .. then intersect them with each other and zero
        weights[i] = xp.maximum(0, xp.minimum(lower, upper))

    # Slaney-style mel is scaled to be approx constant energy per channel
    enorm = 2.0 / (mel_f[2 : n_bins + 2] - mel_f[:n_bins])
    weights *= enorm[:, xp.newaxis]

    # Only check weights if f_mel[0] is positive
    if not xp.all((mel_f[:-2] == 0) | (weights.max(axis=1) > 0)):
        # This means we have an empty channel somewhere
        warnings.warn(
            "Empty filters detected in mel frequency basis. "
            "Some channels will produce empty responses. "
            "Try increasing your sampling rate (and fmax) or "
            "reducing n_bins.",
            stacklevel=2,
        )

    return weights


def an_filterbank_rectangular(
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    dtype: DTypeLike,
    device: Device = "cpu",
) -> Array2D:
    return _an_filterbank_rectangular_impl_cached(
        sr=sr,
        n_fft=n_fft,
        n_bins=n_bins,
        fmin=fmin,
        dtype=dtype,  # type: ignore
        device=device,
    )


@lru_cache
def _an_filterbank_rectangular_impl_cached(
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    dtype: DTypeLike,
    device: Device = "cpu",
) -> Array2D:
    n_fft_bins = n_fft // 2 + 1
    fft_bin_size = sr / 2 / n_fft_bins
    an_freqs = an_frequencies(n_bins=n_bins + 1, fmin=fmin, fmax=sr / 2)
    an_widths = np.diff(an_freqs)

    filterbank = np.zeros((n_bins, n_fft_bins), dtype=dtype)
    for i, (start, width) in enumerate(zip(an_freqs, an_widths)):
        start_index = start / fft_bin_size
        end_index = (start + width) / fft_bin_size
        if floor(start_index) == floor(end_index):
            # This an-bin falls inside one fft-bin
            filterbank[i][floor(start_index)] = end_index - start_index
        elif ceil(start_index) == floor(end_index):
            # This an-bin falls in between two fft-bins
            filterbank[i][floor(start_index)] = ceil(start_index) - start_index
            if floor(end_index) != n_fft_bins:
                filterbank[i][floor(end_index)] = end_index - floor(end_index)
        elif ceil(start_index) < floor(end_index):
            # This an-bin spans >= three fft-bins
            filterbank[i][floor(start_index)] = ceil(start_index) - start_index
            filterbank[i][ceil(start_index) : floor(end_index)] = 1
            if floor(end_index) != n_fft_bins:
                filterbank[i][floor(end_index)] = end_index - floor(end_index)

    xp = get_xp_backend(device)
    return xp.asarray(filterbank)


def log_normal_pmf(
    *,
    n_bins: int,
    bin_size: float,
    mu: float,
    sigma: float,
    dtype: DTypeLike,
    device: Device = "cpu",
) -> Array1D:
    """
    Compute discrete integrals of a log-normal distribution over contiguous ranges.
    """
    if n_bins <= 0:
        raise ValueError("n_bins must be a positive integer.")
    if bin_size <= 0:
        raise ValueError("bin_size must be a positive float.")
    if sigma <= 0:
        raise ValueError("sigma must be positive.")

    # Bin edges: 0, bin_size, 2*bin_size, ..., n_bins*bin_size
    edges = np.linspace(0.0, n_bins * bin_size, num=n_bins + 1, dtype=dtype)

    # Log-normal CDF values at the edges
    cdf = np.zeros_like(edges, dtype=dtype)
    positive_mask = edges > 0.0

    if np.any(positive_mask):
        log_edges = np.log(edges[positive_mask])
        z = (log_edges - mu) / (sigma * np.sqrt(2.0))
        cdf[positive_mask] = 0.5 * (1.0 + erf(z))

    # Probability mass in each bin is the difference of CDF values at its edges
    pmf = np.diff(cdf)
    return pmf


type Mu = float
type Sigma = float


def infer_lognormal_params(
    mode: float,
    left: float,
    right: float,
    mass: float,
    rel_tol_equal_density: float = 1e-8,
    xtol: float = 1e-12,
    rtol: float = 1e-12,
    maxiter: int = 1000,
) -> tuple[Mu, Sigma]:
    """
    Compute sigma and mu for a LogNormal(mu, sigma^2) given:
      - mode,
      - edges A < mode < B with equal pdf(A) = pdf(B) (equivalently A*B = mode^2),
      - probability mass P(A <= X <= B).

    Returns:
      sigma, mu  where mu = ln(mode) + sigma^2.
    """

    # Basic validation
    if mode <= 0 or left <= 0 or right <= 0:
        raise ValueError("mode, left, and right must be positive.")
    if not (left < mode < right):
        raise ValueError(
            "Require left < mode < right for a meaningful symmetric-by-density interval."
        )
    if not (0 < mass < 1):
        raise ValueError("mass must be strictly between 0 and 1.")

    # Equal-density check: A*B should equal M^2
    if not np.isclose(left * right, mode * mode, rtol=rel_tol_equal_density, atol=0.0):
        raise ValueError(
            "Endpoints must satisfy A*B = M^2 for equal density at A and B (given the mode M)."
        )

    # Half-width in log-space relative to the mode
    d = 0.5 * np.log(right / left)  # equals ln(B/M) = -ln(A/M)

    # Define the function whose root in sigma we seek:
    # F(sigma) = Phi((d - sigma^2)/sigma) - Phi((-d - sigma^2)/sigma) - n
    def F(s: float) -> np.ndarray:
        z1 = (d - s * s) / s
        z0 = (-d - s * s) / s
        return norm.cdf(z1) - norm.cdf(z0) - mass

    # Bracket the root: as sigma -> 0+, mass -> 1; as sigma -> inf, mass -> 0
    lo = 1e-12
    f_lo = F(lo)
    if f_lo < 0:
        # This would only happen if n is extremely close to 1 and numerical issues occur.
        # Nudge lo smaller if needed.
        lo = 1e-16
        f_lo = F(lo)
    if f_lo <= 0:
        raise RuntimeError("Failed to establish lower bracket; check inputs.")

    hi = max(10.0, 2.0 * d + 10.0)
    f_hi = F(hi)
    attempts = 0
    while f_hi > 0 and hi < 1e8 and attempts < 100:
        hi *= 2.0
        f_hi = F(hi)
        attempts += 1
    if f_hi >= 0:
        raise RuntimeError(
            "Failed to bracket the root on the upper side; try different inputs."
        )

    # Solve for sigma and mu
    sigma: float = brentq(F, lo, hi, xtol=xtol, rtol=rtol, maxiter=maxiter)  # type: ignore
    mu: float = np.log(mode) + sigma * sigma
    return mu, sigma


def an_filterbank_lognormal(
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    dtype: DTypeLike,
    device: Device = "cpu",
    mass: float = 0.6827,  # Within one standard deviation
    normalize: bool = True,
) -> Array2D:
    return _an_filterbank_lognormal_impl_cached(
        sr=sr,
        n_fft=n_fft,
        n_bins=n_bins,
        fmin=fmin,
        dtype=dtype,  # type: ignore
        device=device,
        mass=mass,
        normalize=normalize,
    )


@lru_cache
def _an_filterbank_lognormal_impl_cached(
    *,
    sr: float,
    n_fft: int,
    n_bins: int,
    fmin: float,
    dtype: DTypeLike,
    device: Device = "cpu",
    mass: float = 0.5,
    normalize: bool = True,
) -> Array2D:
    n_fft_bins = n_fft // 2 + 1
    fft_bin_size = sr / 2 / n_fft_bins
    an_freqs = an_frequencies(n_bins=n_bins + 1, fmin=fmin, fmax=sr / 2)
    filterbank = np.zeros((n_bins, n_fft_bins), dtype=dtype)
    for i in range(len(an_freqs) - 1):
        left: float = an_freqs[i]
        right: float = an_freqs[i + 1]
        mode = (left * right) ** 0.5
        mu, sigma = infer_lognormal_params(mode=mode, left=left, right=right, mass=mass)
        pmf = log_normal_pmf(
            n_bins=n_fft_bins,
            bin_size=fft_bin_size,
            mu=mu,
            sigma=sigma,
            dtype=dtype,
            device=device,
        )
        filterbank[i] = pmf
    if normalize:
        divider = np.zeros(n_bins, dtype=dtype)
        for i in range(len(an_freqs) - 1):
            mode = (an_freqs[i] * an_freqs[i + 1]) ** 0.5
            fft_bin_index = floor(mode / fft_bin_size)
            column_sum = filterbank[:, fft_bin_index].sum()
            divider[i] = column_sum
        filterbank /= divider[:, np.newaxis]
    xp = get_xp_backend(device)
    return xp.asarray(filterbank)


filterbank_type_to_func: dict[FilterbankLike, FilterbankFunc] = {
    "triangular": an_filterbank_triangular,
    "rectangular": an_filterbank_rectangular,
    "lognormal": an_filterbank_lognormal,
}


def get_filterbank_func(filterbank_like: FilterbankLike) -> FilterbankFunc:
    if isinstance(filterbank_like, str):
        return filterbank_type_to_func[filterbank_like]
    elif callable(filterbank_like):
        return filterbank_like
    else:
        raise ValueError(f"Invalid filterbank type: {type(filterbank_like)}")
