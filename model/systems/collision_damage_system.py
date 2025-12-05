from __future__ import annotations

from typing import Set

from ..game_state import GameState
from ..actor import Actor
from ..components import (
    Health, Bullet,
    PlayerDamageState,
    EnemyJustDied,
)
from ..collision_events import (
    CollisionEvents,
    PlayerBulletHitEnemy,
    EnemyBulletHitPlayer,
)


def collision_damage_system(state: GameState, dt: float) -> None:
    """
    订阅会造成伤害的碰撞事件，负责扣血、标记死亡以及删除子弹。
    """
    events: CollisionEvents = state.collision_events
    to_remove: Set[Actor] = set()

    for ev in events.player_bullet_hits_enemy:
        _apply_player_bullet_hits_enemy(ev, to_remove)

    for ev in events.enemy_bullet_hits_player:
        _apply_enemy_bullet_hits_player(ev, to_remove)

    for actor in to_remove:
        state.remove_actor(actor)


def _apply_player_bullet_hits_enemy(ev: PlayerBulletHitEnemy,
                                    to_remove: Set[Actor]) -> None:
    bullet = ev.bullet
    enemy = ev.enemy

    bullet_data = bullet.get(Bullet)
    health = enemy.get(Health)
    if not (bullet_data and health):
        return

    health.hp -= bullet_data.damage
    to_remove.add(bullet)

    if health.hp <= 0:
        death = enemy.get(EnemyJustDied)
        if not death:
            enemy.add(EnemyJustDied(by_player_bullet=True))
        else:
            death.by_player_bullet = True


def _apply_enemy_bullet_hits_player(ev: EnemyBulletHitPlayer,
                                    to_remove: Set[Actor]) -> None:
    bullet = ev.bullet
    player = ev.player

    damage_state = player.get(PlayerDamageState)
    if not damage_state:
        to_remove.add(bullet)
        return

    if damage_state.pending_death or damage_state.invincible_timer > 0.0:
        to_remove.add(bullet)
        return

    damage_state.pending_death = True
    # 每次被击中都重置 deathbomb 窗口，让玩家有足够时间反应
    damage_state.deathbomb_timer = damage_state.deathbomb_window

    to_remove.add(bullet)
