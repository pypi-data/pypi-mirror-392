"""
Gauss Linking Integral (GLI) computation (compat exports)
高斯链接积分(GLI)计算（兼容导出）

This module now re-exports segment-level and pairwise functions from
`gli_segment.py` and `pairwise_gli.py` after refactoring.

本模块在重构后从 `gli_segment.py` 与 `pairwise_gli.py` 重新导出线段级与成对函数。
"""

from __future__ import annotations

import numpy as np
from typing import Tuple
from .geometry import Segment, Curve, Structure
from .gli_segment import gli_segment
from .pairwise_gli import compute_pairwise_node_gli


def gli_curves(curve1: Curve, curve2: Curve, signed: bool = False) -> float:
    """
    Compute total GLI between two polylines by summing segment-level GLIs.
    通过对线段级GLI求和来计算两条折线之间的总GLI。
    
    Parameters / 参数
    ----------
    curve1, curve2 : Curve
        Input curves / 输入曲线
    signed : bool
        Whether to keep signed GLI / 是否保留有符号的GLI
        
    Returns / 返回
    -------
    float
        Total GLI between the two curves / 两条曲线之间的总GLI
    """
    total = 0.0
    for s1 in curve1.segments:
        for s2 in curve2.segments:
            total += gli_segment(s1, s2, signed=signed)
    return total
