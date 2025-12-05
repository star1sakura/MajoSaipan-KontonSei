from __future__ import annotations

from ..game_state import GameState
from ..components import (
    PlayerGraze,
    PlayerScore,
    BulletGrazeState,
)
from ..game_config import GrazeConfig
from ..collision_events import CollisionEvents


def graze_system(state: GameState, dt: float) -> None:
    """
    擦弹系统：
    - 每颗敌弹只擦一次；
    - 擦到后玩家计数 +1，并获得固定得分。
    """
    player = state.get_player()
    if not player:
        return
    p_graze = player.get(PlayerGraze)
    p_score = player.get(PlayerScore)
    if not (p_graze and p_score):
        return

    events: CollisionEvents = state.collision_events
    cfg: GrazeConfig = state.get_resource(GrazeConfig)  # type: ignore
    score_bonus = cfg.score_per_graze if cfg else 0

    for ev in events.player_graze_enemy_bullet:
        bullet = ev.bullet
        graze_state = bullet.get(BulletGrazeState)
        if not graze_state:
            continue

        if graze_state.grazed:
            continue

        graze_state.grazed = True
        p_graze.count += 1
        p_score.score += score_bonus
