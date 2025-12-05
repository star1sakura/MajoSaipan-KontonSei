from __future__ import annotations

from typing import List

from ..game_state import GameState
from ..components import Lifetime


def lifetime_system(state: GameState, dt: float) -> None:
    """
    生命周期系统：
    - 带 Lifetime 的实体 time_left -= dt
    - time_left <= 0 的实体删除
    """
    to_remove_indices: List[int] = []

    for idx, actor in enumerate(state.actors):
        life = actor.get(Lifetime)
        if not life:
            continue

        life.time_left -= dt
        if life.time_left <= 0.0:
            to_remove_indices.append(idx)

    for idx in reversed(to_remove_indices):
        actor = state.actors[idx]
        state.remove_actor(actor)
