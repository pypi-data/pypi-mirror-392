"""
GaussBio3D: Multiscale Gauss Linking Integral Library
GaussBio3D: 多尺度高斯链接积分库

High-level exports / 高层导出
"""

from .config import MgliConfig
from .core.geometry import Node, Segment, Curve, Structure
from .core.gli import gli_segment, gli_curves
from .features.descriptor import global_mgli_descriptor
from .features.node_features import node_mgli_features
from .features.pairwise import pairwise_mgli_matrix

__version__ = "0.1.1"

__all__ = [
    "MgliConfig",
    "Node",
    "Segment",
    "Curve",
    "Structure",
    "gli_segment",
    "gli_curves",
    "global_mgli_descriptor",
    "node_mgli_features",
    "pairwise_mgli_matrix",
]
