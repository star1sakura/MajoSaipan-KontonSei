# model/delayed_bullet.py
"""
延迟子弹队列组件和数据结构。
用于实现 ShotData.delay 功能，让子弹可以延迟发射。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from pygame.math import Vector2

from .components import EnemyBulletKind


@dataclass
class PendingShotData:
    """
    待发射子弹数据。
    
    使用 offset 而非绝对坐标，这样延迟子弹会跟随敌人移动。
    
    Attributes:
        delay: 剩余延迟时间（秒）
        offset_x: 相对发射者的 X 偏移
        offset_y: 相对发射者的 Y 偏移
        velocity: 速度向量
        damage: 伤害值
        bullet_kind: 子弹类型
        motion_phases: 运动阶段序列（可选），用于子弹运动状态机
    """
    delay: float
    offset_x: float  # 相对偏移，不是绝对坐标
    offset_y: float
    velocity: Vector2
    damage: int = 1
    bullet_kind: EnemyBulletKind = EnemyBulletKind.BASIC
    motion_phases: List[object] | None = None  # List[LinearPhase | WaypointPhase | HoverPhase]


@dataclass
class DelayedBulletQueue:
    """
    延迟子弹队列组件。
    挂在敌人 Actor 上，存储待发射的子弹。
    由 delayed_bullet_system 每帧处理。
    """
    pending: List[PendingShotData] = field(default_factory=list)

