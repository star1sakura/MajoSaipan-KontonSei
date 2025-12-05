from __future__ import annotations

"""
角色预设（prefab）系统：
- CharacterId: 可选自机枚举
- character_registry: 通过装饰器注册预设
- get_character_preset / get_all_characters: 查询接口
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List
import copy

from ..registry import Registry
from ..components import ShotConfig, BombConfigData
from ..bomb_handlers import BombType


class CharacterId(Enum):
    """角色 ID 枚举"""
    REIMU_A = auto()
    MARISA_A = auto()


@dataclass
class CharacterPreset:
    """
    角色预设数据类：包含角色的所有配置信息。
    """
    name: str           # 角色名称
    description: str    # 角色描述

    speed_normal: float         # 普通移动速度
    speed_focus: float          # 低速移动速度
    collider_radius: float      # 碰撞体半径

    shot: ShotConfig            # 射击配置
    bomb: BombConfigData        # 炸弹配置

    initial_lives: int = 3              # 初始残机
    initial_bombs: int = 3              # 初始炸弹
    max_lives: int = 8                  # 最大残机
    max_bombs: int = 8                  # 最大炸弹
    max_power: float = 4.0              # 最大火力
    deathbomb_window: float = 0.1       # 死亡炸弹窗口时间

    spawn_offset_y: float = 80.0            # 出生点距底部偏移
    bullet_spawn_offset_y: float = 16.0     # 子弹出生点偏移

    sprite_name: str = "player_default"     # 精灵图名称
    sprite_offset_x: int = -16              # 精灵图 X 偏移
    sprite_offset_y: int = -16              # 精灵图 Y 偏移


character_registry: Registry[CharacterId] = Registry("character")


def get_character_preset(character_id: CharacterId) -> Optional[CharacterPreset]:
    """
    获取角色预设。
    返回深拷贝以避免共享可变列表。
    """
    factory = character_registry.get(character_id)
    if not factory:
        return None
    return copy.deepcopy(factory())


def get_all_characters() -> List[CharacterPreset]:
    """获取所有已注册的角色预设列表。"""
    out: List[CharacterPreset] = []
    for cid in CharacterId:
        preset = get_character_preset(cid)
        if preset:
            out.append(preset)
    return out


# ========== 预设定义 ==========

@character_registry.register(CharacterId.REIMU_A)
def _reimu_a() -> CharacterPreset:
    """博丽灵梦 A 型预设：广角扩散弹 + 圆形炸弹"""
    return CharacterPreset(
        name="博丽灵梦",
        description="梦想封印风，广角扩散弹 + 圆形炸弹",
        speed_normal=220.0,
        speed_focus=120.0,
        collider_radius=3.0,
        shot=ShotConfig(
            cooldown=0.08,
            bullet_speed=520.0,
            damage=1,
            angles_spread=[-20.0, -10.0, 0.0, 10.0, 20.0],
            angles_focus=[-5.0, 0.0, 5.0],
            bullet_sprite="player_bullet_basic",
        ),
        bomb=BombConfigData(
            bomb_type=BombType.CIRCLE,
            duration=0.8,
            invincible_time=2.0,
            radius=96.0,
            effect_sprite="bomb_field",
        ),
        sprite_name="player_reimu",
        sprite_offset_x=-16,
        sprite_offset_y=-16,
    )


@character_registry.register(CharacterId.MARISA_A)
def _marisa_a() -> CharacterPreset:
    """雾雨魔理沙 A 型预设：窄角直射 + 光束炸弹"""
    return CharacterPreset(
        name="雾雨魔理沙",
        description="恋符高火力，窄角直射 + 光束炸弹",
        speed_normal=240.0,
        speed_focus=130.0,
        collider_radius=3.0,
        shot=ShotConfig(
            cooldown=0.07,
            bullet_speed=560.0,
            damage=2,
            angles_spread=[-8.0, 0.0, 8.0],
            angles_focus=[-2.0, 0.0, 2.0],
            bullet_sprite="player_bullet_missile",
        ),
        bomb=BombConfigData(
            bomb_type=BombType.BEAM,
            duration=1.0,
            invincible_time=2.5,
            radius=96.0,
            beam_width=64.0,
            beam_length=600.0,
            effect_sprite="bomb_beam",
        ),
        sprite_name="player_marisa",
        sprite_offset_x=-16,
        sprite_offset_y=-16,
    )


__all__ = [
    "CharacterId",
    "CharacterPreset",
    "character_registry",
    "get_character_preset",
    "get_all_characters",
]
