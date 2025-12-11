"""
玩家射击模式系统
提供可扩展的玩家弹发射模式，使用注册表实现开闭原则。
模式参照敌人弹幕系统 (bullet_patterns.py)。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, List, Tuple

from pygame.math import Vector2

from .registry import Registry
from .components import PlayerBulletKind

if TYPE_CHECKING:
    from .game_state import GameState
    from .components import Position, FocusState


class PlayerShotPatternKind(Enum):
    """玩家射击模式类型"""
    SPREAD = auto()      # 扩散弹（角度偏移）
    STRAIGHT = auto()    # 直射弹（水平位置偏移）
    HOMING = auto()      # 追踪弹（预留）


@dataclass
class PlayerShotPatternConfig:
    """
    玩家射击模式配置

    Attributes:
        kind: 射击模式类型
        cooldown: 射击冷却时间
        bullet_speed: 子弹速度
        damage: 伤害值
        
        # 扩散模式参数
        angles_spread: 展开模式的角度列表
        angles_focus: 聚焦模式的角度列表
        
        # 直射模式参数
        offsets_spread: 展开模式的水平偏移列表
        offsets_focus: 聚焦模式的水平偏移列表
        
        # 增强模式参数
        enhanced_damage_multiplier: 增强伤害倍率
        enhanced_speed_multiplier: 增强弹速倍率
        angles_spread_enhanced: 增强展开角度
        angles_focus_enhanced: 增强聚焦角度
        offsets_spread_enhanced: 增强展开偏移
        offsets_focus_enhanced: 增强聚焦偏移
    """
    kind: PlayerShotPatternKind = PlayerShotPatternKind.SPREAD
    cooldown: float = 0.08
    bullet_speed: float = 520.0
    damage: int = 1
    
    # 扩散模式参数（SPREAD）
    angles_spread: List[float] = field(default_factory=lambda: [-10.0, 0.0, 10.0])
    angles_focus: List[float] = field(default_factory=lambda: [-3.0, 0.0, 3.0])
    
    # 直射模式参数（STRAIGHT）
    offsets_spread: List[float] = field(default_factory=lambda: [-16.0, -8.0, 0.0, 8.0, 16.0])
    offsets_focus: List[float] = field(default_factory=lambda: [-8.0, 0.0, 8.0])
    
    # 增强模式参数
    enhanced_damage_multiplier: float = 1.5
    enhanced_speed_multiplier: float = 1.2
    angles_spread_enhanced: List[float] = field(default_factory=lambda: [-15.0, -7.5, 0.0, 7.5, 15.0])
    angles_focus_enhanced: List[float] = field(default_factory=lambda: [-4.0, -2.0, 0.0, 2.0, 4.0])
    offsets_spread_enhanced: List[float] = field(default_factory=lambda: [-24.0, -12.0, 0.0, 12.0, 24.0])
    offsets_focus_enhanced: List[float] = field(default_factory=lambda: [-12.0, -6.0, 0.0, 6.0, 12.0])


# 玩家射击模式注册表
# 返回值类型: List[Tuple[float, float, Vector2]] 表示 (x_offset, y_offset, velocity)
player_shot_pattern_registry: Registry[PlayerShotPatternKind] = Registry("player_shot_pattern")


def execute_player_shot(
    state: "GameState",
    shooter_x: float,
    shooter_y: float,
    config: PlayerShotPatternConfig,
    is_focusing: bool = False,
    is_enhanced: bool = False,
) -> List[Tuple[float, float, Vector2, int, PlayerBulletKind]]:
    """
    执行玩家射击模式，返回要生成的子弹列表。

    Args:
        state: 游戏状态
        shooter_x: 发射者 X 坐标
        shooter_y: 发射者 Y 坐标
        config: 射击配置
        is_focusing: 是否聚焦状态
        is_enhanced: 是否增强状态

    Returns:
        List of (x, y, velocity, damage, kind) 元组
    """
    handler = player_shot_pattern_registry.get(config.kind)
    if handler:
        return handler(state, shooter_x, shooter_y, config, is_focusing, is_enhanced)
    # 默认使用扩散模式
    return _pattern_spread(state, shooter_x, shooter_y, config, is_focusing, is_enhanced)


# ========== 射击模式实现 ==========

@player_shot_pattern_registry.register(PlayerShotPatternKind.SPREAD)
def _pattern_spread(
    state: "GameState",
    x: float,
    y: float,
    config: PlayerShotPatternConfig,
    is_focusing: bool,
    is_enhanced: bool,
) -> List[Tuple[float, float, Vector2, int, PlayerBulletKind]]:
    """
    扩散弹模式：根据角度列表生成多发子弹。
    """
    # 选择角度列表
    if is_enhanced:
        angles = config.angles_focus_enhanced if is_focusing else config.angles_spread_enhanced
    else:
        angles = config.angles_focus if is_focusing else config.angles_spread
    
    # 计算伤害和速度
    if is_enhanced:
        damage = int(config.damage * config.enhanced_damage_multiplier)
        speed = config.bullet_speed * config.enhanced_speed_multiplier
        kind = PlayerBulletKind.MAIN_ENHANCED
    else:
        damage = config.damage
        speed = config.bullet_speed
        kind = PlayerBulletKind.MAIN_NORMAL
    
    results = []
    for angle_deg in angles:
        rad = math.radians(angle_deg - 90)  # -90 使 0 度指向正上方
        vel = Vector2(math.cos(rad) * speed, math.sin(rad) * speed)
        results.append((x, y, vel, damage, kind))
    
    return results


@player_shot_pattern_registry.register(PlayerShotPatternKind.STRAIGHT)
def _pattern_straight(
    state: "GameState",
    x: float,
    y: float,
    config: PlayerShotPatternConfig,
    is_focusing: bool,
    is_enhanced: bool,
) -> List[Tuple[float, float, Vector2, int, PlayerBulletKind]]:
    """
    直射弹模式：根据水平偏移列表生成多发平行子弹。
    """
    # 选择偏移列表
    if is_enhanced:
        offsets = config.offsets_focus_enhanced if is_focusing else config.offsets_spread_enhanced
    else:
        offsets = config.offsets_focus if is_focusing else config.offsets_spread
    
    # 计算伤害和速度
    if is_enhanced:
        damage = int(config.damage * config.enhanced_damage_multiplier)
        speed = config.bullet_speed * config.enhanced_speed_multiplier
        kind = PlayerBulletKind.MAIN_ENHANCED
    else:
        damage = config.damage
        speed = config.bullet_speed
        kind = PlayerBulletKind.MAIN_NORMAL
    
    results = []
    vel = Vector2(0, -speed)  # 正上方
    for offset_x in offsets:
        results.append((x + offset_x, y, vel, damage, kind))
    
    return results


@player_shot_pattern_registry.register(PlayerShotPatternKind.HOMING)
def _pattern_homing(
    state: "GameState",
    x: float,
    y: float,
    config: PlayerShotPatternConfig,
    is_focusing: bool,
    is_enhanced: bool,
) -> List[Tuple[float, float, Vector2, int, PlayerBulletKind]]:
    """
    追踪弹模式：预留实现，目前与扩散相同。
    """
    return _pattern_spread(state, x, y, config, is_focusing, is_enhanced)
