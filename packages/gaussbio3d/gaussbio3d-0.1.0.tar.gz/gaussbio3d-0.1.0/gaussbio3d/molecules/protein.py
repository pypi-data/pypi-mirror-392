"""
Protein structure representation
蛋白质结构表示

This module defines the Protein class for representing protein structures
built from PDB files.

本模块定义了Protein类，用于表示从PDB文件构建的蛋白质结构。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict
import numpy as np

from ..core.geometry import Node, Segment, Curve, Structure
from ..io import pdb as pdbio


def _classify_residue(resname: str) -> str:
    """
    Coarse-grained residue class based on hydrophobicity/charge/aromaticity.
    基于疏水性/电荷/芳香性的粗粒度残基分类。

    This is a simple heuristic; feel free to refine.
    这是一个简单的启发式方法；可以根据需要改进。
    
    Parameters / 参数
    ----------
    resname : str
        Three-letter residue name / 三字母残基名称
        
    Returns / 返回
    -------
    str
        Residue class label / 残基类别标签
    """
    resname = resname.upper()
    hydrophobic = {"ALA", "VAL", "ILE", "LEU", "MET", "PRO"}
    aromatic = {"PHE", "TYR", "TRP", "HIS"}
    positive = {"LYS", "ARG", "HIS"}
    negative = {"ASP", "GLU"}
    polar = {"SER", "THR", "ASN", "GLN", "CYS"}

    if resname in hydrophobic:
        return "hydrophobic"  # 疏水性
    if resname in aromatic:
        return "aromatic"  # 芳香性
    if resname in positive:
        return "positive"  # 正电荷
    if resname in negative:
        return "negative"  # 负电荷
    if resname in polar:
        return "polar"  # 极性
    return "other"  # 其他


@dataclass
class Protein(Structure):
    """
    Protein Structure built from a PDB file.
    从PDB文件构建的蛋白质结构。

    We represent:
    我们表示为：
      - nodes: at atom-level (default), but group by residue_class
        节点：原子级别（默认），但按残基类别分组
      - curves: / 曲线：
          - backbone curve: Cα trace / 主链曲线：Cα追踪
          - sidechain curves: heavy-atom chains per residue (simplified)
            侧链曲线：每个残基的重原子链（简化）
    """

    @classmethod
    def from_pdb(
        cls,
        path: str,
        chain_id: Optional[str] = None,
    ) -> "Protein":
        """
        Create a Protein from a PDB file.
        从PDB文件创建蛋白质。
        
        Parameters / 参数
        ----------
        path : str
            Path to PDB file / PDB文件路径
        chain_id : str, optional
            Chain ID to extract (if None, all chains) / 要提取的链ID（如果为None，则所有链）
            
        Returns / 返回
        -------
        Protein
            Protein structure / 蛋白质结构
        """
        coords, elements, meta = pdbio.load_pdb_atoms(
            path, chain_id=chain_id, only_protein=True
        )

        nodes: List[Node] = []
        for i, (coord, elem, m) in enumerate(zip(coords, elements, meta)):
            resclass = _classify_residue(m["resname"])
            nodes.append(
                Node(
                    id=i,
                    coord=np.asarray(coord, dtype=float),
                    element=elem,
                    group=resclass,
                    metadata=m,
                )
            )

        struct = cls(
            nodes=nodes,
            curves=[],
            node_segments={},
            metadata={"type": "protein", "source": path, "chain_id": chain_id},
        )

        # Build backbone curves (Cα trace per chain) / 构建主链曲线（每条链的Cα追踪）
        _build_backbone_curves(struct)
        # Build simplified sidechain curves / 构建简化的侧链曲线
        _build_sidechain_curves(struct)

        return struct


def _build_backbone_curves(struct: Protein) -> None:
    """
    Build a backbone curve per chain based on Cα atoms.
    基于Cα原子为每条链构建主链曲线。

    For simplicity, we treat consecutive Cα atoms in residue index order
    as a polyline. We attach segments to the Cα nodes.
    
    为简单起见，我们将按残基索引顺序的连续Cα原子视为折线。
    我们将线段附着到Cα节点。
    
    Parameters / 参数
    ----------
    struct : Protein
        Protein structure to modify / 要修改的蛋白质结构
    """
    # group Cα atoms by chain and residue id / 按链和残基ID对Cα原子分组
    chain_res_to_idx: Dict[tuple, int] = {}
    for i, n in enumerate(struct.nodes):
        m = n.metadata
        if m.get("atom_name", "").strip() == "CA":
            key = (m["chain_id"], m["resid"])
            chain_res_to_idx[key] = i

    # Build per-chain sorted residue ids / 构建每条链的排序残基ID
    chain_to_resids: Dict[str, List[int]] = {}
    for (chain, resid) in chain_res_to_idx.keys():
        chain_to_resids.setdefault(chain, []).append(resid)
    for chain in chain_to_resids:
        chain_to_resids[chain] = sorted(set(chain_to_resids[chain]))

    for chain, resids in chain_to_resids.items():
        segments: List[Segment] = []
        prev_idx: Optional[int] = None
        for resid in resids:
            idx = chain_res_to_idx[(chain, resid)]
            if prev_idx is not None:
                coord_prev = struct.nodes[prev_idx].coord
                coord_curr = struct.nodes[idx].coord
                seg = Segment(
                    start=coord_prev,
                    end=coord_curr,
                    start_node_id=prev_idx,
                    end_node_id=idx,
                    start_type="CA",
                    end_type="CA",
                )
                segments.append(seg)
            prev_idx = idx
        if segments:
            curve = Curve(
                segments=segments,
                curve_type="backbone",
                metadata={"chain_id": chain},
            )
            struct.add_curve(curve)


def _build_sidechain_curves(struct: Protein) -> None:
    """
    Build simplified sidechain curves per residue.
    为每个残基构建简化的侧链曲线。

    This is a very rough approximation:
      - For each residue, connect its non-Cα heavy atoms to Cα
        by direct segments.
        
    这是一个非常粗略的近似：
      - 对于每个残基，将其非Cα重原子通过直线段连接到Cα
      
    Parameters / 参数
    ----------
    struct : Protein
        Protein structure to modify / 要修改的蛋白质结构
    """
    # group atom indices by residue (chain, resid) / 按残基(链, 残基ID)对原子索引分组
    res_to_indices: Dict[tuple, List[int]] = {}
    ca_index: Dict[tuple, int] = {}
    for i, n in enumerate(struct.nodes):
        m = n.metadata
        key = (m["chain_id"], m["resid"])
        res_to_indices.setdefault(key, []).append(i)
        if m.get("atom_name", "").strip() == "CA":
            ca_index[key] = i

    for key, atom_indices in res_to_indices.items():
        if key not in ca_index:
            continue
        ca_idx = ca_index[key]
        ca_coord = struct.nodes[ca_idx].coord
        segments: List[Segment] = []
        for idx in atom_indices:
            if idx == ca_idx:
                continue
            coord = struct.nodes[idx].coord
            seg = Segment(
                start=ca_coord,
                end=coord,
                start_node_id=ca_idx,
                end_node_id=idx,
                start_type=struct.nodes[ca_idx].element,
                end_type=struct.nodes[idx].element,
            )
            segments.append(seg)
        if segments:
            curve = Curve(
                segments=segments,
                curve_type="sidechain",
                metadata={"chain_id": key[0], "resid": key[1]},
            )
            struct.add_curve(curve)
