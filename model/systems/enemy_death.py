from __future__ import annotations

import random
from pygame.math import Vector2

from ..game_state import GameState, spawn_item
from ..components import (
    Position,
    EnemyTag,
    EnemyJustDied,
    EnemyDropConfig,
    ItemType,
)


def enemy_death_system(state: GameState, dt: float) -> None:
    """
    敌人死亡统一处理系统：
    - 查找所有有 EnemyTag + EnemyJustDied 的实体
    - 执行：
        * 掉落道具（根据 EnemyDropConfig）
        * 加分（以后可以加）
        * 清理相关状态
        * 从 GameState 移除敌人实体
    """
    # 用一个列表收集要删的敌人，避免遍历时修改列表
    to_remove = []

    for actor in state.actors:
        if not actor.get(EnemyTag):
            continue

        death = actor.get(EnemyJustDied)
        if not death:
            continue

        pos = actor.get(Position)
        drop = actor.get(EnemyDropConfig)

        # 1) 掉落道具
        if pos and drop:
            _spawn_drops_for_enemy(state, pos.x, pos.y, drop)

        # 2) （以后：给玩家加分、连击、统计这种）

        # 3) 标记删除
        to_remove.append(actor)

    # 真正删除
    for actor in to_remove:
        state.remove_actor(actor)


def _spawn_drops_for_enemy(
    state: GameState,
    cx: float,
    cy: float,
    drop: EnemyDropConfig,
) -> None:
    """
    具体的“根据 DropConfig 生成道具”逻辑，完全在系统里，不放 GameState。
    """
    r = drop.scatter_radius

    # 掉 Power
    for _ in range(drop.power_count):
        offset_x = random.uniform(-r, r)
        offset_y = random.uniform(-r, r)
        spawn_item(
            state,
            x=cx + offset_x,
            y=cy + offset_y,
            item_type=ItemType.POWER,
            value=1,
        )

    # 掉 Point
    for _ in range(drop.point_count):
        offset_x = random.uniform(-r, r)
        offset_y = random.uniform(-r, r)
        spawn_item(
            state,
            x=cx + offset_x,
            y=cy + offset_y,
            item_type=ItemType.POINT,
            value=1,
        )
