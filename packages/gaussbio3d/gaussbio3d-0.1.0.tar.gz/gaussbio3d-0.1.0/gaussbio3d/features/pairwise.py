"""
Pairwise mGLI matrix computation
成对mGLI矩阵计算

This module computes pairwise node-level mGLI matrices between two structures,
useful for cross-attention mechanisms in deep learning models.

本模块计算两个结构之间的成对节点级mGLI矩阵，
对深度学习模型中的交叉注意力机制很有用。
"""

from __future__ import annotations

import numpy as np
from ..core.geometry import Structure
from ..core.gli import compute_pairwise_node_gli


def pairwise_mgli_matrix(
    struct_A: Structure,
    struct_B: Structure,
    signed: bool = False,
    agg: str = "mean",
) -> np.ndarray:
    """
    Compute pairwise node-level mGLI matrix between structure A and B.
    计算结构A和B之间的成对节点级mGLI矩阵。

    This is essentially the gij matrix from compute_pairwise_node_gli.
    这本质上就是compute_pairwise_node_gli的gij矩阵。

    Parameters / 参数
    ----------
    struct_A, struct_B : Structure
        Input structures / 输入结构
    signed : bool
        Whether to keep signed GLI / 是否保留有符号的GLI
    agg : str
        Aggregation over segments / 线段的聚合方式

    Returns / 返回
    -------
    M : np.ndarray
        (N_A, N_B) matrix of mGLI values.
        mGLI值的(N_A, N_B)矩阵
    """
    gij, _ = compute_pairwise_node_gli(
        struct_A, struct_B, signed=signed, agg=agg
    )
    return gij
