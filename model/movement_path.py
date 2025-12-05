# model/movement_path.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict


class PathKind(Enum):
    """
    敌人移动路径类型：
    - STRAIGHT: 恒定速度直线
    - SINE_H: 左右 SINE 摇摆 + 向下
    以后你可以继续加 CIRCLE / FIGURE8 / SCRIPTED 等。
    """
    STRAIGHT = auto()
    SINE_H = auto()


@dataclass
class PathConfig:
    """
    一条路径的参数定义（纯数据）：
    - kind: 路径类型
    - speed: 基础移动速度（像素 / 秒）
    - dir_x, dir_y: 对 STRAIGHT 生效的方向向量
    - amplitude: SINE 的振幅（像素）
    - frequency: SINE 的频率（每秒多少个周期）
    """
    kind: PathKind

    speed: float = 80.0

    dir_x: float = 0.0
    dir_y: float = 1.0

    amplitude: float = 40.0
    frequency: float = 1.0


@dataclass
class PathLibrary:
    """
    所有可用路径配置的库：
    通过字符串 key（path_name）找到 PathConfig。
    """
    configs: Dict[str, PathConfig] = field(default_factory=dict)


def create_default_path_library() -> PathLibrary:
    """
    建一套默认路径：直线下落、直线斜飞、左右 SINE 摇摆等等。
    """
    lib = PathLibrary()

    # 直线缓慢下落
    lib.configs["straight_down_slow"] = PathConfig(
        kind=PathKind.STRAIGHT,
        speed=60.0,
        dir_x=0.0,
        dir_y=1.0,
    )

    # 直线快速下落
    lib.configs["straight_down_fast"] = PathConfig(
        kind=PathKind.STRAIGHT,
        speed=120.0,
        dir_x=0.0,
        dir_y=1.0,
    )

    # 右下斜飞
    lib.configs["diag_down_right"] = PathConfig(
        kind=PathKind.STRAIGHT,
        speed=80.0,
        dir_x=0.7,
        dir_y=1.0,
    )

    # 左右摇摆 + 下落
    lib.configs["sine_down"] = PathConfig(
        kind=PathKind.SINE_H,
        speed=70.0,      # 向下速度
        dir_x=0.0,       # 基本不用
        dir_y=1.0,
        amplitude=50.0,  # 左右偏移幅度
        frequency=0.8,   # 每秒 0.8 个周期
    )

    return lib
