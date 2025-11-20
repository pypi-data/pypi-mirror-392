"""
Persistent Homology (PH) utilities
持久同调(PH)工具

Uses ripser (if available) on precomputed distance matrices to obtain
barcodes, and returns simple persistence summaries / histograms.

依赖ripser（如可用），基于预计算距离矩阵得到条形码，并返回简单的
持久性摘要/直方图。
"""

from __future__ import annotations

import numpy as np

try:
    from ripser import ripser  # type: ignore
    _HAS_RIPSER = True
except Exception:
    _HAS_RIPSER = False


def ph_diagrams_from_distance(rij: np.ndarray, maxdim: int = 2):
    if not _HAS_RIPSER:
        raise ImportError("ripser is required for PH (pip install ripser)")
    res = ripser(rij, distance_matrix=True, maxdim=maxdim)
    return res["dgms"]


def ph_persistence_histogram(dgms: list[np.ndarray], bins: np.ndarray | None = None) -> np.ndarray:
    """
    Build concatenated histogram of (death - birth) per homology dimension.
    为每个同调维度构建(death-birth)的拼接直方图。
    """
    if bins is None:
        bins = np.linspace(0.0, 20.0, 41)  # default 40 bins
    hists = []
    for dgm in dgms:
        lengths = (dgm[:, 1] - dgm[:, 0])
        lengths = lengths[np.isfinite(lengths)]
        hist, _ = np.histogram(np.clip(lengths, 0.0, bins[-1]), bins=bins)
        hists.append(hist.astype(float))
    return np.concatenate(hists, axis=0)


__all__ = ["ph_diagrams_from_distance", "ph_persistence_histogram"]

