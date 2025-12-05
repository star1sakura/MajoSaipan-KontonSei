from __future__ import annotations

from ..game_state import GameState
from ..components import FocusState, Collider, RenderHint
from ..game_config import GrazeConfig


def render_hint_system(state: GameState) -> None:
    """
    为所有玩家更新 RenderHint，让视图层只需读取 RenderHint。
    """
    players = state.get_players()
    if not players:
        return

    gcfg: GrazeConfig = state.get_resource(GrazeConfig)  # type: ignore
    extra = gcfg.extra_radius if gcfg else 0.0

    for player in players:
        focus = player.get(FocusState)
        collider = player.get(Collider)
        hint = player.get(RenderHint)
        if not hint:
            continue

        is_focusing = focus.is_focusing if focus else False
        hint.show_hitbox = is_focusing
        hint.show_graze_field = is_focusing

        if collider and is_focusing:
            hint.graze_field_radius = collider.radius + extra
        else:
            hint.graze_field_radius = 0.0
