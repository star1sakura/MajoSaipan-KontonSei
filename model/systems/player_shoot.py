from __future__ import annotations

from ..game_state import GameState, spawn_player_bullet_with_velocity
from ..actor import Actor
from ..components import (
    Position,
    FocusState,
    ShotConfig,
    ShotOriginOffset,
    InputState,
    OptionConfig,
    OptionState,
    GrazeEnergy,
    PlayerShotPattern,
)
from ..game_config import PlayerConfig
from ..option_shot_handlers import dispatch_option_shot
from ..player_shot_patterns import PlayerShotPatternConfig, execute_player_shot


def player_shoot_system(state: GameState, dt: float) -> None:
    """
    玩家射击系统：
    - 优先使用新版 PlayerShotPattern 组件
    - 向后兼容旧版 ShotConfig
    """
    player = state.get_player()
    if not player:
        return

    pos = player.get(Position)
    focus_state = player.get(FocusState)
    shot_origin = player.get(ShotOriginOffset)
    graze_energy = player.get(GrazeEnergy)
    inp = player.get(InputState)

    if not (pos and focus_state and inp):
        return

    # 判断是否处于增强状态
    is_enhanced = graze_energy is not None and graze_energy.is_enhanced
    is_focusing = focus_state.is_focusing

    # 优先使用新版 PlayerShotPattern
    shot_pattern = player.get(PlayerShotPattern)
    if shot_pattern:
        _fire_with_pattern(state, player, pos, shot_pattern, shot_origin, is_focusing, is_enhanced, inp, dt)
    else:
        # 向后兼容：使用旧版 ShotConfig
        _fire_legacy(state, player, pos, shot_origin, focus_state, graze_energy, inp, dt)


def _fire_with_pattern(
    state: GameState,
    player: Actor,
    pos: Position,
    shot_pattern: PlayerShotPattern,
    shot_origin: ShotOriginOffset,
    is_focusing: bool,
    is_enhanced: bool,
    inp: InputState,
    dt: float,
) -> None:
    """使用新版 PlayerShotPattern 射击"""
    config: PlayerShotPatternConfig = shot_pattern.pattern

    # 冷却计时
    shot_pattern.timer = max(0.0, shot_pattern.timer - dt)
    if not inp.shoot or shot_pattern.timer > 0.0:
        return

    # 计算子弹生成位置
    offset = shot_origin.bullet_spawn_offset_y if shot_origin else 16.0
    spawn_y = pos.y - offset

    # 执行射击模式
    bullets = execute_player_shot(state, pos.x, spawn_y, config, is_focusing, is_enhanced)

    # 生成所有子弹
    for (x, y, vel, damage, kind) in bullets:
        spawn_player_bullet_with_velocity(state, x, y, vel, damage, kind)

    # 重置冷却
    shot_pattern.timer = config.cooldown

    # 子机射击（使用新配置）
    _fire_options_new(state, player, config, is_focusing, is_enhanced)


def _fire_options_new(
    state: GameState,
    player: Actor,
    shot_config: PlayerShotPatternConfig,
    is_focusing: bool,
    is_enhanced: bool,
) -> None:
    """子机射击（新版，使用 PlayerShotPatternConfig）"""
    option_state = player.get(OptionState)
    option_cfg = player.get(OptionConfig)

    if not (option_state and option_cfg):
        return

    # 计算增强伤害倍率
    damage_multiplier = shot_config.enhanced_damage_multiplier if is_enhanced else 1.0

    # 为每个激活的子机分发射击
    for i in range(option_state.active_count):
        if i >= len(option_state.current_positions):
            continue

        opt_pos = option_state.current_positions[i]
        # 使用旧版子机射击分发（子机射击逻辑独立）
        dispatch_option_shot(
            state=state,
            option_pos=(opt_pos[0], opt_pos[1]),
            option_index=i,
            option_cfg=option_cfg,
            shot_cfg=None,  # 不再需要旧版 ShotConfig
            is_focusing=is_focusing,
            is_enhanced=is_enhanced,
            damage_multiplier=damage_multiplier,
        )


def _fire_legacy(
    state: GameState,
    player: Actor,
    pos: Position,
    shot_origin: ShotOriginOffset,
    focus_state: FocusState,
    graze_energy: GrazeEnergy,
    inp: InputState,
    dt: float,
) -> None:
    """向后兼容：使用旧版 ShotConfig"""
    from ..shot_handlers import dispatch_player_shot, dispatch_enhanced_player_shot
    from ..character import EnhancedShotConfig
    from ..components import Shooting

    shooting = player.get(Shooting)
    shot_cfg = player.get(ShotConfig)
    enhanced_shot_cfg = player.get(EnhancedShotConfig)

    if not (shooting and shot_cfg):
        return

    # 冷却计时
    shooting.timer = max(0.0, shooting.timer - dt)
    if not inp.shoot or shooting.timer > 0.0:
        return

    is_enhanced = graze_energy is not None and graze_energy.is_enhanced

    # 主机射击
    if is_enhanced and enhanced_shot_cfg:
        dispatch_enhanced_player_shot(state, shot_cfg, enhanced_shot_cfg, pos, shot_origin, focus_state)
    else:
        dispatch_player_shot(state, shot_cfg, pos, shot_origin, focus_state)

    # 子机射击
    option_state = player.get(OptionState)
    option_cfg = player.get(OptionConfig)
    if option_state and option_cfg:
        is_focusing = focus_state.is_focusing if focus_state else False
        damage_multiplier = enhanced_shot_cfg.option_damage_multiplier if (is_enhanced and enhanced_shot_cfg) else 1.0

        for i in range(option_state.active_count):
            if i >= len(option_state.current_positions):
                continue
            opt_pos = option_state.current_positions[i]
            dispatch_option_shot(
                state=state,
                option_pos=(opt_pos[0], opt_pos[1]),
                option_index=i,
                option_cfg=option_cfg,
                shot_cfg=shot_cfg,
                is_focusing=is_focusing,
                is_enhanced=is_enhanced,
                damage_multiplier=damage_multiplier,
            )

    shooting.timer = shot_cfg.cooldown
