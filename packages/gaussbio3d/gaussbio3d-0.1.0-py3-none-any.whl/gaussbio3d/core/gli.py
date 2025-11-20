"""
Gauss Linking Integral (GLI) computation module
高斯链接积分(GLI)计算模块

This module implements discrete approximation of the Gauss linking integral
between line segments and curves using spherical geometry.

本模块使用球面几何实现线段和曲线之间的高斯链接积分的离散近似。
"""

from __future__ import annotations

import numpy as np
from typing import List, Tuple
from .geometry import Segment, Curve, Structure


def _safe_norm(v: np.ndarray, eps: float = 1e-12) -> float:
    """
    Safe norm computation with epsilon to avoid division by zero.
    安全的范数计算，带有epsilon以避免除零。
    
    Parameters / 参数
    ----------
    v : np.ndarray
        Input vector / 输入向量
    eps : float
        Small epsilon value / 小的epsilon值
        
    Returns / 返回
    -------
    float
        Norm of the vector / 向量的范数
    """
    return float(np.linalg.norm(v) + eps)


def gli_segment(seg1: Segment, seg2: Segment, signed: bool = False) -> float:
    """
    Compute a Gauss-linking-like quantity between two line segments.
    计算两个线段之间的类高斯链接量。

    This is a discrete approximation of the continuous Gauss linking integral
    based on spherical geometry (as in your existing scripts).
    
    这是基于球面几何的连续高斯链接积分的离散近似（如您现有的脚本）。

    Parameters / 参数
    ----------
    seg1, seg2 : Segment
        Input segments / 输入线段
    signed : bool
        If False, return |GLI| (link strength). If True, keep sign (chirality).
        如果为False，返回|GLI|（链接强度）。如果为True，保留符号（手性）。

    Returns / 返回
    -------
    float
        Approximate GLI between the two segments.
        两个线段之间的近似GLI
    """
    a0 = seg1.start
    a1 = seg1.end
    b0 = seg2.start
    b1 = seg2.end

    # Compute relative position vectors / 计算相对位置向量
    r00 = b0 - a0
    r01 = b1 - a0
    r10 = b0 - a1
    r11 = b1 - a1

    # Normalize with safety / 安全归一化
    def unit(v: np.ndarray) -> np.ndarray:
        """Normalize vector to unit length / 将向量归一化为单位长度"""
        n = np.linalg.norm(v)
        if n < 1e-12:
            return np.zeros_like(v)
        return v / n

    u00 = unit(r00)
    u01 = unit(r01)
    u10 = unit(r10)
    u11 = unit(r11)

    # Cross products of edges of the spherical quadrilateral
    # 球面四边形边的叉积
    n0 = unit(np.cross(u00, u01))
    n1 = unit(np.cross(u01, u11))
    n2 = unit(np.cross(u11, u10))
    n3 = unit(np.cross(u10, u00))

    def arc_sin_clamp(x: float) -> float:
        """Clamp and compute arcsin / 截断并计算arcsin"""
        return float(np.arcsin(max(-1.0, min(1.0, x))))

    # Sum signed spherical areas / 求和有向球面面积
    area = 0.0
    area += arc_sin_clamp(np.dot(n0, n1))
    area += arc_sin_clamp(np.dot(n1, n2))
    area += arc_sin_clamp(np.dot(n2, n3))
    area += arc_sin_clamp(np.dot(n3, n0))

    # Orientation sign / 方向符号
    sign = 1.0
    if signed:
        t1 = a1 - a0
        t2 = b1 - b0
        triple = np.dot(np.cross(t1, t2), r00)
        sign = np.sign(triple) if abs(triple) > 1e-12 else 1.0

    gli = sign * area / (4.0 * np.pi)
    return abs(gli) if not signed else gli


def gli_curves(curve1: Curve, curve2: Curve, signed: bool = False) -> float:
    """
    Compute total GLI between two polylines by summing segment-level GLIs.
    通过对线段级GLI求和来计算两条折线之间的总GLI。
    
    Parameters / 参数
    ----------
    curve1, curve2 : Curve
        Input curves / 输入曲线
    signed : bool
        Whether to keep signed GLI / 是否保留有符号的GLI
        
    Returns / 返回
    -------
    float
        Total GLI between the two curves / 两条曲线之间的总GLI
    """
    total = 0.0
    for s1 in curve1.segments:
        for s2 in curve2.segments:
            total += gli_segment(s1, s2, signed=signed)
    return total


def compute_pairwise_node_gli(
    struct_A: Structure,
    struct_B: Structure,
    signed: bool = False,
    agg: str = "mean",
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute pairwise node-level GLI and distances between two structures.
    计算两个结构之间的成对节点级GLI和距离。

    For each node i in A and node j in B, aggregate GLIs between all segments
    touching node i and all segments touching node j.
    
    对于A中的每个节点i和B中的每个节点j，聚合接触节点i的所有线段
    和接触节点j的所有线段之间的GLI。

    Parameters / 参数
    ----------
    struct_A, struct_B : Structure
        Input structures / 输入结构
    signed : bool
        Whether GLI is signed / GLI是否有符号
    agg : str
        Aggregation over segment pairs: "mean" or "median" or "sum".
        线段对的聚合方式："mean"（均值）、"median"（中位数）或"sum"（求和）

    Returns / 返回
    -------
    gij : np.ndarray
        (N_A, N_B) matrix of local GLI values (aggregated).
        局部GLI值的(N_A, N_B)矩阵（聚合后）
    rij : np.ndarray
        (N_A, N_B) matrix of Euclidean distances between node coordinates.
        节点坐标之间欧氏距离的(N_A, N_B)矩阵
    """
    coords_A = struct_A.coords  # (N_A,3)
    coords_B = struct_B.coords  # (N_B,3)
    N_A = coords_A.shape[0]
    N_B = coords_B.shape[0]

    if N_A == 0 or N_B == 0:
        return np.zeros((N_A, N_B)), np.zeros((N_A, N_B))

    # Compute pairwise distances / 计算成对距离
    rij = np.linalg.norm(
        coords_A[:, None, :] - coords_B[None, :, :], axis=-1
    )  # (N_A, N_B)

    gij = np.zeros((N_A, N_B), dtype=float)

    # Compute GLI for each node pair / 计算每个节点对的GLI
    for i in range(N_A):
        segs_i = struct_A.node_segments.get(i, [])
        if not segs_i:
            continue
        for j in range(N_B):
            segs_j = struct_B.node_segments.get(j, [])
            if not segs_j:
                continue
            vals = []
            for s1 in segs_i:
                for s2 in segs_j:
                    vals.append(gli_segment(s1, s2, signed=signed))
            if not vals:
                continue
            vals = np.asarray(vals, dtype=float)
            # Aggregate according to the specified method / 根据指定方法聚合
            if agg == "mean":
                gij[i, j] = float(vals.mean())
            elif agg == "median":
                gij[i, j] = float(np.median(vals))
            elif agg == "sum":
                gij[i, j] = float(vals.sum())
            else:
                gij[i, j] = float(vals.mean())

    return gij, rij
