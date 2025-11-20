"""
Node-level mGLI feature extraction
节点级mGLI特征提取

This module computes mGLI-based feature vectors for individual nodes
in a structure with respect to another structure.

本模块计算结构中单个节点相对于另一个结构的基于mGLI的特征向量。
"""

from __future__ import annotations

import numpy as np
from ..core.geometry import Structure
from ..core.gli import compute_pairwise_node_gli
from ..config import MgliConfig
from .descriptor import _compute_radial_weights


def node_mgli_features(
    struct_A: Structure,
    struct_B: Structure,
    config: MgliConfig,
) -> np.ndarray:
    """
    Compute node-level mGLI feature vectors for structure A
    with respect to structure B.
    
    计算结构A相对于结构B的节点级mGLI特征向量。

    For each node i in A, aggregate GLI contributions across:
      - all nodes j in B
      - radial bins / RBF centers
      
    对于A中的每个节点i，在以下维度聚合GLI贡献：
      - B中的所有节点j
      - 径向分箱/RBF中心

    Output shape: (N_A, K * S)
    输出形状：(N_A, K * S)

    Where:
      - K is number of radial scales
      - S is number of stats in config.stats
      
    其中：
      - K是径向尺度的数量
      - S是config.stats中统计量的数量

    Parameters / 参数
    ----------
    struct_A, struct_B : Structure
        Input structures (e.g. Protein and Ligand).
        输入结构（例如蛋白质和配体）
    config : MgliConfig
        Configuration / 配置

    Returns / 返回
    -------
    features : np.ndarray
        Node-level feature matrix for A, shape (N_A, feat_dim).
        A的节点级特征矩阵，形状为(N_A, feat_dim)
    """
    # Compute pairwise GLI and distances / 计算成对GLI和距离
    gij, rij = compute_pairwise_node_gli(
        struct_A, struct_B, signed=config.signed, agg="mean"
    )  # (N_A,N_B), (N_A,N_B)
    
    # Compute radial weights / 计算径向权重
    weights = _compute_radial_weights(rij, config)  # (K,N_A,N_B)
    K = weights.shape[0]
    stats = config.stats
    S = len(stats)

    N_A = gij.shape[0]
    if N_A == 0:
        return np.zeros((0, K * S), dtype=float)

    # Initialize result tensor / 初始化结果张量
    # result: (N_A, K, S)
    feat = np.zeros((N_A, K, S), dtype=float)

    # For each node in A / 对于A中的每个节点
    for i in range(N_A):
        g_row = gij[i]  # (N_B,)
        if not np.any(g_row):
            continue
        # For each radial scale / 对于每个径向尺度
        for k in range(K):
            w_row = weights[k, i]  # (N_B,)
            mask = w_row > 0.0
            if not mask.any():
                continue
            vals = (g_row * w_row)[mask]
            if vals.size == 0:
                continue
            # Compute statistics / 计算统计量
            for si, st in enumerate(stats):
                if st == "sum":
                    feat[i, k, si] = float(vals.sum())
                elif st == "mean":
                    feat[i, k, si] = float(vals.mean())
                elif st == "max":
                    feat[i, k, si] = float(vals.max())
                elif st == "min":
                    feat[i, k, si] = float(vals.min())
                elif st == "median":
                    feat[i, k, si] = float(np.median(vals))
                else:
                    feat[i, k, si] = float(vals.mean())

    # Flatten to (N_A, K*S) / 展平为(N_A, K*S)
    return feat.reshape(N_A, -1)
