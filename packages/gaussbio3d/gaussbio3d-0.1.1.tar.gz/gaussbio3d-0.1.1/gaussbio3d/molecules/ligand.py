"""
Ligand (small molecule) structure representation
配体（小分子）结构表示

This module defines the Ligand class for representing small molecules
built from SDF/MOL2/SMILES files using RDKit.

本模块定义了Ligand类，用于表示使用RDKit从SDF/MOL2/SMILES文件构建的小分子。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List
import numpy as np

from ..core.geometry import Node, Segment, Curve, Structure
from ..io import mol as molio


@dataclass
class Ligand(Structure):
    """
    Ligand / small-molecule Structure.
    配体/小分子结构。

    Built from SDF/MOL2/SMILES using RDKit, with:
      - atoms as nodes / 原子作为节点
      - bonds as segments (split into half-bonds if desired) / 键作为线段（如需要可分割为半键）
      - optional ring curves (TODO) / 可选的环曲线（待实现）
    """

    @classmethod
    def from_sdf(cls, path: str) -> "Ligand":
        """
        Create a Ligand from an SDF file.
        从SDF文件创建配体。
        
        Parameters / 参数
        ----------
        path : str
            Path to SDF file / SDF文件路径
            
        Returns / 返回
        -------
        Ligand
            Ligand structure / 配体结构
        """
        mol = molio.load_mol_from_sdf(path)
        return cls._from_rdkit_mol(mol, source=f"sdf:{path}")

    @classmethod
    def from_mol2(cls, path: str) -> "Ligand":
        """
        Create a Ligand from a MOL2 file.
        从MOL2文件创建配体。
        
        Parameters / 参数
        ----------
        path : str
            Path to MOL2 file / MOL2文件路径
            
        Returns / 返回
        -------
        Ligand
            Ligand structure / 配体结构
        """
        mol = molio.load_mol_from_mol2(path)
        return cls._from_rdkit_mol(mol, source=f"mol2:{path}")

    @classmethod
    def from_smiles(cls, smiles: str) -> "Ligand":
        """
        Create a Ligand from a SMILES string.
        从SMILES字符串创建配体。
        
        Parameters / 参数
        ----------
        smiles : str
            SMILES string / SMILES字符串
            
        Returns / 返回
        -------
        Ligand
            Ligand structure with 3D coordinates / 带3D坐标的配体结构
        """
        mol = molio.load_mol_from_smiles(smiles)
        return cls._from_rdkit_mol(mol, source=f"smiles:{smiles}")

    @classmethod
    def _from_rdkit_mol(cls, mol, source: str) -> "Ligand":
        """
        Internal method to build Ligand from RDKit molecule.
        从RDKit分子构建配体的内部方法。
        
        Parameters / 参数
        ----------
        mol : rdkit.Chem.Mol
            RDKit molecule object / RDKit分子对象
        source : str
            Source description / 来源描述
            
        Returns / 返回
        -------
        Ligand
            Ligand structure / 配体结构
        """
        coords, elements = molio.mol_to_coordinates_and_elements(mol)
        bonds = molio.mol_to_bond_pairs(mol)

        nodes: List[Node] = []
        for i, (coord, elem) in enumerate(zip(coords, elements)):
            nodes.append(
                Node(
                    id=i,
                    coord=np.asarray(coord, dtype=float),
                    element=elem,
                    group=elem,  # default grouping: by element / 默认分组：按元素
                    metadata=dict(source=source),
                )
            )

        struct = cls(nodes=nodes, curves=[], node_segments={}, metadata={"type": "ligand", "source": source})

        # Build bond curves: each bond is represented as two half-segments
        # 构建键曲线：每个键表示为两个半线段
        for (i, j) in bonds:
            coord_i = struct.nodes[i].coord
            coord_j = struct.nodes[j].coord
            midpoint = 0.5 * (coord_i + coord_j)
            seg1 = Segment(
                start=coord_i,
                end=midpoint,
                start_node_id=i,
                end_node_id=None,
                start_type=struct.nodes[i].element,
                end_type=struct.nodes[j].element,
            )
            seg2 = Segment(
                start=coord_j,
                end=midpoint,
                start_node_id=j,
                end_node_id=None,
                start_type=struct.nodes[j].element,
                end_type=struct.nodes[i].element,
            )
            curve = Curve(segments=[seg1, seg2], curve_type="bond")
            struct.add_curve(curve)

        # TODO: ring detection and ring curves can be added here.
        # 待办：可以在此处添加环检测和环曲线

        return struct
