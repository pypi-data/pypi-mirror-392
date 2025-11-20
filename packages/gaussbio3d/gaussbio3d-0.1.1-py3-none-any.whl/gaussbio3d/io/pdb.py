"""
PDB/mmCIF file I/O using Biopython
使用Biopython的PDB/mmCIF文件输入/输出

This module provides functions to load protein and nucleic acid structures
from PDB or mmCIF files and extract atomic coordinates and metadata.

本模块提供从PDB或mmCIF文件加载蛋白质和核酸结构并提取原子坐标和元数据的函数。
"""

from __future__ import annotations

from typing import List, Tuple, Dict
import numpy as np

try:
    from Bio.PDB import PDBParser, MMCIFParser
except ImportError:  # pragma: no cover
    PDBParser = None
    MMCIFParser = None


def load_pdb_atoms(
    path: str,
    chain_id: str | None = None,
    only_protein: bool = True,
) -> Tuple[np.ndarray, List[str], List[Dict]]:
    """
    Load coordinates and metadata from a PDB or mmCIF file using Biopython.
    使用Biopython从PDB或mmCIF文件加载坐标和元数据。

    Parameters / 参数
    ----------
    path : str
        Path to PDB/mmCIF file / PDB或mmCIF文件路径
    chain_id : str or None
        If not None, only consider this chain.
        如果不为None，则只考虑此链
    only_protein : bool
        If True, only take standard amino acids.
        如果为True，则只提取标准氨基酸

    Returns / 返回
    -------
    coords : np.ndarray
        Atomic coordinates, shape (N_atoms, 3) / 原子坐标，形状为(N_atoms, 3)
    elements : List[str]
        Element symbol per atom / 每个原子的元素符号
    meta : List[dict]
        Per-atom metadata: residue name, id, chain, atom name, etc.
        每个原子的元数据：残基名称、ID、链、原子名称等
        
    Raises / 引发
    ------
    ImportError
        If Biopython is not installed / 如果未安装Biopython
    """
    if PDBParser is None and MMCIFParser is None:
        raise ImportError("Biopython is required for structure parsing (pip install biopython).")

    ext = path.lower().rsplit(".", 1)[-1]
    if ext in {"cif", "mmcif"}:
        if MMCIFParser is None:
            raise ImportError("Biopython MMCIFParser not available; please install biopython.")
        parser = MMCIFParser(QUIET=True)
    else:
        if PDBParser is None:
            raise ImportError("Biopython PDBParser not available; please install biopython.")
        parser = PDBParser(QUIET=True)

    structure = parser.get_structure("struct", path)

    coords_list: List[np.ndarray] = []
    elements: List[str] = []
    meta: List[Dict] = []

    for model in structure:
        for chain in model:
            if chain_id is not None and chain.id != chain_id:
                continue
            for residue in chain:
                resname = residue.get_resname().strip()
                hetflag = residue.id[0].strip()
                if only_protein and hetflag != "" and hetflag != " ":
                    # skip non-standard residues / ligands
                    # 跳过非标准残基/配体
                    continue
                for atom in residue:
                    if atom.element is None or atom.element.strip() == "":
                        elem = atom.get_id()[0]  # fallback from atom name / 从原子名称回退
                    else:
                        elem = atom.element.strip()
                    pos = atom.coord
                    coords_list.append(pos)
                    elements.append(elem)
                    meta.append(
                        dict(
                            chain_id=chain.id,
                            resname=resname,
                            resid=residue.id[1],
                            atom_name=atom.get_name(),
                            hetflag=hetflag,
                        )
                    )

    if not coords_list:
        return np.zeros((0, 3)), [], []
    coords = np.stack(coords_list, axis=0)
    return coords, elements, meta
