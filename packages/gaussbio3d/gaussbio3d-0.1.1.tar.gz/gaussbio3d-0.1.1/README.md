# GaussBio3D: Multiscale Gauss Linking Integral Library
# GaussBio3D: 多尺度高斯链接积分库

A Python library for **multiscale Gauss linking integral (mGLI)**–based 3D topological descriptors for **small molecules, proteins and nucleic acids**.

一个基于**多尺度高斯链接积分(mGLI)**的Python库，用于**小分子、蛋白质和核酸**的3D拓扑描述符计算。

It is designed to be a **unified 3D representation framework** for biomolecular interaction tasks such as:

本库旨在为生物分子交互任务提供**统一的3D表示框架**，支持以下任务：

- Drug–Target Interaction (DTI) / 药物-靶点交互
- Protein–Protein Interaction (PPI) / 蛋白质-蛋白质交互
- Drug–Drug Interaction (DDI) / 药物-药物交互
- miRNA/Nucleic acid–Target Interaction (MTI) / miRNA/核酸-靶点交互
- Protein–DNA/RNA complexes / 蛋白质-DNA/RNA复合物等

---

## 1. Mathematical Background / 数学背景

### 1.1 Gauss Linking Integral (Continuous) / 高斯链接积分（连续形式）

Given two smooth space curves C₁ and C₂, the **Gauss linking integral** is

给定两条光滑空间曲线 C₁ 和 C₂，**高斯链接积分**定义为：

```
GLI(C₁, C₂) = (1/4π) ∫∫ [(dr₁ × dr₂) · (r₁ - r₂)] / ||r₁ - r₂||³
              C₁ C₂
```

It measures the **topological linking / winding** between two curves. For closed curves it is an integer (linking number), but for open curves (e.g. biomolecular fragments) it is a real-valued "linking strength".

它度量两条曲线之间的**拓扑缠绕/缠结**关系。对于闭合曲线，它是一个整数（链接数），但对于开放曲线（如生物分子片段），它是一个实值的"链接强度"。

### 1.2 Discrete Segment Approximation / 离散线段近似

We approximate each curve by a set of straight segments:

我们用一组直线段来近似每条曲线：

- C₁ = {Lᵢ}, where Lᵢ = [a₀, a₁]
- C₂ = {Mⱼ}, where Mⱼ = [b₀, b₁]

Then: / 则有：

```
GLI(C₁, C₂) ≈ Σᵢⱼ GLI(Lᵢ, Mⱼ)
```

For line segments L=[a₀,a₁] and M=[b₀,b₁], we use a **standard spherical geometry–based approximation** (the same as in your scripts):

对于线段 L=[a₀,a₁] 和 M=[b₀,b₁]，我们使用基于**球面几何的标准近似方法**：

1. Define / 定义：

```
r₀₀ = b₀ - a₀,  r₀₁ = b₁ - a₀
r₁₀ = b₀ - a₁,  r₁₁ = b₁ - a₁
```

2. Normalize these vectors to get four unit vectors on the unit sphere
   将这些向量归一化得到单位球面上的四个单位向量

3. Construct four oriented spherical triangles and sum their signed areas using `arcsin` of dot products between successive cross products
   构造四个定向球面三角形，使用连续叉积的点积的 `arcsin` 求和它们的有向面积

4. Multiply by a sign determined by the orientation of the two segments
   乘以由两个线段方向确定的符号

The library exposes `gli_segment(seg1, seg2, signed=True/False)` which computes this value. With `signed=False`, we use the absolute value |GLI| to measure **linking strength** independent of chirality.

本库提供 `gli_segment(seg1, seg2, signed=True/False)` 函数来计算此值。当 `signed=False` 时，我们使用绝对值 |GLI| 来度量与手性无关的**链接强度**。

---

## 2. Multiscale & Grouped mGLI Features / 多尺度与分组mGLI特征

We want features that capture **how strongly and at what distance scales** parts of molecule A and B are topologically linked.

我们希望捕获分子A和B的各部分在**何种强度和何种距离尺度**下的拓扑链接特征。

### 2.1 Node Pair Quantities / 节点对量

For nodes (atoms / residues / bases) i ∈ A, j ∈ B:

对于节点（原子/残基/碱基）i ∈ A, j ∈ B：

- Position / 位置: xᵢ, xⱼ
- Distance / 距离: rᵢⱼ = ||xᵢ - xⱼ||
- Local GLI / 局部GLI: gᵢⱼ = aggregated GLI between segments incident to node i and node j
  (sum or median over the node's local segments, as in your original code)
  节点i和节点j相关联线段之间的聚合GLI（对节点的局部线段求和或取中位数）

### 2.2 Radial Weighting (Multi-scale) / 径向加权（多尺度）

We define radial basis functions φₖ(r) (either **hard bins** or **RBF**):

我们定义径向基函数 φₖ(r)（**硬分箱**或**RBF**）：

- Hard bins / 硬分箱:

```
φₖ(r) = 𝟙[r ∈ [Rₖ, Rₖ₊₁)], k=1..K
```

- RBF / 径向基函数:

```
φₖ(r) = exp(-(r-μₖ)²/(2σₖ²))
```

Then multi-scale aggregated features / 则多尺度聚合特征为：

```
hₖ = Σᵢⱼ φₖ(rᵢⱼ) · f(gᵢⱼ)
```

where f can be gᵢⱼ, |gᵢⱼ| or different statistics (sum/mean/max/min/median over node pairs in that scale).

其中 f 可以是 gᵢⱼ、|gᵢⱼ| 或不同的统计量（该尺度下节点对的求和/均值/最大值/最小值/中位数）。

### 2.3 Grouping: Elements / Residues / Bases / 分组：元素/残基/碱基

We further group nodes by discrete categories:

我们进一步按离散类别对节点分组：

- small molecule / 小分子: element / functional group / 元素/官能团
- protein / 蛋白质: residue type or residue class (hydrophobic/aromatic/etc.) / 残基类型或残基类别（疏水/芳香等）
- nucleic acid / 核酸: base type (A/C/G/T/U) or backbone vs base / 碱基类型(A/C/G/T/U)或主链vs碱基

Define / 定义：

```
cₐ(i) ∈ {1,...,Cₐ},  c_B(j) ∈ {1,...,C_B}
```

Then / 则：

```
h_{cₐ,c_b,k} = Σ_{i,j: cₐ(i)=cₐ, c_B(j)=c_b} φₖ(rᵢⱼ) · f(gᵢⱼ)
```

Stacking these h_{cₐ,c_b,k} (and possibly their min/max/mean/median) gives a **global mGLI descriptor** for a structure pair.

堆叠这些 h_{cₐ,c_b,k}（以及可能的最小/最大/均值/中位数）可以得到结构对的**全局mGLI描述符**。

---

## 3. Unified Geometry Representation / 统一几何表示

We represent each biomolecule as / 我们将每个生物分子表示为：

- `Node` / 节点: atom / residue / base / 原子/残基/碱基
- `Segment` / 线段: oriented segment between two 3D points, optionally attached to nodes / 两个3D点之间的有向线段，可选地附着到节点
- `Curve` / 曲线: a polyline made of segments, e.g. backbone, side-chain, ring / 由线段组成的折线，如主链、侧链、环
- `Structure` / 结构: collection of nodes + curves + mapping from nodes to their local segments / 节点+曲线的集合+节点到其局部线段的映射

This supports / 这支持：

- small molecule / 小分子:
  - backbone curves (bond chains) / 主链曲线（键链）
  - ring curves (aromatic / aliphatic rings) / 环曲线（芳香环/脂肪环）
- protein / 蛋白质:
  - backbone curve (Cα trace) / 主链曲线（Cα追踪）
  - sidechain curves per residue / 每个残基的侧链曲线
- nucleic acid / 核酸:
  - backbone curve (phosphate or sugar-phosphate) / 主链曲线（磷酸或糖-磷酸）
  - base ring curves / 碱基环曲线

---

## 4. Installation & Dependencies / 安装和依赖

GaussBio3D **requires RDKit** for small-molecule I/O (SDF/MOL2/SMILES) and **requires Biopython** for PDB/mmCIF parsing.
GaussBio3D **强制依赖 RDKit**（用于小分子 I/O：SDF/MOL2/SMILES）以及 **Biopython**（用于 PDB/mmCIF 解析）。

Required / 必需：

- Python 3.9+
- `numpy`
- `rdkit`
- `biopython`
- `tqdm` (progress bars)

Recommended installation on Windows/macOS/Linux via Conda（推荐方式）：

```bash
conda install -c conda-forge rdkit
pip install gaussbio3d
pip install numba  # optional JIT acceleration
```

If you prefer pip-only and have an RDKit wheel available for your platform:
若仅使用 pip 并且你的平台可用 RDKit 轮子：

```bash
pip install rdkit-pypi
pip install gaussbio3d
pip install numba  # optional JIT acceleration
```

From source / 从源码安装：

```bash
git clone https://github.com/yourusername/GaussBio3D
cd GaussBio3D
pip install -e .
```

---

## Quick Start / 快速开始

### Environment & Install / 环境与安装

- Python `3.9+`，支持 Windows / macOS / Linux。
- 必需依赖：`numpy`、`rdkit`、`biopython`、`tqdm`。
- 推荐安装：
  - Conda 安装 RDKit：`conda install -c conda-forge rdkit`
  - 安装包：`pip install gaussbio3d`
  - 可选加速：`pip install numba`（CPU JIT）、`pip install ripser`（PH）、`pip install torch`（GPU，按环境选择 CUDA/CPU 索引）。
- 源码安装：
  ```bash
  git clone https://github.com/yourusername/GaussBio3D
  cd GaussBio3D
  pip install -e .
  # 可选特性一键安装
  pip install -r GaussBio3D/requirements-optional.txt
  ```

### Core Methods & Scenarios / 核心方法与适用场景

- 方法A：全局mGLI描述符（结构对级别）
  - 输入：`Structure` A/B（蛋白质/核酸/小分子），`MgliConfig`。
  - 输出：`np.ndarray`，形状 `(D,)` 的整体拓扑摘要向量。
  - 典型用途：结构对相似性、分类/回归模型输入、检索/打分。
  - 参数要点：`distance_bins`/`use_rbf` 控制尺度；`group_mode_A/B` 控制分组；`signed` 控制是否保留手性；性能相关 `max_distance`、`n_jobs`、`use_gpu`。
  - 接口：`features.descriptor.global_mgli_descriptor(structA, structB, config)`。

- 方法B：节点级mGLI特征（图节点通道）
  - 输入：`Structure` A/B，`MgliConfig`。
  - 输出：`np.ndarray` 或字典结构（视实现），形状约 `(N_nodes, C)`；可与PLM/GeoGNN嵌入拼接。
  - 典型用途：DTI/PPI 图模型的节点特征增强，作为额外的3D拓扑通道。
  - 参数要点：分组策略影响通道维度（如残基类别、元素/官能团）；同样支持 `max_distance`、`n_jobs`、`use_gpu`。
  - 接口：`features.node_features.node_mgli_features(structA, structB, config)`。

- 方法C：成对mGLI矩阵（跨注意力/边特征优化方案）
  - 输入：`Structure` A/B，`MgliConfig`。
  - 输出：`np.ndarray`，形状 `(N_A, N_B)` 的节点对矩阵，用于跨注意力偏置或边特征。
  - 典型用途：Cross-attention GNN 的 bias/edge weight，或匹配/对齐任务的相似度基底。
  - 性能要点：支持 `max_distance` 距离剪枝、`n_jobs` 行并行、`use_gpu` 的PyTorch批量GLI。
  - 接口：`features.pairwise.pairwise_mgli_matrix(structA, structB, config)`。

- 方法D：拓扑(PH)特征直方图（可选）
  - 输入：距离矩阵（来自结构对或子结构），`MgliConfig`（用于直方图参数）。
  - 输出：`np.ndarray` 的PH直方图向量，可与mGLI特征级联。
  - 典型用途：几何-拓扑融合，如口袋识别、复合物界面模式分析、鲁棒结构摘要。
  - 依赖说明：需要 `ripser`；未安装时对应接口抛出 ImportError。
  - 接口：`features.topo_features.ph_histogram_features(distance_matrix, config)`。

- 方法E：任务封装（DTI/PPI/MTI）
  - 输入：文件路径与任务参数（如 `pdb_path`、`sdf_path`、`chain_id`），`MgliConfig`。
  - 输出：包含全局/节点/成对矩阵等的特征字典，支持 `utils/cache.CacheManager` 的命名缓存持久化。
  - 典型用途：一键批量特征计算与落盘，统一命名为 `物质名_方法_维度.npy` 便于复用。
  - 配置透传：`max_distance`、`n_jobs`、`use_gpu` 等性能参数在任务接口中向下透传。
  - 接口：`tasks.dti.compute_dti_features(...)` 等。

#### Method Differences & Selection / 方法差异与选择建议

- 方法A（全局）
  - 粒度：结构对级别；输出 `(D,)` 一维摘要向量。
  - 适用：检索、分类/回归、全局评分与排序。
  - 优势：维度低、稳健，易与传统ML管线对接。
  - 局限：不提供节点或边级细节，难直接用于注意力。

- 方法B（节点级）
  - 粒度：节点；输出约 `(N_nodes, C)`。
  - 适用：图模型节点通道，融合 PLM/GeoGNN 嵌入。
  - 优势：保留局部差异，便于多模态特征拼接。
  - 局限：维度随分组增长，需规范化与正则。

- 方法C（成对矩阵）
  - 粒度：节点对；输出 `(N_A, N_B)`。
  - 适用：跨注意力偏置/边权，相似度匹配与对齐。
  - 优势：最细粒度，信息最丰富，适合注意力机制。
  - 性能：计算量最高；可通过 `max_distance`、`n_jobs`、`use_gpu` 显著加速。

- 方法D（PH直方图）
  - 输入：距离矩阵；输出拓扑直方图向量。
  - 适用：几何-拓扑融合（口袋识别、界面模式摘要），对噪声/变形更鲁棒。
  - 依赖：需安装 `ripser`；与mGLI联合使用更佳。
  - 局限：不直接体现GLI手性与方向性，需要与mGLI特征互补。

- 方法E（任务封装）
  - 作用：一键生成全局/节点/成对等特征并落盘（统一命名与缓存）。
  - 适用：快速集成与批处理，减少样板代码与重复计算。
  - 优势：封装配置透传与命名规范，便于复用与协作。
  - 局限：灵活性不如直接调用底层接口，定制时需回到A–D方法。

选择建议：
- 需要全局摘要与检索 → 选 方法A。
- 构建图模型并增强节点通道 → 选 方法B，并与PLM/GeoGNN拼接。
- 需要跨注意力或边权/匹配 → 选 方法C；优先启用 `max_distance` 与并行/GPU。
- 希望鲁棒的拓扑摘要或几何-拓扑融合 → 选 方法D，并与mGLI联合。
- 快速落地与批处理 → 选 方法E（任务封装）。

### Basic Example / 基础示例

```python
from gaussbio3d.molecules import Protein, Ligand
from gaussbio3d.config import MgliConfig
from gaussbio3d.features.descriptor import global_mgli_descriptor
from gaussbio3d.features.pairwise import pairwise_mgli_matrix

# 加载结构
prot = Protein.from_pdb("examples/target.pdb", chain_id="A")
lig  = Ligand.from_sdf("examples/drug.sdf")

# 配置：启用距离剪枝/并行/GPU（按需）
cfg = MgliConfig(max_distance=8.0, n_jobs=4, use_gpu=False)

# 全局描述符
desc = global_mgli_descriptor(prot, lig, cfg)
print("global shape:", desc.shape)

# 成对矩阵（用于交叉注意力）
M = pairwise_mgli_matrix(prot, lig, cfg)
print("pairwise shape:", M.shape)
```

### FAQ / 常见问题解答

- RDKit 安装失败怎么办？
  - Windows/macOS/Linux 推荐 `conda install -c conda-forge rdkit`；或使用 `rdkit-pypi` 轮子。
- 没有GPU可以使用吗？
  - 可以。未安装 `torch` 或无CUDA时会自动走CPU路径；`use_gpu=True` 仅在 `torch` 可用时启用。
- 如何加速大规模结构对计算？
  - 设置 `max_distance` 做距离剪枝；`n_jobs` 并行行处理；按需启用 GPU；使用 `utils/cache.py` 复用中间结果。
- PDB/mmCIF 链选择问题？
  - 通过 `Protein.from_pdb(path, chain_id="A")` 指定链；mmCIF同理。
- 输出文件命名如何统一？
  - 使用 `utils.cache.format_name(material, method, dim)` 与 `CacheManager.save_named(...)`，生成 `物质名_方法_维度.npy`。

### Advanced Guidance & Best Practices / 进阶指引与最佳实践

- 距离尺度设计：根据任务选择 `distance_bins` 或 RBF；近距强调强拓扑、远距捕获全局趋势。
- 分组策略：蛋白质用残基类别/功能分类，小分子用元素/官能团；避免高维稀疏造成噪声。
- 计算加速：优先启用 `max_distance`；`n_jobs` 在节点维度并行；GPU 适合大矩阵批量GLI。
- 特征融合：将节点级mGLI与PLM/GeoGNN嵌入拼接，作为额外的3D拓扑通道。
- 缓存与复用：对距离矩阵、成对GLI等中间结果做持久化缓存，减少重复计算。
- 可复现性：固定随机种子、记录配置参数与依赖版本；在CI中做小样本回归测试。

## 5. Basic Usage / 基本用法

### 5.1 Compute a Protein–Ligand Global mGLI Descriptor / 计算蛋白质-配体全局mGLI描述符

```python
from gaussbio3d.molecules import Protein, Ligand
from gaussbio3d.config import MgliConfig
from gaussbio3d.features.descriptor import global_mgli_descriptor

# Load protein and ligand / 加载蛋白质和配体
prot = Protein.from_pdb("examples/target.pdb", chain_id="A")
lig = Ligand.from_sdf("examples/drug.sdf")

# Configure mGLI parameters / 配置mGLI参数
config = MgliConfig(
    distance_bins=[0.0, 3.0, 6.0, 10.0, 20.0],
    use_rbf=False,
    signed=False,
    group_mode_A="residue_class",
    group_mode_B="element",
)

# Compute global descriptor / 计算全局描述符
feat = global_mgli_descriptor(prot, lig, config)
print("Feature shape:", feat.shape)
```

Quick DTI example / 快速 DTI 示例：

```python
from gaussbio3d.tasks.dti import compute_dti_features
from gaussbio3d.config import MgliConfig

cfg = MgliConfig()
feats = compute_dti_features(
    pdb_path="examples/target.pdb",  # supports .pdb or .cif
    sdf_path="examples/drug.sdf",
    chain_id="A",
    config=cfg,
)
print({k: v.shape for k, v in feats.items()})
```

### 5.2 Node-level mGLI Features for a DTI Model / DTI模型的节点级mGLI特征

```python
from gaussbio3d.features.node_features import node_mgli_features

# Compute node-level features / 计算节点级特征
node_feat_prot = node_mgli_features(prot, lig, config)
node_feat_lig  = node_mgli_features(lig, prot, config)
```

These can be concatenated with PLM embeddings / GeoGNN embeddings as 3D topological channels.

这些可以与PLM嵌入/GeoGNN嵌入连接作为3D拓扑通道。

### 5.3 Pairwise mGLI Matrix for Cross-attention / 用于交叉注意力的成对mGLI矩阵

```python
from gaussbio3d.features.pairwise import pairwise_mgli_matrix

# Compute pairwise matrix / 计算成对矩阵
M = pairwise_mgli_matrix(prot, lig, config)
# M.shape = (N_prot_nodes, N_lig_nodes)
```

Use M as a bias term or edge feature in a DTI cross-attention GNN.

在DTI交叉注意力GNN中将M用作偏置项或边特征。

---

## 6. Tasks Helpers (DTI / PPI / MTI) / 任务辅助工具

We provide thin convenience wrappers in `gaussbio3d.tasks` to integrate easily with your existing pipelines.

我们在 `gaussbio3d.tasks` 中提供了简便的包装器，以便轻松集成到您现有的流程中。

Example / 示例:

```python
from gaussbio3d.tasks.dti import compute_dti_features

# Compute all DTI features at once / 一次性计算所有DTI特征
dti_feats = compute_dti_features(
    pdb_path="examples/target.pdb",
    sdf_path="examples/drug.sdf",
)
```

---

 

## 8. Project Structure / 项目结构

```
GaussBio3D/
├── gaussbio3d/
│   ├── __init__.py
│   ├── config.py              # Configuration / 配置
│   ├── core/                  # Core algorithms / 核心算法
│   │   ├── geometry.py        # Geometric primitives / 几何基元
│   │   └── gli.py             # GLI computation / GLI计算
│   ├── features/              # Feature extraction / 特征提取
│   │   ├── descriptor.py      # Global descriptors / 全局描述符
│   │   ├── node_features.py   # Node-level features / 节点级特征
│   │   └── pairwise.py        # Pairwise features / 成对特征
│   ├── io/                    # Input/Output / 输入输出
│   │   ├── mol.py             # Molecule file I/O / 分子文件I/O
│   │   └── pdb.py             # PDB file I/O / PDB文件I/O
│   ├── molecules/             # Molecule representations / 分子表示
│   │   ├── ligand.py          # Small molecules / 小分子
│   │   ├── protein.py         # Proteins / 蛋白质
│   │   └── nucleic_acid.py    # Nucleic acids / 核酸
│   └── tasks/                 # Task-specific helpers / 特定任务辅助
│       ├── dti.py             # Drug-Target Interaction / 药物-靶点交互
│       ├── ppi.py             # Protein-Protein Interaction / 蛋白质-蛋白质交互
│       └── mti.py             # Molecule-Target Interaction / 分子-靶点交互
├── examples/                  # Example scripts / 示例脚本
├── tests/                     # Unit tests / 单元测试
├── README.md
├── setup.py
└── requirements.txt
```

---

## Performance & Topology Extensions / 性能与拓扑扩展

- Distance pruning: set `MgliConfig.max_distance` to mask far pairs.
- Parallel rows: set `MgliConfig.n_jobs` for thread-based parallel over nodes.
- GPU backend: set `MgliConfig.use_gpu=True` to enable PyTorch tensors (requires `torch` and CUDA).
- Topology (PH): `features/topo_features.py` provides PH histograms via `ripser` and concatenation with mGLI.
- Cache & naming: `utils/cache.py` persists intermediates and saves outputs as `物质名_方法_维度.npy`.

Optional dependencies: `numba` (JIT), `torch` (GPU), `ripser` (PH).

## License / 许可证

MIT License

---

## Citation / 引用

If you use GaussBio3D in your research, please cite:

如果您在研究中使用了GaussBio3D，请引用：

```bibtex
@software{gaussbio3d,
  title={GaussBio3D: Multiscale Gauss Linking Integral Library for Biomolecular 3D Topology},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/GaussBio3D}
}
```
