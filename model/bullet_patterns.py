"""
弹幕模式系统
提供可扩展的敌弹发射模式，使用注册表实现开闭原则。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, List, Callable

from pygame.math import Vector2

from .registry import Registry

if TYPE_CHECKING:
    from .game_state import GameState
    from .components import Position


class BulletPatternKind(Enum):
    """弹幕模式类型"""
    AIM_PLAYER = auto()      # 自机狙
    STRAIGHT_DOWN = auto()   # 直下
    N_WAY = auto()           # N-Way 扇形弹
    RING = auto()            # 全方位环形弹
    SPIRAL = auto()          # 螺旋弹


@dataclass
class BulletPatternConfig:
    """
    弹幕模式配置

    Attributes:
        kind: 弹幕类型
        bullet_speed: 子弹速度
        damage: 伤害值
        count: 子弹数量（用于 N_WAY, RING 等）
        spread_deg: 扇形展开角度（用于 N_WAY）
        start_angle_deg: 起始角度（用于 RING, SPIRAL）
        spin_speed_deg: 每秒旋转角度（用于 SPIRAL）
    """
    kind: BulletPatternKind = BulletPatternKind.AIM_PLAYER
    bullet_speed: float = 260.0
    damage: int = 1
    count: int = 1
    spread_deg: float = 30.0
    start_angle_deg: float = 0.0
    spin_speed_deg: float = 60.0


@dataclass
class PatternState:
    """
    弹幕模式运行时状态（挂在敌人身上）
    """
    current_angle: float = 0.0  # 当前旋转角度（用于 SPIRAL）


# 弹幕模式注册表
# 返回值类型: List[Vector2] 表示要发射的每颗子弹的速度向量
bullet_pattern_registry: Registry[BulletPatternKind] = Registry("bullet_pattern")


def execute_pattern(
    state: "GameState",
    shooter_pos: "Position",
    config: BulletPatternConfig,
    pattern_state: PatternState | None = None,
) -> List[Vector2]:
    """
    执行弹幕模式，返回要发射的子弹速度列表。

    Args:
        state: 游戏状态
        shooter_pos: 发射者位置
        config: 弹幕配置
        pattern_state: 可选的运行时状态

    Returns:
        子弹速度向量列表
    """
    handler = bullet_pattern_registry.get(config.kind)
    if not handler:
        # 默认直下
        return [Vector2(0, config.bullet_speed)]

    return handler(state, shooter_pos, config, pattern_state)


# ========== 弹幕模式实现 ==========

@bullet_pattern_registry.register(BulletPatternKind.AIM_PLAYER)
def _pattern_aim_player(
    state: "GameState",
    shooter_pos: "Position",
    config: BulletPatternConfig,
    pattern_state: PatternState | None,
) -> List[Vector2]:
    """自机狙：朝向玩家发射"""
    from .components import Position as Pos

    if not state.player:
        return [Vector2(0, config.bullet_speed)]

    player_pos = state.player.get(Pos)
    if not player_pos:
        return [Vector2(0, config.bullet_speed)]

    dir_vec = Vector2(player_pos.x - shooter_pos.x, player_pos.y - shooter_pos.y)
    if dir_vec.length_squared() < 1e-9:
        return [Vector2(0, config.bullet_speed)]

    dir_vec = dir_vec.normalize() * config.bullet_speed
    return [dir_vec]


@bullet_pattern_registry.register(BulletPatternKind.STRAIGHT_DOWN)
def _pattern_straight_down(
    state: "GameState",
    shooter_pos: "Position",
    config: BulletPatternConfig,
    pattern_state: PatternState | None,
) -> List[Vector2]:
    """直下：向下发射"""
    return [Vector2(0, config.bullet_speed)]


@bullet_pattern_registry.register(BulletPatternKind.N_WAY)
def _pattern_n_way(
    state: "GameState",
    shooter_pos: "Position",
    config: BulletPatternConfig,
    pattern_state: PatternState | None,
) -> List[Vector2]:
    """
    N-Way 扇形弹：
    - 以自机狙方向为中心
    - 展开 spread_deg 角度
    - 发射 count 颗子弹
    """
    from .components import Position as Pos

    # 计算基准方向（朝向玩家或直下）
    base_angle = 90.0  # 默认直下（90度）
    if state.player:
        player_pos = state.player.get(Pos)
        if player_pos:
            dx = player_pos.x - shooter_pos.x
            dy = player_pos.y - shooter_pos.y
            if dx * dx + dy * dy > 1e-9:
                base_angle = math.degrees(math.atan2(dy, dx))

    velocities: List[Vector2] = []
    count = max(1, config.count)

    if count == 1:
        rad = math.radians(base_angle)
        velocities.append(Vector2(
            math.cos(rad) * config.bullet_speed,
            math.sin(rad) * config.bullet_speed,
        ))
    else:
        half_spread = config.spread_deg / 2.0
        for i in range(count):
            t = i / (count - 1)  # 0.0 ~ 1.0
            angle = base_angle - half_spread + config.spread_deg * t
            rad = math.radians(angle)
            velocities.append(Vector2(
                math.cos(rad) * config.bullet_speed,
                math.sin(rad) * config.bullet_speed,
            ))

    return velocities


@bullet_pattern_registry.register(BulletPatternKind.RING)
def _pattern_ring(
    state: "GameState",
    shooter_pos: "Position",
    config: BulletPatternConfig,
    pattern_state: PatternState | None,
) -> List[Vector2]:
    """
    环形弹：
    - 从 start_angle_deg 开始
    - 均匀分布 count 颗子弹（360度）
    """
    velocities: List[Vector2] = []
    count = max(1, config.count)
    angle_step = 360.0 / count

    for i in range(count):
        angle = config.start_angle_deg + angle_step * i
        rad = math.radians(angle)
        velocities.append(Vector2(
            math.cos(rad) * config.bullet_speed,
            math.sin(rad) * config.bullet_speed,
        ))

    return velocities


@bullet_pattern_registry.register(BulletPatternKind.SPIRAL)
def _pattern_spiral(
    state: "GameState",
    shooter_pos: "Position",
    config: BulletPatternConfig,
    pattern_state: PatternState | None,
) -> List[Vector2]:
    """
    螺旋弹：
    - 每次发射 count 颗环形弹
    - 每次发射后角度递增 spin_speed_deg（需要 PatternState）
    """
    velocities: List[Vector2] = []
    count = max(1, config.count)
    angle_step = 360.0 / count

    # 获取当前旋转角度
    current = config.start_angle_deg
    if pattern_state:
        current = pattern_state.current_angle

    for i in range(count):
        angle = current + angle_step * i
        rad = math.radians(angle)
        velocities.append(Vector2(
            math.cos(rad) * config.bullet_speed,
            math.sin(rad) * config.bullet_speed,
        ))

    # 更新状态（如果有）
    if pattern_state:
        pattern_state.current_angle += config.spin_speed_deg

    return velocities
