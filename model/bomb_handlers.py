from __future__ import annotations

from enum import Enum, auto
from typing import Callable, Optional, List, TYPE_CHECKING

from .registry import Registry
from .components import BombConfigData, Position, BombFieldTag, Collider, Lifetime, SpriteInfo, CollisionLayer
from .actor import Actor

if TYPE_CHECKING:
    from .game_state import GameState


class BombType(Enum):
    """炸弹类型枚举"""
    CIRCLE = auto()  # 圆形炸弹
    BEAM = auto()    # 光束炸弹


bomb_registry: Registry[BombType] = Registry("bomb")


def dispatch_bomb(state, player_pos: Position, cfg: BombConfigData) -> List[Actor]:
    """分发炸弹行为，返回创建的炸弹实体列表。"""
    handler: Optional[Callable] = bomb_registry.get(cfg.bomb_type)
    if handler:
        return handler(state, player_pos, cfg)
    return _bomb_circle(state, player_pos, cfg)


@bomb_registry.register(BombType.CIRCLE)
def _bomb_circle(state, player_pos: Position, cfg: BombConfigData) -> List[Actor]:
    """圆形炸弹：以玩家位置为中心生成炸弹场。"""
    from .game_state import spawn_bomb_field
    bomb = spawn_bomb_field(
        state,
        x=player_pos.x,
        y=player_pos.y,
        radius=cfg.radius,
        duration=cfg.duration,
    )
    return [bomb]


@bomb_registry.register(BombType.BEAM)
def _bomb_beam(state, player_pos: Position, cfg: BombConfigData) -> List[Actor]:
    """光束炸弹：向上生成多段光束。"""
    actors: List[Actor] = []
    num_segments = 12
    spacing = cfg.beam_length / num_segments
    radius = cfg.beam_width / 2
    for i in range(num_segments):
        y = player_pos.y - (i + 1) * spacing
        bomb = Actor()
        bomb.add(Position(player_pos.x, y))
        bomb.add(Collider(
            radius=radius,
            layer=CollisionLayer.PLAYER_BULLET,
            mask=CollisionLayer.ENEMY | CollisionLayer.ENEMY_BULLET,
        ))
        bomb.add(BombFieldTag())
        bomb.add(Lifetime(time_left=cfg.duration))
        bomb.add(SpriteInfo(
            name=cfg.effect_sprite,
            offset_x=int(-radius),
            offset_y=int(-radius),
        ))
        state.add_actor(bomb)
        actors.append(bomb)
    return actors
