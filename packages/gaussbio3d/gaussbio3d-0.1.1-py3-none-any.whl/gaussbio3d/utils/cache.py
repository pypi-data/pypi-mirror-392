"""
Persistent cache manager and unified naming helpers
持久化缓存管理与统一命名助手

Provides a simple filesystem-backed cache for storing intermediate
arrays (e.g., node/segment endpoints, distance matrices), and a
unified naming scheme "物质名_方法_维度.npy".

提供用于存储中间数组的简单文件系统缓存，以及统一的输出命名方案。
"""

from __future__ import annotations

import os
import hashlib
import numpy as np
from typing import Optional


def format_name(base: str, method: str, dim: str) -> str:
    """Return unified filename like "base_method_dim.npy"."""
    base = os.path.basename(base)
    base = os.path.splitext(base)[0]
    return f"{base}_{method}_{dim}.npy"


class CacheManager:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _key_path(self, key: str) -> str:
        # Map arbitrary key to a stable file path via hash
        h = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        return os.path.join(self.base_dir, f"{h}.npy")

    def exists(self, key: str) -> bool:
        return os.path.exists(self._key_path(key))

    def load(self, key: str) -> Optional[np.ndarray]:
        path = self._key_path(key)
        if os.path.exists(path):
            try:
                return np.load(path, allow_pickle=False)
            except Exception:
                return None
        return None

    def save(self, key: str, arr: np.ndarray) -> str:
        path = self._key_path(key)
        np.save(path, arr)
        return path

    def save_named(self, base: str, method: str, dim: str, arr: np.ndarray) -> str:
        filename = format_name(base, method, dim)
        path = os.path.join(self.base_dir, filename)
        np.save(path, arr)
        return path


__all__ = ["CacheManager", "format_name"]

