"""
Molecule file I/O using RDKit
使用RDKit的分子文件输入/输出

This module provides functions to load small molecules from various file formats
(SDF, MOL2, SMILES) and extract coordinates and connectivity information.

本模块提供从各种文件格式(SDF、MOL2、SMILES)加载小分子并提取坐标和连接信息的函数。
"""

from __future__ import annotations

from typing import Tuple, List
import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
except ImportError:  # pragma: no cover
    Chem = None
    AllChem = None


def load_mol_from_sdf(path: str) -> "Chem.Mol":
    """
    Load an RDKit mol object from an SDF file.
    从SDF文件加载RDKit分子对象。
    
    Parameters / 参数
    ----------
    path : str
        Path to SDF file / SDF文件路径
        
    Returns / 返回
    -------
    Chem.Mol
        RDKit molecule object / RDKit分子对象
        
    Raises / 引发
    ------
    ImportError
        If RDKit is not installed / 如果未安装RDKit
    ValueError
        If no valid molecule found in file / 如果文件中未找到有效分子
    """
    if Chem is None:
        raise ImportError("RDKit is required for SDF parsing (pip install rdkit-pypi).")
    suppl = Chem.SDMolSupplier(path, removeHs=False)
    mols = [m for m in suppl if m is not None]
    if not mols:
        raise ValueError(f"No valid molecule found in SDF: {path}")
    return mols[0]


# RDKit is required for SDF/MOL2/SMILES parsing in release


def load_mol_from_mol2(path: str) -> "Chem.Mol":
    """
    Load an RDKit mol object from a MOL2 file.
    从MOL2文件加载RDKit分子对象。
    
    Parameters / 参数
    ----------
    path : str
        Path to MOL2 file / MOL2文件路径
        
    Returns / 返回
    -------
    Chem.Mol
        RDKit molecule object / RDKit分子对象
        
    Raises / 引发
    ------
    ImportError
        If RDKit is not installed / 如果未安装RDKit
    ValueError
        If failed to read MOL2 file / 如果读取MOL2文件失败
    """
    if Chem is None:
        raise ImportError("RDKit is required for MOL2 parsing.")
    mol = Chem.MolFromMol2File(path, removeHs=False)
    if mol is None:
        raise ValueError(f"Failed to read MOL2: {path}")
    return mol


def load_mol_from_smiles(smiles: str) -> "Chem.Mol":
    """
    Load an RDKit mol object from SMILES and generate 3D conformer.
    从SMILES加载RDKit分子对象并生成3D构象。
    
    Parameters / 参数
    ----------
    smiles : str
        SMILES string / SMILES字符串
        
    Returns / 返回
    -------
    Chem.Mol
        RDKit molecule object with 3D coordinates / 带3D坐标的RDKit分子对象
        
    Raises / 引发
    ------
    ImportError
        If RDKit is not installed / 如果未安装RDKit
    ValueError
        If failed to parse SMILES / 如果解析SMILES失败
    """
    if Chem is None or AllChem is None:
        raise ImportError("RDKit is required for SMILES/3D generation.")
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Failed to parse SMILES: {smiles}")
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, AllChem.ETKDG())
    AllChem.UFFOptimizeMolecule(mol)
    return mol


def mol_to_coordinates_and_elements(mol: "Chem.Mol") -> Tuple[np.ndarray, List[str]]:
    """
    Extract 3D coordinates and element symbols from an RDKit molecule.
    从RDKit分子中提取3D坐标和元素符号。

    Parameters / 参数
    ----------
    mol : Chem.Mol
        RDKit molecule object / RDKit分子对象

    Returns / 返回
    -------
    coords : np.ndarray
        Atomic coordinates, shape (N_atoms, 3) / 原子坐标，形状为(N_atoms, 3)
    elements : List[str]
        Element symbol per atom / 每个原子的元素符号
    """
    conf = mol.GetConformer()
    n = mol.GetNumAtoms()
    coords = np.zeros((n, 3), dtype=float)
    elements: List[str] = []
    for i, atom in enumerate(mol.GetAtoms()):
        pos = conf.GetAtomPosition(i)
        coords[i] = [pos.x, pos.y, pos.z]
        elements.append(atom.GetSymbol())
    return coords, elements


def mol_to_bond_pairs(mol: "Chem.Mol") -> List[Tuple[int, int]]:
    """
    Extract bond pairs (i, j) from RDKit molecule.
    从RDKit分子中提取键对(i, j)。
    
    Parameters / 参数
    ----------
    mol : Chem.Mol
        RDKit molecule object / RDKit分子对象
        
    Returns / 返回
    -------
    bonds : List[Tuple[int, int]]
        List of atom index pairs connected by bonds
        由键连接的原子索引对列表
    """
    bonds = []
    for bond in mol.GetBonds():
        i = bond.GetBeginAtomIdx()
        j = bond.GetEndAtomIdx()
        bonds.append((i, j))
    return bonds
