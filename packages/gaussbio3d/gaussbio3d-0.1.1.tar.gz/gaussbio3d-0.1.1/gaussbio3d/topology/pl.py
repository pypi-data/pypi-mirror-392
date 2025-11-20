"""
Persistent Laplacians (PL) utilities
持久拉普拉斯(PL)工具

This module defines interface shims that rely on external TDA libraries
to compute Hodge Laplacian spectra. If unavailable, an ImportError is raised.

本模块定义依赖外部TDA库计算Hodge拉普拉斯谱的接口；若不可用则抛异常。
"""

from __future__ import annotations

import numpy as np


def pl_hodge_spectrum(rij: np.ndarray, k: int = 10) -> np.ndarray:
    """
    Placeholder interface for Hodge Laplacian spectrum based on Vietoris-Rips.
    基于Vietoris-Rips的Hodge拉普拉斯谱接口占位。

    Requires giotto-tda or gudhi; raises ImportError if not installed.
    需要giotto-tda或gudhi；未安装则抛出ImportError。
    """
    raise ImportError("PL requires giotto-tda/gudhi; please install giotto-tda or gudhi")


__all__ = ["pl_hodge_spectrum"]

