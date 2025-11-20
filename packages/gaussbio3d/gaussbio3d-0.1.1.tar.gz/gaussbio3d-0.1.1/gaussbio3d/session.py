"""
Session and caching helpers
会话与缓存辅助

Provide a Session bound to a protein to reuse caches when computing
features across multiple ligands.

提供绑定到蛋白质的Session，以在对多个配体计算特征时复用缓存。
"""

from __future__ import annotations

from typing import Dict, Any

from .molecules.protein import Protein
from .molecules.ligand import Ligand
from .config import MgliConfig
from .features.descriptor import global_mgli_descriptor
from .features.node_features import node_mgli_features
from .features.pairwise import pairwise_mgli_matrix


class Session:
    def __init__(self, protein: Protein, config: MgliConfig, use_gpu: bool = False):
        self.protein = protein
        self.config = config
        self.use_gpu = use_gpu
        self._cache: Dict[str, Any] = {}
        # Placeholders for future caches (coords, segment endpoints, etc.)
        # 未来缓存的占位（坐标、线段端点等）

    def compute_features_for_ligand(self, ligand: Ligand) -> Dict[str, Any]:
        """
        Compute features for a given ligand, reusing protein context.
        在复用蛋白质上下文的情况下为给定配体计算特征。
        """
        key = ligand.metadata.get("source", f"ligand:{len(ligand.nodes)}")
        pw_key = f"pairwise_mgli::{key}"
        pairwise_mat = self._cache.get(pw_key)
        if pairwise_mat is None:
            pairwise_mat = pairwise_mgli_matrix(
                self.protein,
                ligand,
                signed=self.config.signed,
                agg="mean",
                max_distance=getattr(self.config, "max_distance", None),
                n_jobs=getattr(self.config, "n_jobs", 1),
                use_gpu=getattr(self.config, "use_gpu", False),
            )
            self._cache[pw_key] = pairwise_mat

        global_feat = global_mgli_descriptor(self.protein, ligand, self.config)
        prot_node_feat = node_mgli_features(self.protein, ligand, self.config)
        lig_node_feat = node_mgli_features(ligand, self.protein, self.config)
        return dict(
            global_feat=global_feat,
            prot_node_feat=prot_node_feat,
            lig_node_feat=lig_node_feat,
            pairwise_mgli=pairwise_mat,
        )
