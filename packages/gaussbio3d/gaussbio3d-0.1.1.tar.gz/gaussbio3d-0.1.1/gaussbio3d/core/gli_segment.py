"""
Segment-level GLI and batch computation
线段级GLI及批量计算

Provides vectorized and optionally Numba-accelerated batch GLI between
arrays of segment endpoints.

提供对线段端点数组的矢量化（可选Numba加速）批量GLI计算。
"""

from __future__ import annotations

import numpy as np
import math

_HAS_NUMBA = False
try:
    import numba  # type: ignore

    _HAS_NUMBA = True
except Exception:
    _HAS_NUMBA = False


def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    n = np.where(n < 1e-12, 1.0, n)
    return v / n


def _arc_sin_clamp(x: np.ndarray) -> np.ndarray:
    return np.arcsin(np.clip(x, -1.0, 1.0))


def gli_segment(seg1, seg2, signed: bool = False) -> float:
    """
    Single-segment GLI (kept for convenience and backward compatibility).
    单线段GLI（为方便与向后兼容保留）。
    """
    a0 = seg1.start
    a1 = seg1.end
    b0 = seg2.start
    b1 = seg2.end

    r00 = b0 - a0
    r01 = b1 - a0
    r10 = b0 - a1
    r11 = b1 - a1

    u00 = _unit(r00[None, :])[0]
    u01 = _unit(r01[None, :])[0]
    u10 = _unit(r10[None, :])[0]
    u11 = _unit(r11[None, :])[0]

    n0 = _unit(np.cross(u00, u01)[None, :])[0]
    n1 = _unit(np.cross(u01, u11)[None, :])[0]
    n2 = _unit(np.cross(u11, u10)[None, :])[0]
    n3 = _unit(np.cross(u10, u00)[None, :])[0]

    area = (
        float(_arc_sin_clamp(np.dot(n0, n1)))
        + float(_arc_sin_clamp(np.dot(n1, n2)))
        + float(_arc_sin_clamp(np.dot(n2, n3)))
        + float(_arc_sin_clamp(np.dot(n3, n0)))
    )

    sign = 1.0
    if signed:
        t1 = a1 - a0
        t2 = b1 - b0
        triple = float(np.dot(np.cross(t1, t2), r00))
        sign = np.sign(triple) if abs(triple) > 1e-12 else 1.0

    gli = sign * area / (4.0 * np.pi)
    return abs(gli) if not signed else gli


def gli_segment_batch(
    a0: np.ndarray,
    a1: np.ndarray,
    b0: np.ndarray,
    b1: np.ndarray,
    signed: bool = False,
) -> np.ndarray:
    """
    Vectorized GLI over batches of segment endpoints.
    对线段端点批次的矢量化GLI计算。

    Parameters
    ----------
    a0, a1, b0, b1 : np.ndarray
        Arrays of shape (N, 3) for segment endpoints.
        线段端点数组，形状为 (N, 3)
    signed : bool
        Whether to keep sign (chirality) / 是否保留符号（手性）

    Returns
    -------
    np.ndarray
        GLI values of shape (N,).
        GLI值，形状为 (N,)
    """
    assert a0.shape == a1.shape == b0.shape == b1.shape
    assert a0.ndim == 2 and a0.shape[1] == 3

    r00 = b0 - a0
    r01 = b1 - a0
    r10 = b0 - a1
    r11 = b1 - a1

    u00 = _unit(r00)
    u01 = _unit(r01)
    u10 = _unit(r10)
    u11 = _unit(r11)

    n0 = _unit(np.cross(u00, u01))
    n1 = _unit(np.cross(u01, u11))
    n2 = _unit(np.cross(u11, u10))
    n3 = _unit(np.cross(u10, u00))

    area = (
        _arc_sin_clamp(np.sum(n0 * n1, axis=-1))
        + _arc_sin_clamp(np.sum(n1 * n2, axis=-1))
        + _arc_sin_clamp(np.sum(n2 * n3, axis=-1))
        + _arc_sin_clamp(np.sum(n3 * n0, axis=-1))
    )

    if signed:
        t1 = a1 - a0
        t2 = b1 - b0
        triple = np.sum(np.cross(t1, t2) * r00, axis=-1)
        sign = np.where(np.abs(triple) > 1e-12, np.sign(triple), 1.0)
    else:
        sign = 1.0

    gli = sign * area / (4.0 * np.pi)
    return np.abs(gli) if not signed else gli


if _HAS_NUMBA:

    @numba.njit(fastmath=True, parallel=True)
    def _unit_nb(v: np.ndarray) -> np.ndarray:
        n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
        if n < 1e-12:
            n = 1.0
        return np.array([v[0] / n, v[1] / n, v[2] / n])

    @numba.njit(fastmath=True)
    def _cross_nb(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return np.array([
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        ])

    @numba.njit(fastmath=True)
    def _dot_nb(a: np.ndarray, b: np.ndarray) -> float:
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    @numba.njit(fastmath=True)
    def _asin_clamp_nb(x: float) -> float:
        if x < -1.0:
            x = -1.0
        elif x > 1.0:
            x = 1.0
        return math.asin(x)

    @numba.njit(fastmath=True, parallel=True)
    def gli_segment_batch_numba(
        a0: np.ndarray,
        a1: np.ndarray,
        b0: np.ndarray,
        b1: np.ndarray,
        signed: bool = False,
    ) -> np.ndarray:
        N = a0.shape[0]
        out = np.empty(N, dtype=np.float64)
        for k in numba.prange(N):
            r00 = b0[k] - a0[k]
            r01 = b1[k] - a0[k]
            r10 = b0[k] - a1[k]
            r11 = b1[k] - a1[k]

            u00 = _unit_nb(r00)
            u01 = _unit_nb(r01)
            u10 = _unit_nb(r10)
            u11 = _unit_nb(r11)

            n0 = _unit_nb(_cross_nb(u00, u01))
            n1 = _unit_nb(_cross_nb(u01, u11))
            n2 = _unit_nb(_cross_nb(u11, u10))
            n3 = _unit_nb(_cross_nb(u10, u00))

            area = (
                _asin_clamp_nb(_dot_nb(n0, n1))
                + _asin_clamp_nb(_dot_nb(n1, n2))
                + _asin_clamp_nb(_dot_nb(n2, n3))
                + _asin_clamp_nb(_dot_nb(n3, n0))
            )

            sign = 1.0
            if signed:
                t1 = a1[k] - a0[k]
                t2 = b1[k] - b0[k]
                triple = _dot_nb(_cross_nb(t1, t2), r00)
                if abs(triple) > 1e-12:
                    sign = math.copysign(1.0, triple)
                else:
                    sign = 1.0

            gli = sign * area / (4.0 * math.pi)
            if not signed:
                gli = abs(gli)
            out[k] = gli
        return out

    def gli_segment_batch_accel(
        a0: np.ndarray,
        a1: np.ndarray,
        b0: np.ndarray,
        b1: np.ndarray,
        signed: bool = False,
    ) -> np.ndarray:
        """
        Accelerated batch GLI using numba when available.
        当可用时，使用numba的加速批量GLI。
        """
        return gli_segment_batch_numba(a0, a1, b0, b1, signed)
else:

    def gli_segment_batch_accel(
        a0: np.ndarray,
        a1: np.ndarray,
        b0: np.ndarray,
        b1: np.ndarray,
        signed: bool = False,
    ) -> np.ndarray:
        """
        Fallback to numpy vectorized implementation when numba is unavailable.
        当numba不可用时，回退到numpy的矢量化实现。
        """
        return gli_segment_batch(a0, a1, b0, b1, signed)

__all__ = [
    "gli_segment",
    "gli_segment_batch",
    "gli_segment_batch_accel",
]