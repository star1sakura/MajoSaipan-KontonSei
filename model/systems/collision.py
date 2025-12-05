from __future__ import annotations

from typing import List

from ..game_state import GameState
from ..components import (
    Position,
    Collider,
    PlayerBulletTag,
    EnemyBulletTag,
    PlayerTag,
    EnemyTag,
    BombFieldTag,
    ItemTag,
)
from ..collision_events import (
    CollisionEvents,
    PlayerBulletHitEnemy,
    EnemyBulletHitPlayer,
    BombHitEnemy,
    BombClearedEnemyBullet,
    PlayerPickupItem,
    PlayerGrazeEnemyBullet,
)
from ..game_config import GrazeConfig


def _check_collision(a_pos: Position, a_col: Collider, b_pos: Position, b_col: Collider) -> bool:
    dx = a_pos.x - b_pos.x
    dy = a_pos.y - b_pos.y
    dist_sq = dx * dx + dy * dy
    r_sum = a_col.radius + b_col.radius
    return dist_sq <= r_sum * r_sum


def collision_detection_system(state: GameState) -> None:
    """
    简单的圆形碰撞检测；将命中/擦弹/拾取/炸弹事件填充到 CollisionEvents。
    """
    events: CollisionEvents = state.collision_events
    events.clear()

    gcfg: GrazeConfig = state.get_resource(GrazeConfig)  # type: ignore
    graze_extra = gcfg.extra_radius if gcfg else 0.0

    bullets_enemy: List[tuple] = []
    bullets_player: List[tuple] = []
    players: List[tuple] = []
    enemies: List[tuple] = []
    bombs: List[tuple] = []
    items: List[tuple] = []

    for actor in state.actors:
        pos = actor.get(Position)
        col = actor.get(Collider)
        if not (pos and col):
            continue

        if actor.has(PlayerTag):
            players.append((actor, pos, col))
        elif actor.has(EnemyTag):
            enemies.append((actor, pos, col))
        elif actor.has(PlayerBulletTag):
            bullets_player.append((actor, pos, col))
        elif actor.has(EnemyBulletTag):
            bullets_enemy.append((actor, pos, col))
        elif actor.has(BombFieldTag):
            bombs.append((actor, pos, col))
        elif actor.has(ItemTag):
            items.append((actor, pos, col))

    # 玩家 vs 敌弹（命中和擦弹）
    for p_actor, p_pos, p_col in players:
        graze_col = Collider(radius=p_col.radius + graze_extra, layer=p_col.layer, mask=p_col.mask)
        for b_actor, b_pos, b_col in bullets_enemy:
            if _check_collision(p_pos, p_col, b_pos, b_col):
                events.enemy_bullet_hits_player.append(EnemyBulletHitPlayer(bullet=b_actor, player=p_actor))
            elif graze_extra > 0 and _check_collision(p_pos, graze_col, b_pos, b_col):
                events.player_graze_enemy_bullet.append(PlayerGrazeEnemyBullet(player=p_actor, bullet=b_actor))

    # 玩家子弹 vs 敌人
    for e_actor, e_pos, e_col in enemies:
        for b_actor, b_pos, b_col in bullets_player:
            if _check_collision(e_pos, e_col, b_pos, b_col):
                events.player_bullet_hits_enemy.append(PlayerBulletHitEnemy(bullet=b_actor, enemy=e_actor))

    # 玩家 vs 道具（拾取）
    for p_actor, p_pos, p_col in players:
        for i_actor, i_pos, i_col in items:
            if _check_collision(p_pos, p_col, i_pos, i_col):
                events.player_pickup_item.append(PlayerPickupItem(player=p_actor, item=i_actor))

    # 炸弹场 vs 敌弹和敌人
    for bomb_actor, bomb_pos, bomb_col in bombs:
        for b_actor, b_pos, b_col in bullets_enemy:
            if _check_collision(bomb_pos, bomb_col, b_pos, b_col):
                events.bomb_clears_enemy_bullet.append(BombClearedEnemyBullet(bomb=bomb_actor, bullet=b_actor))
        for e_actor, e_pos, e_col in enemies:
            if _check_collision(bomb_pos, bomb_col, e_pos, e_col):
                events.bomb_hits_enemy.append(BombHitEnemy(bomb=bomb_actor, enemy=e_actor))
