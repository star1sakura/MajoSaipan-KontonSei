from __future__ import annotations

from pygame.math import Vector2

from ..game_state import GameState
from ..components import Position, Velocity, MoveStats, FocusState, InputState


def player_move_system(
    state: GameState,
    dt: float,
) -> None:
    """
    玩家移动系统：根据输入和 MoveStats 设置速度。
    """
    player = state.get_player()
    if not player:
        return

    pos = player.get(Position)
    vel = player.get(Velocity)
    stats = player.get(MoveStats)
    focus_state = player.get(FocusState)

    if not (pos and vel and stats and focus_state):
        return

    inp = player.get(InputState)
    if not inp:
        return

    dx = (1 if inp.right else 0) - (1 if inp.left else 0)
    dy = (1 if inp.down else 0) - (1 if inp.up else 0)

    if dx == 0 and dy == 0:
        vel.vec.update(0, 0)
    else:
        direction = Vector2(dx, dy)
        if direction.length_squared() > 0:
            direction = direction.normalize()

        speed = stats.speed_focus if inp.focus else stats.speed_normal
        vel.vec = direction * speed

    focus_state.is_focusing = inp.focus
