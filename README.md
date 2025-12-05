# Touhou_KontonSei

一个用 pygame 写的东方风格 STG 原型，采用简单的 ECS（Actor + Component + System）架构。

## 运行
- Python 3.10+，安装依赖：`pip install -r requirements.txt`
- 启动：`python main.py`

## 操作
- 方向键：移动
- Shift：低速移动并显示判定点/擦弹圈
- Z：射击
- X：炸弹

## 目录结构
- `main.py`：入口，创建窗口与 `GameController`
- `controller/game_controller.py`：主循环与系统调用顺序
- `model/`：逻辑层
  - `actor.py`：Actor 容器，`add/get/has`
  - `components.py`：所有组件定义（位置/速度/碰撞/玩家状态/道具等）
  - `game_state.py`：世界状态（actors、player、时间、PoC、路径库等）与工厂函数（玩家/敌人/子弹/道具/炸弹）
  - `collision_events.py`：每帧碰撞事件记录
  - `systems/`：全部逻辑系统（移动、碰撞、擦弹、道具、炸弹、关卡时间线等）
  - `stages/`：关卡脚本（时间表、敌人波次）
  - `movement_path.py`：敌人路径库
- `view/`：渲染层（资源加载、HUD、PoC 线、判定点/擦弹圈）

## 核心数据模型（ECS）
- Actor：组件容器。
- Component：在 `model/components.py` 定义，常用：
  - 位置/速度 `Position/Velocity`，重力 `Gravity`
  - 碰撞体 `Collider(layer, mask, radius)`，子弹相关 `Bullet/BulletGrazeState`
  - 玩家状态 `PlayerLife/PlayerBomb/PlayerDamageState/PlayerPower/PlayerScore/PlayerGraze`
  - 射击配置 `Shooting/ShotPattern/FocusState`，敌人射击 `EnemyShooting`
  - 道具 `Item/ItemTag`，掉落配置 `EnemyDropConfig`
  - 标记：`PlayerTag/EnemyTag/PlayerBulletTag/EnemyBulletTag/BombFieldTag/ItemTag`
- GameState：保存 actors、player 引用、世界尺寸、时间帧计数、PoC 状态、收集/擦弹配置、关卡状态、路径库，以及本帧的 `CollisionEvents`。

## 主循环调用序（逻辑 + 渲染）
`controller/game_controller.py` 中每帧：

```text
输入轮询 → 计算 bomb 边沿
玩家移动 player_move_system
玩家射击 player_shoot_system
敌人射击 enemy_shoot_system
PoC 状态 poc_system
重力 gravity_system
道具自动吸 item_autocollect_system
关卡推进 stage_system
位移更新 movement_system
碰撞检测 collision_detection_system → 写入 CollisionEvents
伤害结算 collision_damage_system
bomb 命中 bomb_hit_system
擦弹 graze_system
道具拾取 item_pickup_system
玩家受伤处理 player_damage_system（含死亡炸判断）
bomb 系统事件 bomb_system
敌人死亡处理 enemy_death_system（掉落道具等）
生命周期清理 lifetime_system
渲染 renderer.render
```

### 组件/事件流示意图
```text
[输入/计时] 
   ↓
玩家/敌人射击系统 ——→ 生成子弹（带 Collider/Tag）
   ↓
运动系 movement_system 按 Velocity/Gravity 更新 Position
   ↓
碰撞检测 collision_detection_system
   ├─ 玩家弹 vs 敌人 → PlayerBulletHitEnemy
   ├─ 敌弹 vs 玩家 → EnemyBulletHitPlayer
   ├─ 炸弹圈 vs 敌人/弹 → BombHitEnemy / BombClearedEnemyBullet
   └─ 玩家 vs 道具 → PlayerPickupItem
   ↓ 使用 CollisionEvents
伤害结算 collision_damage_system / bomb_hit_system / graze_system / item_pickup_system
   └─ 可能标记死亡 EnemyJustDied 或更新玩家血量/火力/分数
   ↓
敌人死亡 enemy_death_system：据 EnemyDropConfig 掉落 Item
   ↓
lifetime_system 清理超时或被移除的 Actor
   ↓
renderer 根据 Position/SpriteInfo/HUD 状态绘制
```

## 关卡脚本
- `model/stages/stage1.py`：定义时间轴事件（在 `setup_stage1` 中注册），驱动敌人生成、路径、掉落。
- 主循环里 `stage_system` 依据帧时间触发事件并生成敌人/道具。

## 渲染
- `view/assets.py`：加载素材（占位图可自行替换）。
- `view/renderer.py`：绘制所有带 `SpriteInfo` 的 Actor；绘制 HUD、PoC 线；按住 Shift 显示判定点与擦弹圈。

## 调试提示
- 关掉敌人生成/掉落：修改 `stage1.py` 内的事件表。
- 验证碰撞/拾取：`game_controller.py` 中已有初始掉落道具，可观测 PoC/自动吸/碰撞事件链。

