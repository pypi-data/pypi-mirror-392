"""
Protein-Protein Interaction (PPI) task helpers
蛋白质-蛋白质交互(PPI)任务辅助工具

This module provides convenience functions to compute mGLI features
for protein-protein interaction prediction tasks.

本模块提供便捷函数来计算用于蛋白质-蛋白质交互预测任务的mGLI特征。
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from ..molecules.protein import Protein
from ..config import MgliConfig
from ..features.descriptor import global_mgli_descriptor
from ..features.node_features import node_mgli_features
from ..features.pairwise import pairwise_mgli_matrix


def compute_ppi_features(
    pdb_path_A: str,
    pdb_path_B: str,
    chain_id_A: Optional[str] = None,
    chain_id_B: Optional[str] = None,
    config: Optional[MgliConfig] = None,
) -> Dict[str, Any]:
    """
    Compute mGLI-based features for a Protein–Protein Interaction (PPI) pair.
    计算蛋白质-蛋白质交互(PPI)对的基于mGLI的特征。
    
    Parameters / 参数
    ----------
    pdb_path_A : str
        Path to first protein PDB file / 第一个蛋白质PDB文件路径
    pdb_path_B : str
        Path to second protein PDB file / 第二个蛋白质PDB文件路径
    chain_id_A : str, optional
        Chain ID for first protein / 第一个蛋白质的链ID
    chain_id_B : str, optional
        Chain ID for second protein / 第二个蛋白质的链ID
    config : MgliConfig, optional
        mGLI configuration; if None, default is used
        mGLI配置；如果为None，则使用默认值

    Returns / 返回
    -------
    result : dict
        Dictionary containing:
        包含以下内容的字典：
        {
          "global_feat": np.ndarray,   # global descriptor / 全局描述符
          "A_node_feat": np.ndarray,   # node-level features for protein A / 蛋白质A的节点级特征
          "B_node_feat": np.ndarray,   # node-level features for protein B / 蛋白质B的节点级特征
          "pairwise_mgli": np.ndarray, # pairwise GLI matrix / 成对GLI矩阵
        }
    """
    if config is None:
        config = MgliConfig()

    # Load proteins / 加载蛋白质
    prot_A = Protein.from_pdb(pdb_path_A, chain_id=chain_id_A)
    prot_B = Protein.from_pdb(pdb_path_B, chain_id=chain_id_B)

    # Compute features / 计算特征
    global_feat = global_mgli_descriptor(prot_A, prot_B, config)
    A_node_feat = node_mgli_features(prot_A, prot_B, config)
    B_node_feat = node_mgli_features(prot_B, prot_A, config)
    pairwise_mat = pairwise_mgli_matrix(prot_A, prot_B, signed=config.signed, agg="mean")

    return dict(
        global_feat=global_feat,
        A_node_feat=A_node_feat,
        B_node_feat=B_node_feat,
        pairwise_mgli=pairwise_mat,
    )
