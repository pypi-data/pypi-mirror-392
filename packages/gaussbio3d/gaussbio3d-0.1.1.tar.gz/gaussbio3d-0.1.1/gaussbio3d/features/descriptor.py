"""
Global mGLI descriptor computation
全局mGLI描述符计算

This module computes multi-scale, grouped topological descriptors
based on Gauss linking integrals between two biomolecular structures.

本模块基于两个生物分子结构之间的高斯链接积分计算多尺度、分组的拓扑描述符。
"""

from __future__ import annotations

from typing import Dict, Tuple, List
import numpy as np

from ..core.geometry import Structure, Node
from ..core.pairwise_gli import compute_pairwise_node_gli
from ..config import MgliConfig


def _get_group_key(node: Node, mode: str) -> str:
    """
    Get group key for a node based on grouping mode.
    根据分组模式获取节点的组键。
    
    Parameters / 参数
    ----------
    node : Node
        The node / 节点
    mode : str
        Grouping mode: "element" or "group"
        分组模式："element"（元素）或"group"（组）
        
    Returns / 返回
    -------
    str
        Group key / 组键
    """
    if mode == "element":
        return node.element
    elif mode == "group":
        return node.group or node.element
    else:
        return node.group or node.element


def _build_group_indices(
    structure: Structure,
    mode: str,
) -> Tuple[Dict[str, int], np.ndarray]:
    """
    Build mapping from group key -> index, and an array of group index per node.
    构建从组键到索引的映射，以及每个节点的组索引数组。

    Parameters / 参数
    ----------
    structure : Structure
        Input structure / 输入结构
    mode : str
        Grouping mode / 分组模式

    Returns / 返回
    -------
    group_to_idx : dict
        Mapping from group key to index / 从组键到索引的映射
    node_group_idx : np.ndarray
        Array of group indices per node / 每个节点的组索引数组
    """
    keys: List[str] = []
    for n in structure.nodes:
        k = _get_group_key(n, mode)
        if k not in keys:
            keys.append(k)
    group_to_idx = {k: i for i, k in enumerate(keys)}
    node_group_idx = np.zeros(len(structure.nodes), dtype=int)
    for i, n in enumerate(structure.nodes):
        node_group_idx[i] = group_to_idx[_get_group_key(n, mode)]
    return group_to_idx, node_group_idx


def _compute_radial_weights(
    rij: np.ndarray,
    config: MgliConfig,
) -> np.ndarray:
    """
    Compute radial weights Φ_k(r_ij) for all i,j and k.
    计算所有i,j和k的径向权重Φ_k(r_ij)。

    Parameters / 参数
    ----------
    rij : np.ndarray
        Distance matrix, shape (N_A, N_B) / 距离矩阵，形状为(N_A, N_B)
    config : MgliConfig
        Configuration / 配置

    Returns / 返回
    -------
    weights : np.ndarray
        Radial weight tensor, shape (K, N_A, N_B)
        径向权重张量，形状为(K, N_A, N_B)
    """
    if config.use_rbf:
        # RBF mode / RBF模式
        centers = np.asarray(config.distance_bins, dtype=float)
        K = centers.shape[0]
        if config.rbf_sigma is None:
            # heuristic sigma = mean gap or 1.0 / 启发式sigma = 平均间隔或1.0
            diffs = np.diff(np.sort(centers))
            sigma = float(diffs.mean() if diffs.size > 0 else 1.0)
        else:
            sigma = float(config.rbf_sigma)
        r = rij[None, :, :]  # (1,N_A,N_B)
        c = centers[:, None, None]  # (K,1,1)
        weights = np.exp(-((r - c) ** 2) / (2.0 * sigma**2))
        return weights
    else:
        # Hard bins mode / 硬分箱模式
        # distance_bins are edges [R0,...,RK] / distance_bins是边界[R0,...,RK]
        edges = np.asarray(config.distance_bins, dtype=float)
        assert edges.ndim == 1 and edges.size >= 2
        K = edges.size - 1
        weights = np.zeros((K,) + rij.shape, dtype=float)
        for k in range(K):
            mask = (rij >= edges[k]) & (rij < edges[k + 1])
            weights[k][mask] = 1.0
        return weights


def global_mgli_descriptor(
    struct_A: Structure,
    struct_B: Structure | None,
    config: MgliConfig,
) -> np.ndarray:
    """
    Compute a global multiscale mGLI descriptor between two structures (or self).
    计算两个结构（或自身）之间的全局多尺度mGLI描述符。

    If struct_B is None, we compute self-mGLI of struct_A.
    如果struct_B为None，则计算struct_A的自mGLI。

    Output is a flat vector over:
      - group_A × group_B × radial scale × statistics
      
    输出是一个扁平向量，包含：
      - 组A × 组B × 径向尺度 × 统计量

    Parameters / 参数
    ----------
    struct_A, struct_B : Structure
        Input structures. If struct_B is None, B=A.
        输入结构。如果struct_B为None，则B=A。
    config : MgliConfig
        Configuration for bins / RBF / grouping modes / stats.
        分箱/RBF/分组模式/统计量的配置

    Returns / 返回
    -------
    feat : np.ndarray
        1D feature vector / 1D特征向量
    """
    if struct_B is None:
        struct_B = struct_A

    # Compute pairwise node GLI and distances / 计算成对节点GLI和距离
    gij, rij = compute_pairwise_node_gli(
        struct_A,
        struct_B,
        signed=config.signed,
        agg="mean",
        max_distance=getattr(config, "max_distance", None),
        n_jobs=getattr(config, "n_jobs", 1),
        use_gpu=getattr(config, "use_gpu", False),
    )  # (N_A, N_B), (N_A,N_B)

    # Build group indices / 构建组索引
    group_to_idx_A, node_group_A = _build_group_indices(struct_A, config.group_mode_A)
    group_to_idx_B, node_group_B = _build_group_indices(struct_B, config.group_mode_B)

    G_A = len(group_to_idx_A)
    G_B = len(group_to_idx_B)

    # Compute radial weights / 计算径向权重
    weights = _compute_radial_weights(rij, config)  # (K,N_A,N_B)
    K = weights.shape[0]

    stats = config.stats
    S = len(stats)

    # Initialize feature tensor / 初始化特征张量
    # feat[ga, gb, k, s]
    feat = np.zeros((G_A, G_B, K, S), dtype=float)

    # For each group pair and scale, gather values
    # 对于每个组对和尺度，收集值
    for ga in range(G_A):
        mask_A = node_group_A == ga
        if not mask_A.any():
            continue
        for gb in range(G_B):
            mask_B = node_group_B == gb
            if not mask_B.any():
                continue
            # Extract submatrices / 提取子矩阵
            sub_g = gij[mask_A][:, mask_B]          # (nA, nB)
            sub_r = rij[mask_A][:, mask_B]          # (nA, nB)
            if sub_g.size == 0:
                continue
            for k in range(K):
                w = weights[k][mask_A][:, mask_B]   # (nA,nB)
                mask = w > 0.0
                if not mask.any():
                    continue
                vals = (sub_g * w)[mask]
                if vals.size == 0:
                    continue
                # Compute statistics / 计算统计量
                for si, st in enumerate(stats):
                    if st == "sum":
                        feat[ga, gb, k, si] = float(vals.sum())
                    elif st == "mean":
                        feat[ga, gb, k, si] = float(vals.mean())
                    elif st == "max":
                        feat[ga, gb, k, si] = float(vals.max())
                    elif st == "min":
                        feat[ga, gb, k, si] = float(vals.min())
                    elif st == "median":
                        feat[ga, gb, k, si] = float(np.median(vals))
                    else:
                        feat[ga, gb, k, si] = float(vals.mean())

    return feat.reshape(-1)
