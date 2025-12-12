from __future__ import annotations

from ..game_state import GameState, spawn_enemy_bullet
from ..components import Position, EnemyShootingV2, EnemyTag
from ..bullet_patterns import execute_pattern, BulletPatternConfig, PatternState, ShotData
from ..delayed_bullet import DelayedBulletQueue, PendingShotData
from ..pattern_combinators import (
    StaggerConfig,
    RepeatConfig,
    SequenceConfig,
    execute_stagger,
    execute_repeat,
    execute_sequence,
)

from typing import List


def enemy_shoot_system(state: GameState, dt: float) -> None:
    """
    敌弹系统：使用 EnemyShootingV2 + BulletPatternConfig 支持丰富弹幕模式。
    支持 ShotData.delay：delay > 0 的子弹会进入延迟队列。
    支持组合器配置：StaggerConfig、RepeatConfig、SequenceConfig。
    """
    for actor in state.actors:
        if not actor.has(EnemyTag):
            continue

        pos = actor.get(Position)
        if not pos:
            continue

        cfg = actor.get(EnemyShootingV2)
        if not cfg:
            continue

        cfg.timer -= dt
        if cfg.timer > 0.0:
            continue

        cfg.timer = cfg.cooldown

        pattern_state: PatternState | None = cfg.state
        shots: List[ShotData] = []

        # 根据 pattern 类型执行不同的处理
        pattern = cfg.pattern
        if isinstance(pattern, StaggerConfig):
            shots = execute_stagger(state, pos, pattern, pattern_state)
        elif isinstance(pattern, RepeatConfig):
            shots = execute_repeat(state, pos, pattern, pattern_state)
        elif isinstance(pattern, SequenceConfig):
            shots = execute_sequence(state, pos, pattern, pattern_state)
        elif isinstance(pattern, BulletPatternConfig):
            shots = execute_pattern(state, pos, pattern, pattern_state)
        else:
            # 默认作为 BulletPatternConfig 处理
            shots = execute_pattern(state, pos, pattern, pattern_state)

        # 获取伤害值（从基础 pattern 或组合器中提取）
        damage = _get_damage(pattern)

        # 处理所有 ShotData：立即发射或加入队列
        for shot in shots:
            spawn_x = pos.x + shot.offset.x
            spawn_y = pos.y + shot.offset.y

            if shot.delay <= 0 and not shot.motion_phases:
                # 立即发射（无运动阶段）
                spawn_enemy_bullet(
                    state,
                    x=spawn_x,
                    y=spawn_y,
                    velocity=shot.velocity,
                    damage=damage,
                )
            elif shot.delay <= 0 and shot.motion_phases:
                # 立即发射但有运动阶段，需要附加 BulletMotion 组件
                from ..components import BulletMotion
                bullet = spawn_enemy_bullet(
                    state,
                    x=spawn_x,
                    y=spawn_y,
                    velocity=shot.velocity,
                    damage=damage,
                )
                bullet.add(BulletMotion(phases=list(shot.motion_phases)))
            else:
                # 加入延迟队列
                queue = actor.get(DelayedBulletQueue)
                if not queue:
                    queue = DelayedBulletQueue()
                    actor.add(queue)
                
                queue.pending.append(PendingShotData(
                    delay=shot.delay,
                    offset_x=shot.offset.x,  # 存储偏移，不是绝对坐标
                    offset_y=shot.offset.y,
                    velocity=shot.velocity,
                    damage=damage,
                    motion_phases=shot.motion_phases,
                ))


def _get_damage(pattern: object) -> int:
    """从 pattern 配置中提取伤害值"""
    if isinstance(pattern, StaggerConfig):
        return pattern.base_pattern.damage
    elif isinstance(pattern, RepeatConfig):
        return pattern.base_pattern.damage
    elif isinstance(pattern, SequenceConfig):
        if pattern.patterns:
            return pattern.patterns[0].damage
        return 1
    elif isinstance(pattern, BulletPatternConfig):
        return pattern.damage
    return 1
