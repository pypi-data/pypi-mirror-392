"""
Segment-level J features: local / cross-scale / global statistics
线段级J特征：局部/跨尺度/全局统计

Computes GLI over segment pairs between two structures and aggregates
into multi-scale statistics. Designed to integrate with descriptor outputs.

在两个结构的线段对上计算GLI并聚合为多尺度统计，旨在与描述符集成。
"""

from __future__ import annotations

from typing import Dict, Any, List, Tuple
import numpy as np

from ..core.geometry import Structure, Segment
from ..core.gli_segment import gli_segment_batch_accel as gli_segment_batch
from ..config import MgliConfig


def _collect_segments(struct: Structure) -> Tuple[np.ndarray, np.ndarray, List[Segment]]:
    a0_list: List[np.ndarray] = []
    a1_list: List[np.ndarray] = []
    seg_list: List[Segment] = []
    for curve in struct.curves:
        for seg in curve.segments:
            a0_list.append(seg.start)
            a1_list.append(seg.end)
            seg_list.append(seg)
    if not a0_list:
        return np.zeros((0, 3)), np.zeros((0, 3)), []
    return np.stack(a0_list, axis=0), np.stack(a1_list, axis=0), seg_list


def _segment_midpoints(a0: np.ndarray, a1: np.ndarray) -> np.ndarray:
    return 0.5 * (a0 + a1)


def _hard_bin_weights(r: np.ndarray, edges: np.ndarray) -> np.ndarray:
    K = edges.size - 1
    W = np.zeros((K,) + r.shape, dtype=float)
    for k in range(K):
        mask = (r >= edges[k]) & (r < edges[k + 1])
        W[k][mask] = 1.0
    return W


def segment_j_features(
    struct_A: Structure,
    struct_B: Structure,
    config: MgliConfig,
    use_gpu: bool | None = None,
) -> Dict[str, Any]:
    """
    Compute multi-scale J features over segment pairs between A and B.
    在A与B的线段对上计算多尺度J特征。

    Returns
    -------
    dict with keys:
      - local_j: (N_A_nodes, K) per-node per-scale sums
      - cross_scale_corr: (K, K) correlation matrix over global scale sums
      - global_stats: (K, S) stats over all segment pairs per scale
    """
    if use_gpu is None:
        use_gpu = getattr(config, "use_gpu", False)

    # Collect segments
    A0, A1, segs_A = _collect_segments(struct_A)
    B0, B1, segs_B = _collect_segments(struct_B)
    M = A0.shape[0]
    N = B0.shape[0]
    if M == 0 or N == 0:
        return dict(
            local_j=np.zeros((len(struct_A.nodes), 0), dtype=float),
            cross_scale_corr=np.zeros((0, 0), dtype=float),
            global_stats=np.zeros((0, 0), dtype=float),
        )

    # Midpoint distances for pruning & binning
    cA = _segment_midpoints(A0, A1)  # (M,3)
    cB = _segment_midpoints(B0, B1)  # (N,3)
    d = np.linalg.norm(cA[:, None, :] - cB[None, :, :], axis=-1)  # (M,N)

    # Distance pruning
    maxd = getattr(config, "max_distance", None)
    if maxd is not None and maxd > 0:
        mask_pairs = d <= maxd
    else:
        mask_pairs = np.ones((M, N), dtype=bool)

    # Build weights per scale (hard bins or RBF)
    if getattr(config, "use_rbf", False):
        centers = np.asarray(config.distance_bins, dtype=float)
        K = centers.size
        sigma = float(getattr(config, "rbf_sigma", 1.0))
        r = d[None, :, :]
        c = centers[:, None, None]
        W = np.exp(-((r - c) ** 2) / (2.0 * sigma**2))  # (K,M,N)
    else:
        edges = np.asarray(config.distance_bins, dtype=float)
        K = edges.size - 1
        W = _hard_bin_weights(d, edges)  # (K,M,N)

    # Compute GLI over segment pairs using blocks to limit memory
    # For simplicity, loop over A segments and vectorize over B per segment
    # 并对每个A线段在B上矢量化
    per_scale_sums = np.zeros((K,), dtype=float)

    # Map per-node local contributions
    N_A_nodes = len(struct_A.nodes)
    local_j = np.zeros((N_A_nodes, K), dtype=float)

    # Pre-compute segment->node incidence list
    seg_incidence_A: List[Tuple[int, int]] = []
    for seg in segs_A:
        seg_incidence_A.append((getattr(seg, "start_node_id", -1), getattr(seg, "end_node_id", -1)))

    for i in range(M):
        # Build products for A[i] with all valid B[j]
        valid_j = np.where(mask_pairs[i])[0]
        if valid_j.size == 0:
            continue
        nj = valid_j.size
        A0_i = np.repeat(A0[i][None, :], nj, axis=0)
        A1_i = np.repeat(A1[i][None, :], nj, axis=0)
        B0_j = B0[valid_j]
        B1_j = B1[valid_j]

        vals = gli_segment_batch(A0_i, A1_i, B0_j, B1_j, signed=getattr(config, "signed", False))

        # Accumulate per scale using weights
        for k in range(K):
            wk = W[k, i, valid_j]
            if wk.size:
                s = float(np.sum(vals * wk))
                per_scale_sums[k] += s
                # Assign to incident nodes
                sni, eni = seg_incidence_A[i]
                if 0 <= sni < N_A_nodes:
                    local_j[sni, k] += s
                if 0 <= eni < N_A_nodes:
                    local_j[eni, k] += s

    # Cross-scale correlation over global sums
    if K > 0:
        v = per_scale_sums.reshape(1, -1)
        if np.all(v == 0.0):
            cross_corr = np.zeros((K, K), dtype=float)
        else:
            # normalize and compute corr matrix
            x = (v - v.mean())
            denom = np.sqrt((x * x).sum())
            x = x / (denom + 1e-12)
            cross_corr = (x.T @ x)
    else:
        cross_corr = np.zeros((0, 0), dtype=float)

    # Global stats per scale
    stats = getattr(config, "stats", ["sum", "mean"])  # reuse
    S = len(stats)
    # For each scale, we approximate stats over accumulated contributions
    global_stats = np.zeros((K, S), dtype=float)
    for k in range(K):
        # Construct per-pair values filtered by mask
        vals_k: List[float] = []
        for i in range(M):
            valid_j = np.where(mask_pairs[i])[0]
            if valid_j.size == 0:
                continue
            nj = valid_j.size
            A0_i = np.repeat(A0[i][None, :], nj, axis=0)
            A1_i = np.repeat(A1[i][None, :], nj, axis=0)
            B0_j = B0[valid_j]
            B1_j = B1[valid_j]
            vals_ij = gli_segment_batch(A0_i, A1_i, B0_j, B1_j, signed=getattr(config, "signed", False))
            wk = W[k, i, valid_j]
            vals_k.extend(list(vals_ij * wk))
        arr = np.asarray(vals_k, dtype=float)
        if arr.size == 0:
            continue
        for si, st in enumerate(stats):
            if st == "sum":
                global_stats[k, si] = float(arr.sum())
            elif st == "mean":
                global_stats[k, si] = float(arr.mean())
            elif st == "max":
                global_stats[k, si] = float(arr.max())
            elif st == "min":
                global_stats[k, si] = float(arr.min())
            elif st == "median":
                global_stats[k, si] = float(np.median(arr))
            else:
                global_stats[k, si] = float(arr.mean())

    return dict(
        local_j=local_j,
        cross_scale_corr=cross_corr,
        global_stats=global_stats,
    )


__all__ = ["segment_j_features"]

