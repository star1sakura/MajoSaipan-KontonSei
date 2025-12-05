from __future__ import annotations

from typing import Set

from ..game_state import GameState
from ..actor import Actor
from ..components import Health, EnemyJustDied
from ..collision_events import (
    CollisionEvents,
    BombHitEnemy,
    BombClearedEnemyBullet,
)


def bomb_hit_system(state: GameState, dt: float) -> None:
    """
    订阅 Bomb 相关碰撞事件：清弹与炸敌。
    """
    events: CollisionEvents = state.collision_events
    to_remove: Set[Actor] = set()

    for ev in events.bomb_clears_enemy_bullet:
        to_remove.add(ev.bullet)

    for ev in events.bomb_hits_enemy:
        _apply_bomb_hits_enemy(ev)

    for actor in to_remove:
        state.remove_actor(actor)


def _apply_bomb_hits_enemy(ev: BombHitEnemy) -> None:
    enemy = ev.enemy
    health = enemy.get(Health)
    if not health:
        return

    health.hp = 0

    death = enemy.get(EnemyJustDied)
    if not death:
        enemy.add(EnemyJustDied(by_player_bullet=False))
