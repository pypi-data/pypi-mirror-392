"""
Topology feature interfaces (PH/PL/PTHL) and concatenation with mGLI
拓扑特征接口(PH/PL/PTHL)与mGLI拼接

Provides vectorized topology feature extraction using distance matrices
and glues them with mGLI descriptors.

使用距离矩阵进行拓扑特征提取，并与mGLI描述符拼接。
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Any

from ..core.geometry import Structure
from ..core.pairwise_gli import compute_pairwise_node_gli
from ..config import MgliConfig
from ..topology.ph import ph_diagrams_from_distance, ph_persistence_histogram
from .descriptor import global_mgli_descriptor


def topo_features_for_pair(
    struct_A: Structure,
    struct_B: Structure | None,
    config: MgliConfig,
    concat_with_mgli: bool = True,
) -> Dict[str, Any]:
    """
    Compute topology features (PH histograms) and optionally concatenate with mGLI.
    计算拓扑特征（PH直方图），并可选与mGLI拼接。
    """
    if struct_B is None:
        struct_B = struct_A

    # distances only are sufficient for PH
    _, rij = compute_pairwise_node_gli(
        struct_A,
        struct_B,
        signed=False,
        agg="mean",
        max_distance=getattr(config, "max_distance", None),
        n_jobs=getattr(config, "n_jobs", 1),
        use_gpu=False,
    )

    dgms = ph_diagrams_from_distance(rij, maxdim=2)
    ph_hist = ph_persistence_histogram(dgms)

    result: Dict[str, Any] = {"ph_hist": ph_hist}

    if concat_with_mgli:
        mgli = global_mgli_descriptor(struct_A, struct_B, config)
        result["concat"] = np.concatenate([mgli.reshape(-1), ph_hist.reshape(-1)])

    return result


__all__ = ["topo_features_for_pair"]

