"""
Configuration module for mGLI feature computation
mGLI特征计算的配置模块
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Any, Dict
import json


@dataclass
class MgliConfig:
    """
    Global configuration for mGLI feature computation.
    mGLI特征计算的全局配置。

    Attributes / 属性
    ----------
    distance_bins : List[float]
        If use_rbf=False: interpreted as bin edges [R0, R1, ..., RK].
        If use_rbf=True: interpreted as RBF centers μ_k (σ is inferred or given).
        
        如果use_rbf=False: 解释为分箱边界 [R0, R1, ..., RK]
        如果use_rbf=True: 解释为RBF中心 μ_k（σ被推断或给定）
        
    use_rbf : bool
        Whether to use RBF radial basis (True) or hard bins (False).
        是否使用RBF径向基(True)或硬分箱(False)
        
    rbf_sigma : Optional[float]
        If use_rbf=True and rbf_sigma is None, a heuristic σ is used
        (e.g. based on mean gap between centers).
        
        如果use_rbf=True且rbf_sigma为None，将使用启发式σ
        （例如基于中心之间的平均间隔）
        
    signed : bool
        Whether to keep the signed GLI (True) or use |GLI| (False).
        是否保留有符号的GLI(True)或使用|GLI|(False)
        
    stats : List[str]
        Statistics to aggregate over node pairs: subset of
        ["sum", "mean", "max", "min", "median"].
        
        在节点对上聚合的统计量：
        ["sum", "mean", "max", "min", "median"]的子集
        
    group_mode_A : str
        How to group nodes in structure A:
        - "element": use node.element
        - "group": use node.group (residue class / base type, etc.)
        
        如何对结构A中的节点分组：
        - "element": 使用node.element
        - "group": 使用node.group（残基类别/碱基类型等）
        
    group_mode_B : str
        Same as group_mode_A but for structure B.
        与group_mode_A相同，但用于结构B
    """

    distance_bins: List[float] = field(
        default_factory=lambda: [0.0, 3.0, 6.0, 10.0, 20.0]
    )
    use_rbf: bool = False
    rbf_sigma: Optional[float] = None
    signed: bool = False
    stats: List[str] = field(
        default_factory=lambda: ["sum", "mean", "max", "min", "median"]
    )
    group_mode_A: str = "element"
    group_mode_B: str = "element"

    # Performance and execution options / 性能与执行选项
    use_gpu: bool = False
    max_distance: Optional[float] = None
    n_jobs: int = 1

    def to_json(self) -> str:
        """Serialize configuration to JSON string / 将配置序列化为JSON字符串"""
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(s: str) -> "MgliConfig":
        """Create configuration from JSON string / 从JSON字符串创建配置"""
        data: Dict[str, Any] = json.loads(s)
        return MgliConfig(**data)
