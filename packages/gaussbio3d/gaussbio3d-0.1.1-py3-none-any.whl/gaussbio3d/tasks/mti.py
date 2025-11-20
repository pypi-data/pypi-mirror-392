"""
Molecule-Target Interaction (MTI) task helpers
分子-靶点交互(MTI)任务辅助工具

This module provides convenience functions to compute mGLI features
for protein-nucleic acid interaction tasks (e.g., protein-DNA/RNA binding).

本模块提供便捷函数来计算用于蛋白质-核酸交互任务的mGLI特征（例如，蛋白质-DNA/RNA结合）。
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from ..molecules.protein import Protein
from ..molecules.nucleic_acid import NucleicAcid
from ..config import MgliConfig
from ..features.descriptor import global_mgli_descriptor
from ..features.node_features import node_mgli_features
from ..features.pairwise import pairwise_mgli_matrix


def compute_mti_features(
    protein_pdb: str,
    na_pdb: str,
    protein_chain: Optional[str] = None,
    na_chain: Optional[str] = None,
    config: Optional[MgliConfig] = None,
) -> Dict[str, Any]:
    """
    Compute mGLI-based features for a Protein–Nucleic Acid (DNA/RNA) pair.
    计算蛋白质-核酸(DNA/RNA)对的基于mGLI的特征。

    This is suitable as a building block for MTI-like tasks
    (e.g. protein–DNA binding, etc.).
    
    这适合作为MTI类任务的构建块（例如蛋白质-DNA结合等）。

    Parameters / 参数
    ----------
    protein_pdb : str
        Path to protein PDB file / 蛋白质PDB文件路径
    na_pdb : str
        Path to nucleic acid PDB file / 核酸PDB文件路径
    protein_chain : str, optional
        Protein chain ID / 蛋白质链ID
    na_chain : str, optional
        Nucleic acid chain ID / 核酸链ID
    config : MgliConfig, optional
        mGLI configuration; if None, default is used
        mGLI配置；如果为None，则使用默认值

    Returns / 返回
    -------
    result : dict
        Dictionary containing:
        包含以下内容的字典：
        {
          "global_feat": np.ndarray,    # global descriptor / 全局描述符
          "prot_node_feat": np.ndarray, # node-level features for protein / 蛋白质的节点级特征
          "na_node_feat": np.ndarray,   # node-level features for nucleic acid / 核酸的节点级特征
          "pairwise_mgli": np.ndarray,  # pairwise GLI matrix / 成对GLI矩阵
        }
    """
    if config is None:
        config = MgliConfig()

    # Load protein and nucleic acid / 加载蛋白质和核酸
    prot = Protein.from_pdb(protein_pdb, chain_id=protein_chain)
    na = NucleicAcid.from_pdb(na_pdb, chain_id=na_chain)

    # Compute features / 计算特征
    global_feat = global_mgli_descriptor(prot, na, config)
    prot_node_feat = node_mgli_features(prot, na, config)
    na_node_feat = node_mgli_features(na, prot, config)
    pairwise_mat = pairwise_mgli_matrix(prot, na, signed=config.signed, agg="mean")

    return dict(
        global_feat=global_feat,
        prot_node_feat=prot_node_feat,
        na_node_feat=na_node_feat,
        pairwise_mgli=pairwise_mat,
    )
