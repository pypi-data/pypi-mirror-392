"""
Drug-Target Interaction (DTI) task helpers
药物-靶点交互(DTI)任务辅助工具

This module provides convenience functions to compute mGLI features
for drug-target interaction prediction tasks.

本模块提供便捷函数来计算用于药物-靶点交互预测任务的mGLI特征。
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from ..molecules.protein import Protein
from ..molecules.ligand import Ligand
from ..config import MgliConfig
from ..features.descriptor import global_mgli_descriptor
from ..features.node_features import node_mgli_features
from ..features.pairwise import pairwise_mgli_matrix


def compute_dti_features(
    pdb_path: str,
    sdf_path: Optional[str] = None,
    smiles: Optional[str] = None,
    chain_id: Optional[str] = None,
    config: Optional[MgliConfig] = None,
) -> Dict[str, Any]:
    """
    Convenience function to compute mGLI-based features for a single DTI pair.
    计算单个DTI对的基于mGLI的特征的便捷函数。

    Parameters / 参数
    ----------
    pdb_path : str
        Protein PDB path / 蛋白质PDB路径
    sdf_path : str, optional
        Ligand SDF path (if provided) / 配体SDF路径（如果提供）
    smiles : str, optional
        Ligand SMILES string (used if sdf_path is None)
        配体SMILES字符串（如果sdf_path为None则使用）
    chain_id : str, optional
        Protein chain ID to use / 要使用的蛋白质链ID
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
          "prot_node_feat": np.ndarray,# node-level features for protein / 蛋白质的节点级特征
          "lig_node_feat": np.ndarray, # node-level features for ligand / 配体的节点级特征
          "pairwise_mgli": np.ndarray, # pairwise GLI matrix / 成对GLI矩阵
        }
    """
    if config is None:
        config = MgliConfig()

    # Load protein and ligand / 加载蛋白质和配体
    prot = Protein.from_pdb(pdb_path, chain_id=chain_id)
    if sdf_path is not None:
        lig = Ligand.from_sdf(sdf_path)
    elif smiles is not None:
        lig = Ligand.from_smiles(smiles)
    else:
        raise ValueError("Either sdf_path or smiles must be provided.")

    # Compute features / 计算特征
    global_feat = global_mgli_descriptor(prot, lig, config)
    prot_node_feat = node_mgli_features(prot, lig, config)
    lig_node_feat = node_mgli_features(lig, prot, config)
    pairwise_mat = pairwise_mgli_matrix(prot, lig, signed=config.signed, agg="mean")

    return dict(
        global_feat=global_feat,
        prot_node_feat=prot_node_feat,
        lig_node_feat=lig_node_feat,
        pairwise_mgli=pairwise_mat,
    )
