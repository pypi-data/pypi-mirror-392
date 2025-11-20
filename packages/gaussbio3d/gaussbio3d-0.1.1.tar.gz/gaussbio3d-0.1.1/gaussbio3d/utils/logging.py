"""
Logging and progress utilities
日志与进度工具
"""

from __future__ import annotations

import logging
from typing import Iterable, Iterator, Optional


def get_logger(name: str = "gaussbio3d", level: int = logging.INFO) -> logging.Logger:
    """
    Create and configure a logger.
    创建并配置一个logger。
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def progress_for(
    iterable: Iterable,
    desc: str = "",
    enable: bool = True,
) -> Iterator:
    """
    Wrap an iterable with a tqdm progress bar when enabled.
    当启用时，用tqdm进度条包装一个可迭代对象。
    """
    if not enable:
        for x in iterable:
            yield x
        return
    try:
        from tqdm import tqdm  # type: ignore
        for x in tqdm(iterable, desc=desc):
            yield x
    except Exception:
        for x in iterable:
            yield x