# model/systems/delayed_bullet_system.py
"""
延迟子弹处理系统。
每帧减少 DelayedBulletQueue 中子弹的延迟时间，
当延迟归零时从敌人当前位置生成子弹实体。
"""
from __future__ import annotations

from ..game_state import GameState, spawn_enemy_bullet
from ..delayed_bullet import DelayedBulletQueue
from ..components import Position


def delayed_bullet_system(state: GameState, dt: float) -> None:
    """
    处理延迟子弹队列。
    
    遍历所有带有 DelayedBulletQueue 组件的 Actor，
    递减每个待发射子弹的延迟时间，
    延迟归零时从 Actor 当前位置发射子弹（跟随移动）。
    """
    for actor in state.actors:
        queue = actor.get(DelayedBulletQueue)
        if not queue:
            continue
        
        # 获取敌人当前位置
        pos = actor.get(Position)
        if not pos:
            # 敌人已死亡或无位置，清空队列
            queue.pending.clear()
            continue
        
        still_pending = []
        for shot in queue.pending:
            shot.delay -= dt
            if shot.delay <= 0:
                # 延迟归零，从敌人当前位置 + 偏移生成子弹
                spawn_enemy_bullet(
                    state,
                    x=pos.x + shot.offset_x,
                    y=pos.y + shot.offset_y,
                    velocity=shot.velocity,
                    damage=shot.damage,
                    bullet_kind=shot.bullet_kind,
                )
            else:
                # 还未到时间，保留在队列中
                still_pending.append(shot)
        
        queue.pending = still_pending

