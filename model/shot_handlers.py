from __future__ import annotations

from enum import Enum, auto
from typing import Callable, Optional, TYPE_CHECKING

from pygame.math import Vector2

from .registry import Registry
from .components import ShotConfig, ShotOriginOffset, FocusState

if TYPE_CHECKING:
    from .game_state import GameState


class ShotKind(Enum):
    """射击类型枚举"""
    SPREAD = auto()   # 扩散弹
    MISSILE = auto()  # 导弹（目前与扩散弹相同）


shot_registry: Registry[ShotKind] = Registry("player_shot")


def dispatch_player_shot(
    state: GameState,
    shot_cfg: ShotConfig,
    pos,
    shot_origin: Optional[ShotOriginOffset],
    focus_state: FocusState,
) -> None:
    """分发玩家射击行为。"""
    handler: Optional[Callable] = shot_registry.get(shot_cfg.shot_type)
    if handler:
        handler(state, shot_cfg, pos, shot_origin, focus_state)
    else:
        _shot_spread(state, shot_cfg, pos, shot_origin, focus_state)


@shot_registry.register(ShotKind.SPREAD)
def _shot_spread(
    state,
    cfg: ShotConfig,
    pos,
    shot_origin: Optional[ShotOriginOffset],
    focus_state: FocusState,
) -> None:
    """扩散弹射击：根据是否聚焦选择不同角度。"""
    from .game_state import spawn_player_bullet
    angles = cfg.angles_focus if focus_state.is_focusing else cfg.angles_spread
    offset = shot_origin.bullet_spawn_offset_y if shot_origin else 16.0
    y = pos.y - offset
    for ang in angles:
        spawn_player_bullet(
            state,
            x=pos.x,
            y=y,
            damage=cfg.damage,
            speed=cfg.bullet_speed,
            angle_deg=ang,
        )


@shot_registry.register(ShotKind.MISSILE)
def _shot_missile(
    state,
    cfg: ShotConfig,
    pos,
    shot_origin: Optional[ShotOriginOffset],
    focus_state: FocusState,
) -> None:
    """导弹射击：目前与扩散弹相同，以后可扩展。"""
    _shot_spread(state, cfg, pos, shot_origin, focus_state)
