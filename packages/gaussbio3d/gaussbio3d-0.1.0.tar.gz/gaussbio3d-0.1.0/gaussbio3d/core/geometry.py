"""
Geometric primitives for biomolecular structure representation
生物分子结构表示的几何基元

This module defines the core geometric abstractions:
本模块定义核心几何抽象：
- Node: atom / residue / base / 节点：原子/残基/碱基
- Segment: oriented line segment / 线段：有向线段
- Curve: polyline made of segments / 曲线：由线段组成的折线
- Structure: collection of nodes and curves / 结构：节点和曲线的集合
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import numpy as np


@dataclass
class Node:
    """
    A generic node in a biomolecular structure.
    生物分子结构中的通用节点。

    Can represent an atom, residue, or base, depending on usage.
    可以表示原子、残基或碱基，取决于使用场景。

    Attributes / 属性
    ----------
    id : int
        Unique integer ID (0..N-1).
        唯一整数ID (0..N-1)
        
    coord : np.ndarray
        3D coordinate, shape (3,).
        3D坐标，形状为(3,)
        
    element : str
        Chemical element symbol (C, N, O, S, P, ...).
        化学元素符号 (C, N, O, S, P, ...)
        
    group : str
        Higher-level group label (e.g. residue class, base type, functional group).
        更高层次的组标签（如残基类别、碱基类型、官能团）
        
    metadata : dict
        Arbitrary extra information (residue name, chain ID, etc.).
        任意额外信息（残基名称、链ID等）
    """

    id: int
    coord: np.ndarray
    element: str
    group: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Segment:
    """
    A directed 3D line segment.
    有向3D线段。

    Attributes / 属性
    ----------
    start : np.ndarray
        Start coordinate (3,).
        起始坐标 (3,)
        
    end : np.ndarray
        End coordinate (3,).
        终止坐标 (3,)
        
    start_node_id : Optional[int]
        ID of the node at or near the start (if any).
        起始处或附近节点的ID（如果有）
        
    end_node_id : Optional[int]
        ID of the node at or near the end (if any).
        终止处或附近节点的ID（如果有）
        
    start_type : str
        Type label for start (e.g. element).
        起始类型标签（如元素）
        
    end_type : str
        Type label for end (e.g. element).
        终止类型标签（如元素）
    """

    start: np.ndarray
    end: np.ndarray
    start_node_id: Optional[int] = None
    end_node_id: Optional[int] = None
    start_type: str = ""
    end_type: str = ""


@dataclass
class Curve:
    """
    A polyline curve composed of segments.
    由线段组成的折线曲线。

    Attributes / 属性
    ----------
    segments : List[Segment]
        The segments forming this curve.
        构成此曲线的线段
        
    curve_type : str
        E.g. "backbone", "sidechain", "ring".
        例如 "backbone"（主链）、"sidechain"（侧链）、"ring"（环）
        
    metadata : dict
        Additional info (chain id, residue ids involved, etc.).
        附加信息（链ID、涉及的残基ID等）
    """

    segments: List[Segment]
    curve_type: str = "generic"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Structure:
    """
    A biomolecular structure represented by nodes and curves.
    由节点和曲线表示的生物分子结构。

    Attributes / 属性
    ----------
    nodes : List[Node]
        Node list.
        节点列表
        
    curves : List[Curve]
        Curves describing geometry (backbone, sidechains, rings, etc.).
        描述几何的曲线（主链、侧链、环等）
        
    node_segments : Dict[int, List[Segment]]
        Mapping from node id to the list of segments incident to that node.
        Used to compute local GLI per node pair.
        
        从节点ID到该节点关联的线段列表的映射。
        用于计算每个节点对的局部GLI。
        
    metadata : dict
        Global metadata (e.g. structure type, PDB ID).
        全局元数据（如结构类型、PDB ID）
    """

    nodes: List[Node] = field(default_factory=list)
    curves: List[Curve] = field(default_factory=list)
    node_segments: Dict[int, List[Segment]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_curve(self, curve: Curve) -> None:
        """
        Add a curve to the structure and update node_segments mapping.
        向结构添加曲线并更新node_segments映射。
        
        Parameters / 参数
        ----------
        curve : Curve
            The curve to add / 要添加的曲线
        """
        self.curves.append(curve)
        # update node_segments mapping / 更新node_segments映射
        for seg in curve.segments:
            if seg.start_node_id is not None:
                self.node_segments.setdefault(seg.start_node_id, []).append(seg)
            if seg.end_node_id is not None:
                self.node_segments.setdefault(seg.end_node_id, []).append(seg)

    def add_node(self, node: Node) -> None:
        """
        Add a node to the structure.
        向结构添加节点。
        
        Parameters / 参数
        ----------
        node : Node
            The node to add / 要添加的节点
        """
        self.nodes.append(node)

    @property
    def coords(self) -> np.ndarray:
        """
        Return a (N,3) array of node coordinates.
        返回节点坐标的(N,3)数组。
        
        Returns / 返回
        -------
        np.ndarray
            Coordinate array, shape (N, 3) / 坐标数组，形状为(N, 3)
        """
        if not self.nodes:
            return np.zeros((0, 3), dtype=float)
        return np.stack([n.coord for n in self.nodes], axis=0)
