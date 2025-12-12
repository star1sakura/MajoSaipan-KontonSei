# model/systems/bullet_motion_system.py
"""
子弹运动状态机系统。
根据 BulletMotion 组件中的当前阶段类型更新子弹速度，
检测阶段完成条件并切换到下一阶段。
"""
from __future__ import annotations

import math

from pygame.math import Vector2

from ..game_state import GameState
from ..components import (
    Position,
    Velocity,
    BulletMotion,
    MotionPhaseKind,
    LinearPhase,
    WaypointPhase,
    HoverPhase,
)


def bullet_motion_system(state: GameState, dt: float) -> None:
    """
    子弹运动状态机系统。
    
    遍历所有带有 BulletMotion 组件的子弹，
    根据当前阶段类型更新速度，检测完成条件并切换阶段。
    """
    for actor in state.actors:
        motion = actor.get(BulletMotion)
        if not motion:
            continue
        
        pos = actor.get(Position)
        vel = actor.get(Velocity)
        if not pos or not vel:
            continue
        
        # 没有阶段则跳过
        if not motion.phases or motion.current_phase >= len(motion.phases):
            continue
        
        phase = motion.phases[motion.current_phase]
        
        if phase.kind == MotionPhaseKind.LINEAR:
            _process_linear_phase(phase, vel)
        elif phase.kind == MotionPhaseKind.WAYPOINT:
            _process_waypoint_phase(phase, pos, vel, motion, dt)
        elif phase.kind == MotionPhaseKind.HOVER:
            _process_hover_phase(phase, vel, motion, dt)


def _process_linear_phase(phase: LinearPhase, vel: Velocity) -> None:
    """
    处理直线运动阶段。
    设置速度为方向向量乘以速度值。
    LinearPhase 不会自动结束，子弹将持续直线飞行。
    """
    # 归一化方向向量
    dir_x = phase.direction_x
    dir_y = phase.direction_y
    length = math.sqrt(dir_x * dir_x + dir_y * dir_y)
    
    if length > 1e-9:
        dir_x /= length
        dir_y /= length
    else:
        # 默认向下
        dir_x = 0.0
        dir_y = 1.0
    
    vel.vec = Vector2(dir_x * phase.speed, dir_y * phase.speed)


def _process_waypoint_phase(
    phase: WaypointPhase,
    pos: Position,
    vel: Velocity,
    motion: BulletMotion,
    dt: float,
) -> None:
    """
    处理路径点运动阶段。
    子弹朝当前路径点移动，到达后切换到下一个路径点。
    所有路径点完成后切换到下一阶段。
    """
    waypoints = phase.waypoints
    
    # 空路径点列表，直接切换到下一阶段
    if not waypoints:
        _advance_phase(motion)
        return
    
    # 当前路径点索引超出范围，切换到下一阶段
    if phase.current_index >= len(waypoints):
        _advance_phase(motion)
        return
    
    # 获取当前目标路径点
    target_x, target_y = waypoints[phase.current_index]
    
    # 计算到目标的方向和距离
    dx = target_x - pos.x
    dy = target_y - pos.y
    distance = math.sqrt(dx * dx + dy * dy)
    
    # 检测是否到达路径点
    if distance <= phase.arrival_threshold:
        # 到达当前路径点，切换到下一个
        phase.current_index += 1
        
        # 检查是否完成所有路径点
        if phase.current_index >= len(waypoints):
            _advance_phase(motion)
            return
        
        # 更新目标为下一个路径点
        target_x, target_y = waypoints[phase.current_index]
        dx = target_x - pos.x
        dy = target_y - pos.y
        distance = math.sqrt(dx * dx + dy * dy)
    
    # 设置朝向目标的速度
    if distance > 1e-9:
        dir_x = dx / distance
        dir_y = dy / distance
        vel.vec = Vector2(dir_x * phase.speed, dir_y * phase.speed)
    else:
        vel.vec = Vector2(0, 0)


def _process_hover_phase(
    phase: HoverPhase,
    vel: Velocity,
    motion: BulletMotion,
    dt: float,
) -> None:
    """
    处理悬停阶段。
    子弹停止移动，持续指定时间后切换到下一阶段。
    """
    # 停止移动
    vel.vec = Vector2(0, 0)
    
    # 更新计时器
    motion.phase_timer += dt
    
    # 检测是否完成悬停
    if motion.phase_timer >= phase.duration:
        _advance_phase(motion)


def _advance_phase(motion: BulletMotion) -> None:
    """
    切换到下一个运动阶段。
    重置阶段计时器。
    """
    motion.current_phase += 1
    motion.phase_timer = 0.0
