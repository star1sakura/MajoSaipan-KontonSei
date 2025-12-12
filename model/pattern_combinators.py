# model/pattern_combinators.py
"""
弹幕时序组合器。
在现有 BulletPatternConfig 基础上添加时序控制：
- stagger: 错峰发射（每颗依次延迟）
- repeat: 重复发射（N轮，可旋转）
- sequence: 序列发射（多个 pattern 链式执行）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from pygame.math import Vector2

from .bullet_patterns import (
    BulletPatternConfig,
    ShotData,
    execute_pattern,
    PatternState,
)

if TYPE_CHECKING:
    from .game_state import GameState
    from .components import Position


# ========== 组合器配置 ==========

@dataclass
class StaggerConfig:
    """
    错峰发射配置。
    每颗子弹依次增加延迟，形成"扫射"效果。
    
    Attributes:
        base_pattern: 基础弹幕配置
        delay_per_bullet: 每颗子弹增加的延迟（秒）
    """
    base_pattern: BulletPatternConfig
    delay_per_bullet: float = 0.05 # 每颗子弹增加的延迟（秒）


@dataclass
class RepeatConfig:
    """
    重复发射配置。
    同一 pattern 重复 N 次，可选每轮旋转。
    
    Attributes:
        base_pattern: 基础弹幕配置
        times: 重复次数
        interval: 每轮间隔（秒）
        rotate_per_repeat: 每轮旋转角度（度）
    """
    base_pattern: BulletPatternConfig
    times: int = 3
    interval: float = 0.2
    rotate_per_repeat: float = 0.0


@dataclass
class SequenceConfig:
    """
    序列发射配置。
    多个 pattern 按顺序执行。
    
    Attributes:
        patterns: pattern 列表
        intervals: 各 pattern 之间的间隔（长度应为 len(patterns)-1）
    """
    patterns: List[BulletPatternConfig] = field(default_factory=list)
    intervals: List[float] = field(default_factory=list)


# ========== 组合器执行函数 ==========

def execute_stagger(
    state: "GameState",
    shooter_pos: "Position",
    config: StaggerConfig,
    pattern_state: PatternState | None = None,
) -> List[ShotData]:
    """
    执行错峰发射。
    
    Returns:
        ShotData 列表，每颗子弹的 delay 依次递增
    """
    base_shots = execute_pattern(state, shooter_pos, config.base_pattern, pattern_state)
    
    result: List[ShotData] = []
    for i, shot in enumerate(base_shots):
        staggered = ShotData(
            velocity=shot.velocity,
            offset=shot.offset,
            delay=shot.delay + i * config.delay_per_bullet,
        )
        result.append(staggered)
    
    return result


def execute_repeat(
    state: "GameState",
    shooter_pos: "Position",
    config: RepeatConfig,
    pattern_state: PatternState | None = None,
) -> List[ShotData]:
    """
    执行重复发射。
    
    Returns:
        ShotData 列表，包含 N 轮 pattern，每轮累积延迟和旋转
    """
    result: List[ShotData] = []
    
    for round_idx in range(config.times):
        # 每轮的累积延迟
        round_delay = round_idx * config.interval
        # 每轮的累积旋转
        round_rotation = round_idx * config.rotate_per_repeat
        
        # 执行基础 pattern
        base_shots = execute_pattern(state, shooter_pos, config.base_pattern, pattern_state)
        
        for shot in base_shots:
            # 旋转速度向量
            rotated_vel = shot.velocity.rotate(round_rotation)
            
            repeated = ShotData(
                velocity=rotated_vel,
                offset=shot.offset,
                delay=shot.delay + round_delay,
            )
            result.append(repeated)
    
    return result


def execute_sequence(
    state: "GameState",
    shooter_pos: "Position",
    config: SequenceConfig,
    pattern_state: PatternState | None = None,
) -> List[ShotData]:
    """
    执行序列发射。
    
    Returns:
        ShotData 列表，多个 pattern 依次执行，累积延迟
    """
    result: List[ShotData] = []
    cumulative_delay = 0.0
    
    for i, pattern in enumerate(config.patterns):
        shots = execute_pattern(state, shooter_pos, pattern, pattern_state)
        
        for shot in shots:
            sequenced = ShotData(
                velocity=shot.velocity,
                offset=shot.offset,
                delay=shot.delay + cumulative_delay,
            )
            result.append(sequenced)
        
        # 添加间隔（最后一个 pattern 不需要）
        if i < len(config.intervals):
            cumulative_delay += config.intervals[i]
    
    return result


# ========== 便捷工厂函数 ==========

def stagger(
    pattern: BulletPatternConfig,
    delay_per_bullet: float = 0.05,
) -> StaggerConfig:
    """创建错峰配置的便捷函数"""
    return StaggerConfig(base_pattern=pattern, delay_per_bullet=delay_per_bullet)


def repeat(
    pattern: BulletPatternConfig,
    times: int = 3,
    interval: float = 0.2,
    rotate: float = 0.0,
) -> RepeatConfig:
    """创建重复配置的便捷函数"""
    return RepeatConfig(
        base_pattern=pattern,
        times=times,
        interval=interval,
        rotate_per_repeat=rotate,
    )


def sequence(
    patterns: List[BulletPatternConfig],
    intervals: List[float],
) -> SequenceConfig:
    """创建序列配置的便捷函数"""
    return SequenceConfig(patterns=patterns, intervals=intervals)
