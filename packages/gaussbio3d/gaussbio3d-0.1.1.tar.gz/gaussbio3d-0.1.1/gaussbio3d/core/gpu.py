"""
GPU-accelerated batch GLI using PyTorch or CuPy
使用PyTorch或CuPy的GPU加速批量GLI

Provides a torch implementation of gli_segment_batch that mirrors
the numpy version using tensor broadcasting. Falls back to CPU if
torch is unavailable.

提供与numpy版本一致的torch实现，使用张量广播；如果torch不可用则不导出。
"""

from __future__ import annotations

import numpy as np

try:
    import torch  # type: ignore
    _HAS_TORCH = True
except Exception:
    _HAS_TORCH = False


def _unit_t(x: "torch.Tensor") -> "torch.Tensor":
    n = torch.linalg.vector_norm(x, dim=-1, keepdim=True)
    n = torch.where(n < 1e-12, torch.tensor(1.0, device=x.device, dtype=x.dtype), n)
    return x / n


def _asin_clamp_t(x: "torch.Tensor") -> "torch.Tensor":
    return torch.arcsin(torch.clamp(x, -1.0, 1.0))


def gli_segment_batch_torch(
    a0: np.ndarray,
    a1: np.ndarray,
    b0: np.ndarray,
    b1: np.ndarray,
    signed: bool = False,
    device: str | None = None,
) -> np.ndarray:
    """
    Torch-based batch GLI for segment endpoint arrays.
    基于Torch的线段端点数组批量GLI。

    Parameters
    ----------
    a0,a1,b0,b1 : np.ndarray
        Arrays of shape (N,3)
    signed : bool
        Whether to keep sign
    device : str, optional
        Torch device (e.g., "cuda"). If None, uses cuda if available.

    Returns
    -------
    np.ndarray
        GLI values of shape (N,)
    """
    if not _HAS_TORCH:
        raise ImportError("PyTorch is required for GPU GLI (pip install torch)")

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    # Convert to torch tensors
    a0_t = torch.as_tensor(a0, dtype=torch.float64, device=device)
    a1_t = torch.as_tensor(a1, dtype=torch.float64, device=device)
    b0_t = torch.as_tensor(b0, dtype=torch.float64, device=device)
    b1_t = torch.as_tensor(b1, dtype=torch.float64, device=device)

    r00 = b0_t - a0_t
    r01 = b1_t - a0_t
    r10 = b0_t - a1_t
    r11 = b1_t - a1_t

    u00 = _unit_t(r00)
    u01 = _unit_t(r01)
    u10 = _unit_t(r10)
    u11 = _unit_t(r11)

    n0 = _unit_t(torch.cross(u00, u01))
    n1 = _unit_t(torch.cross(u01, u11))
    n2 = _unit_t(torch.cross(u11, u10))
    n3 = _unit_t(torch.cross(u10, u00))

    area = (
        _asin_clamp_t(torch.sum(n0 * n1, dim=-1))
        + _asin_clamp_t(torch.sum(n1 * n2, dim=-1))
        + _asin_clamp_t(torch.sum(n2 * n3, dim=-1))
        + _asin_clamp_t(torch.sum(n3 * n0, dim=-1))
    )

    if signed:
        t1 = a1_t - a0_t
        t2 = b1_t - b0_t
        triple = torch.sum(torch.cross(t1, t2) * r00, dim=-1)
        sign = torch.where(torch.abs(triple) > 1e-12, torch.sign(triple), torch.tensor(1.0, device=device))
    else:
        sign = torch.tensor(1.0, device=device)

    gli = sign * area / (4.0 * np.pi)
    if not signed:
        gli = torch.abs(gli)

    out = gli.detach().cpu().numpy()
    return out


__all__ = ["gli_segment_batch_torch"]

