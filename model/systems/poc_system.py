from __future__ import annotations

from ..game_state import GameState
from ..components import Position, PlayerPower
from ..game_config import CollectConfig


def poc_system(state: GameState) -> None:
    """
    负责计算当前帧 PoC 是否生效：
    - 基于玩家位置和配置中的 poc_line_ratio
    - 结果写入 state.poc_active
    - 控制层只需要按顺序调用本系统，不需要知道具体规则
    """
    cfg: CollectConfig = state.get_resource(CollectConfig)  # type: ignore

    player = state.get_player()
    if not player:
        state.poc_active = False
        return
    pos = player.get(Position)
    if not pos:
        state.poc_active = False
        return

    # 使用 GameState 的 height 和配置的比例计算 PoC 线位置
    poc_line_y = state.height * cfg.poc_line_ratio

    active = pos.y <= poc_line_y

    # 如果以后想做“满 Power 常驻 PoC”，可以在这里加：
    power = player.get(PlayerPower)
    if power and power.power >= power.max_power:
        # 例如：满 Power 一定激活 PoC
        # active = True
        # 或者你想要“满 Power 无视高度”可以直接：
        # state.poc_active = True; return
        pass

    state.poc_active = active
