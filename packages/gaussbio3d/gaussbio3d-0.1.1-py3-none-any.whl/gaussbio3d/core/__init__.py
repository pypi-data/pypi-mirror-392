"""
Core module for geometry and GLI computation
几何和GLI计算的核心模块

Exports commonly used primitives and GLI functions.
导出常用的几何基元与GLI函数。
"""

from .geometry import Node, Segment, Curve, Structure
from .gli_segment import gli_segment, gli_segment_batch, gli_segment_batch_accel
from .pairwise_gli import compute_pairwise_node_gli

__all__ = [
    "Node",
    "Segment",
    "Curve",
    "Structure",
    "gli_segment",
    "gli_segment_batch",
    "gli_segment_batch_accel",
    "compute_pairwise_node_gli",
]
