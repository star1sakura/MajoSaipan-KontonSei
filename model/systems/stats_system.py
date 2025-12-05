from __future__ import annotations

from ..game_state import GameState
from ..components import EnemyTag, EnemyBulletTag, PlayerBulletTag, ItemTag


def stats_system(state: GameState) -> None:
    """
    每帧统计各类实体数量。
    职责：遍历所有实体并更新 GameState.entity_stats，
    供调试信息和 HUD 显示使用。
    """
    stats = state.entity_stats
    stats.total = len(state.actors)
    stats.enemies = 0
    stats.enemy_bullets = 0
    stats.player_bullets = 0
    stats.items = 0

    for actor in state.actors:
        if actor.has(EnemyTag):
            stats.enemies += 1
        if actor.has(EnemyBulletTag):
            stats.enemy_bullets += 1
        if actor.has(PlayerBulletTag):
            stats.player_bullets += 1
        if actor.has(ItemTag):
            stats.items += 1
