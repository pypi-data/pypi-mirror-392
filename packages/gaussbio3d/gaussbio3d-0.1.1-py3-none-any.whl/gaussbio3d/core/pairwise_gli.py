"""
Pairwise node-level GLI using batch segment computation
使用批量线段计算的成对节点级GLI

This module aggregates GLI across segment pairs touching node pairs,
implemented with vectorized batch calls.

本模块在接触节点对的线段对上聚合GLI，使用矢量化批量调用实现。
"""

from __future__ import annotations

import numpy as np
from typing import Tuple, Optional, List

from .geometry import Structure
from .gli_segment import gli_segment_batch_accel as gli_segment_batch
try:
    # Optional GPU backend (PyTorch)
    from .gpu import gli_segment_batch_torch  # type: ignore
    _HAS_TORCH = True
except Exception:
    _HAS_TORCH = False


def compute_pairwise_node_gli(
    struct_A: Structure,
    struct_B: Structure,
    signed: bool = False,
    agg: str = "mean",
    max_distance: Optional[float] = None,
    n_jobs: int = 1,
    use_gpu: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute pairwise node-level GLI and distances between two structures.
    计算两个结构之间的成对节点级GLI和距离。

    Aggregates GLI over all segment pairs incident to nodes i (in A)
    and j (in B), using a vectorized cartesian product.

    使用矢量化笛卡尔积在A中节点i与B中节点j的所有关联线段对上聚合GLI。
    """
    coords_A = struct_A.coords  # (N_A,3)
    coords_B = struct_B.coords  # (N_B,3)
    N_A = coords_A.shape[0]
    N_B = coords_B.shape[0]

    if N_A == 0 or N_B == 0:
        return np.zeros((N_A, N_B)), np.zeros((N_A, N_B))

    # Distances matrix
    rij = np.linalg.norm(coords_A[:, None, :] - coords_B[None, :, :], axis=-1)

    # Pre-extract per-node segment endpoints for reuse
    seg_endpoints_A = []  # list of (a0s, a1s)
    for i in range(N_A):
        segs_i = struct_A.node_segments.get(i, [])
        if not segs_i:
            seg_endpoints_A.append((None, None))
            continue
        a0s = np.stack([s.start for s in segs_i], axis=0)
        a1s = np.stack([s.end for s in segs_i], axis=0)
        seg_endpoints_A.append((a0s, a1s))

    seg_endpoints_B = []  # list of (b0s, b1s)
    for j in range(N_B):
        segs_j = struct_B.node_segments.get(j, [])
        if not segs_j:
            seg_endpoints_B.append((None, None))
            continue
        b0s = np.stack([s.start for s in segs_j], axis=0)
        b1s = np.stack([s.end for s in segs_j], axis=0)
        seg_endpoints_B.append((b0s, b1s))

    gij = np.zeros((N_A, N_B), dtype=float)

    # Precompute candidate j indices per i based on distance pruning
    j_candidates: List[np.ndarray] = []
    if max_distance is not None and max_distance > 0:
        for i in range(N_A):
            j_candidates.append(np.where(rij[i] <= max_distance)[0])
    else:
        for i in range(N_A):
            j_candidates.append(np.arange(N_B, dtype=int))

    def _compute_row(i: int) -> Tuple[int, np.ndarray]:
        a0s, a1s = seg_endpoints_A[i]
        row = np.zeros(N_B, dtype=float)
        if a0s is None:
            return i, row
        ni = a0s.shape[0]
        js = j_candidates[i]
        for j in js:
            b0s, b1s = seg_endpoints_B[j]
            if b0s is None:
                continue
            nj = b0s.shape[0]

            # Cartesian product of segments: (ni * nj, 3)
            A0 = np.repeat(a0s, nj, axis=0)
            A1 = np.repeat(a1s, nj, axis=0)
            B0 = np.tile(b0s, (ni, 1))
            B1 = np.tile(b1s, (ni, 1))

            if use_gpu and _HAS_TORCH:
                vals = gli_segment_batch_torch(A0, A1, B0, B1, signed=signed)
            else:
                vals = gli_segment_batch(A0, A1, B0, B1, signed=signed)

            if vals.size == 0:
                continue
            if agg == "mean":
                row[j] = float(vals.mean())
            elif agg == "median":
                row[j] = float(np.median(vals))
            elif agg == "sum":
                row[j] = float(vals.sum())
            else:
                row[j] = float(vals.mean())
        return i, row

    if n_jobs is None or n_jobs <= 1:
        for i in range(N_A):
            ii, row = _compute_row(i)
            gij[ii] = row
    else:
        # Lightweight threading; numpy releases GIL
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=int(n_jobs)) as ex:
            for ii, row in ex.map(_compute_row, range(N_A)):
                gij[ii] = row

    return gij, rij
