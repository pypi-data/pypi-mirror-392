import cupy as cp

_overlap_add_f32 = cp.RawKernel(
    r"""
extern "C" __global__
void overlap_add_f32(const float* __restrict__ ytmp,
                     const long long stride_k, const long long stride_f,
                     const int n_fft, const int n_frames, const int hop,
                     float* __restrict__ y, const int y_len) {
    long long tid = blockDim.x * (long long)blockIdx.x + threadIdx.x;
    long long N = (long long)n_fft * (long long)n_frames;
    if (tid >= N) return;
    int k = (int)(tid % n_fft);
    int f = (int)(tid / n_fft);
    int out_idx = f * hop + k;
    if (out_idx < y_len) {
        const float val = ytmp[k * stride_k + f * stride_f];
        atomicAdd(&y[out_idx], val);
    }
}
""",
    "overlap_add_f32",
)

_overlap_add_f64 = cp.RawKernel(
    r"""
extern "C" __global__
void overlap_add_f64(const double* __restrict__ ytmp,
                     const long long stride_k, const long long stride_f,
                     const int n_fft, const int n_frames, const int hop,
                     double* __restrict__ y, const int y_len) {
    long long tid = blockDim.x * (long long)blockIdx.x + threadIdx.x;
    long long N = (long long)n_fft * (long long)n_frames;
    if (tid >= N) return;
    int k = (int)(tid % n_fft);
    int f = (int)(tid / n_fft);
    int out_idx = f * hop + k;
    if (out_idx < y_len) {
        const double val = ytmp[k * stride_k + f * stride_f];
        atomicAdd(&y[out_idx], val);
    }
}
""",
    "overlap_add_f64",
)

_wss_f32 = cp.RawKernel(
    r"""
extern "C" __global__
void wss_f32(const float* __restrict__ win_sq,
             const int n_fft, const int n_frames, const int hop,
             float* __restrict__ out, const int out_len) {
    long long tid = blockDim.x * (long long)blockIdx.x + threadIdx.x;
    long long N = (long long)n_fft * (long long)n_frames;
    if (tid >= N) return;
    int k = (int)(tid % n_fft);
    int f = (int)(tid / n_fft);
    int out_idx = f * hop + k;
    if (out_idx < out_len) {
        atomicAdd(&out[out_idx], win_sq[k]);
    }
}
""",
    "wss_f32",
)

_wss_f64 = cp.RawKernel(
    r"""
extern "C" __global__
void wss_f64(const double* __restrict__ win_sq,
             const int n_fft, const int n_frames, const int hop,
             double* __restrict__ out, const int out_len) {
    long long tid = blockDim.x * (long long)blockIdx.x + threadIdx.x;
    long long N = (long long)n_fft * (long long)n_frames;
    if (tid >= N) return;
    int k = (int)(tid % n_fft);
    int f = (int)(tid / n_fft);
    int out_idx = f * hop + k;
    if (out_idx < out_len) {
        atomicAdd(&out[out_idx], win_sq[k]);
    }
}
""",
    "wss_f64",
)
