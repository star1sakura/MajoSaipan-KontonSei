from __future__ import annotations

from pygame.math import Vector2

from ..game_state import GameState
from ..components import Position, Velocity, ItemTag, Item
from ..game_config import CollectConfig


def item_autocollect_system(state: GameState, dt: float) -> None:
    """
    自动吸道具系统：
    - PoC 线只负责把道具标记为 auto_collect=True
    - 只要道具是 auto_collect=True，就每帧朝玩家当前位置飞
    - 玩家掉回 PoC 线下，道具依然会追着玩家跑，直到被吃掉
    """
    player = state.get_player()
    if not player:
        return

    cfg: CollectConfig = state.get_resource(CollectConfig)  # type: ignore
    magnet_speed = cfg.magnet_speed if cfg else 500.0
    p_pos = player.get(Position)
    if not p_pos:
        return

    poc_active = state.poc_active

    for actor in state.actors:
        if not actor.get(ItemTag):
            continue

        i_pos = actor.get(Position)
        i_vel = actor.get(Velocity)
        item = actor.get(Item)
        if not (i_pos and i_vel and item):
            continue

        # 第 1 步：当这一帧 PoC 激活时，把道具标记为自动吸
        if poc_active:
            item.auto_collect = True

        # 第 2 步：只有 auto_collect=True 的道具才会被吸
        if not item.auto_collect:
            continue

        # 第 3 步：每一帧都朝玩家“当前的位置”飞，
        # 而不是只算触发那一帧的位置
        to_player = Vector2(p_pos.x - i_pos.x, p_pos.y - i_pos.y)
        if to_player.length_squared() == 0:
            continue

        to_player = to_player.normalize() * magnet_speed
        i_vel.vec = to_player
