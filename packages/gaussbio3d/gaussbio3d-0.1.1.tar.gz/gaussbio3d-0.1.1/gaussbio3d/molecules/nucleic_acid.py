"""
Nucleic acid (DNA/RNA) structure representation
核酸(DNA/RNA)结构表示

This module defines the NucleicAcid class for representing DNA/RNA structures
built from PDB files.

本模块定义了NucleicAcid类，用于表示从PDB文件构建的DNA/RNA结构。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict
import numpy as np

from ..core.geometry import Node, Segment, Curve, Structure
from ..io import pdb as pdbio


def _is_nucleic_res(resname: str) -> bool:
    """
    Check if a residue name corresponds to a nucleic acid.
    检查残基名称是否对应核酸。
    
    Parameters / 参数
    ----------
    resname : str
        Residue name / 残基名称
        
    Returns / 返回
    -------
    bool
        True if nucleic acid / 如果是核酸则为True
    """
    r = resname.upper()
    # very rough list for DNA/RNA / DNA/RNA的粗略列表
    return r in {"DA", "DC", "DG", "DT", "A", "C", "G", "U"}


def _base_type(resname: str) -> str:
    """
    Get base type from residue name.
    从残基名称获取碱基类型。
    
    Parameters / 参数
    ----------
    resname : str
        Residue name / 残基名称
        
    Returns / 返回
    -------
    str
        Base type (A/C/G/T/U/OTHER) / 碱基类型
    """
    r = resname.upper()
    mapping = {
        "DA": "A",
        "DC": "C",
        "DG": "G",
        "DT": "T",
        "A": "A",
        "C": "C",
        "G": "G",
        "U": "U",
    }
    return mapping.get(r, "OTHER")


@dataclass
class NucleicAcid(Structure):
    """
    Nucleic acid (DNA/RNA) Structure.
    核酸(DNA/RNA)结构。

    We represent:
    我们表示为：
      - nodes: atoms (only nucleic acid residues) / 节点：原子（仅核酸残基）
      - curves: / 曲线：
          - backbone curve: P atom trace (or C4'/C3', etc.) per chain
            主链曲线：P原子追踪（或C4'/C3'等）每条链
          - base ring curves (TODO: simple connections from backbone to base heavy atoms)
            碱基环曲线（待办：从主链到碱基重原子的简单连接）
    """

    @classmethod
    def from_pdb(
        cls,
        path: str,
        chain_id: Optional[str] = None,
    ) -> "NucleicAcid":
        """
        Create a NucleicAcid from a PDB file.
        从PDB文件创建核酸。
        
        Parameters / 参数
        ----------
        path : str
            Path to PDB file / PDB文件路径
        chain_id : str, optional
            Chain ID to extract (if None, all chains) / 要提取的链ID（如果为None，则所有链）
            
        Returns / 返回
        -------
        NucleicAcid
            Nucleic acid structure / 核酸结构
        """
        coords, elements, meta_all = pdbio.load_pdb_atoms(
            path, chain_id=chain_id, only_protein=False
        )

        nodes: List[Node] = []
        for i, (coord, elem, m) in enumerate(zip(coords, elements, meta_all)):
            if not _is_nucleic_res(m["resname"]):
                continue
            group = _base_type(m["resname"])
            nodes.append(
                Node(
                    id=len(nodes),  # reindex / 重新索引
                    coord=np.asarray(coord, dtype=float),
                    element=elem,
                    group=group,  # group by base type / 按碱基类型分组
                    metadata=m,
                )
            )

        struct = cls(
            nodes=nodes,
            curves=[],
            node_segments={},
            metadata={"type": "nucleic_acid", "source": path, "chain_id": chain_id},
        )

        _build_backbone_curves_na(struct)
        _build_base_curves(struct)

        return struct


def _build_backbone_curves_na(struct: NucleicAcid) -> None:
    """
    Build backbone curves for nucleic acids.
    为核酸构建主链曲线。

    We approximate backbone using P atoms per chain in residue order.
    我们使用按残基顺序的每条链的P原子来近似主链。
    
    Parameters / 参数
    ----------
    struct : NucleicAcid
        Nucleic acid structure to modify / 要修改的核酸结构
    """
    chain_res_to_idx: Dict[tuple, int] = {}
    for i, n in enumerate(struct.nodes):
        m = n.metadata
        if m.get("atom_name", "").strip() == "P":
            key = (m["chain_id"], m["resid"])
            chain_res_to_idx[key] = i

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
                    start_type="P",
                    end_type="P",
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


def _build_base_curves(struct: NucleicAcid) -> None:
    """
    Build simple base curves.
    构建简单的碱基曲线。

    For each nucleotide, connect backbone atom(s) to base heavy atoms.
    For simplicity, we treat the first non-P heavy atom as backbone anchor.
    
    对于每个核苷酸，将主链原子连接到碱基重原子。
    为简单起见，我们将第一个非P重原子作为主链锚点。
    
    Parameters / 参数
    ----------
    struct : NucleicAcid
        Nucleic acid structure to modify / 要修改的核酸结构
    """
    res_to_indices: Dict[tuple, List[int]] = {}
    backbone_idx: Dict[tuple, int] = {}

    for i, n in enumerate(struct.nodes):
        m = n.metadata
        key = (m["chain_id"], m["resid"])
        res_to_indices.setdefault(key, []).append(i)

    for key, idxs in res_to_indices.items():
        # pick one P as backbone anchor if exists / 如果存在，选择一个P作为主链锚点
        P_candidates = [i for i in idxs if struct.nodes[i].metadata.get("atom_name", "").strip() == "P"]
        if P_candidates:
            backbone_idx[key] = P_candidates[0]
        else:
            # fallback: first atom as pseudo-backbone / 回退：第一个原子作为伪主链
            backbone_idx[key] = idxs[0]

    for key, idxs in res_to_indices.items():
        bb = backbone_idx[key]
        bb_coord = struct.nodes[bb].coord
        segments: List[Segment] = []
        for i in idxs:
            if i == bb:
                continue
            coord = struct.nodes[i].coord
            seg = Segment(
                start=bb_coord,
                end=coord,
                start_node_id=bb,
                end_node_id=i,
                start_type=struct.nodes[bb].element,
                end_type=struct.nodes[i].element,
            )
            segments.append(seg)
        if segments:
            curve = Curve(
                segments=segments,
                curve_type="base",
                metadata={"chain_id": key[0], "resid": key[1]},
            )
            struct.add_curve(curve)
