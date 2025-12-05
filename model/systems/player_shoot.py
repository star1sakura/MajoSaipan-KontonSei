from __future__ import annotations

from ..game_state import GameState
from ..components import (
    Position,
    Shooting,
    FocusState,
    ShotConfig,
    ShotOriginOffset,
    InputState,
)
from ..game_config import PlayerConfig
from ..shot_handlers import dispatch_player_shot


def player_shoot_system(state: GameState, dt: float) -> None:
    """
    玩家射击系统：读取 ShotConfig / ShotOriginOffset / Shooting。
    """
    player = state.get_player()
    if not player:
        return

    pos = player.get(Position)
    shooting = player.get(Shooting)
    focus_state = player.get(FocusState)
    shot_cfg = player.get(ShotConfig)
    shot_origin = player.get(ShotOriginOffset)

    inp = player.get(InputState)

    if not (pos and shooting and focus_state and shot_cfg and inp):
        return

    # 冷却计时
    shooting.timer = max(0.0, shooting.timer - dt)
    if not inp.shoot or shooting.timer > 0.0:
        return

    dispatch_player_shot(state, shot_cfg, pos, shot_origin, focus_state)

    shooting.timer = shot_cfg.cooldown
