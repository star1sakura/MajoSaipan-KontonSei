"""
主菜单场景：游戏标题画面和菜单选项。
"""
from __future__ import annotations

import math
import pygame
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view.assets import Assets


class MenuState(Enum):
    """菜单状态"""
    TITLE = auto()
    CHARACTER_SELECT = auto()
    OPTIONS = auto()


class MenuResult(Enum):
    """菜单返回结果"""
    NONE = auto()
    START_GAME = auto()
    EXIT = auto()


class MainMenu:
    """主菜单场景"""

    def __init__(self, screen: pygame.Surface, assets: Assets) -> None:
        self.screen = screen
        self.assets = assets
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 菜单状态
        self.state = MenuState.TITLE
        self.selected_index = 0
        self.time = 0.0
        
        # 菜单选项
        self.menu_items = [
            "开始游戏",
            "退出游戏",
        ]
        
        # 角色选择
        self.character_index = 0
        self.selected_character_id = None
        
        # 字体
        try:
            self.font_title = pygame.font.Font(assets.font_path, 48)
            self.font_subtitle = pygame.font.Font(assets.font_path, 24)
            self.font_menu = pygame.font.Font(assets.font_path, 28)
            self.font_small = pygame.font.Font(assets.font_path, 18)
        except (FileNotFoundError, pygame.error):
            self.font_title = pygame.font.Font(None, 64)
            self.font_subtitle = pygame.font.Font(None, 32)
            self.font_menu = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
        
        # 输入冷却
        self.input_cooldown = 0.0
        
        # 星星粒子背景
        self.stars = self._generate_stars(100)
    
    def _generate_stars(self, count: int) -> list[dict]:
        """生成星星粒子"""
        import random
        stars = []
        for _ in range(count):
            stars.append({
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "speed": random.uniform(20, 80),
                "size": random.randint(1, 3),
                "brightness": random.randint(100, 255),
            })
        return stars
    
    def _update_stars(self, dt: float) -> None:
        """更新星星粒子"""
        for star in self.stars:
            star["y"] += star["speed"] * dt
            if star["y"] > self.height:
                star["y"] = 0
                star["x"] = __import__("random").randint(0, self.width)
    
    def _draw_stars(self) -> None:
        """绘制星星粒子"""
        for star in self.stars:
            brightness = star["brightness"]
            color = (brightness, brightness, brightness)
            pygame.draw.circle(
                self.screen, 
                color, 
                (int(star["x"]), int(star["y"])), 
                star["size"]
            )
    
    def _draw_text_with_shadow(
        self, 
        text: str, 
        font: pygame.font.Font, 
        color: tuple[int, int, int], 
        x: int, 
        y: int,
        center: bool = False,
        shadow_offset: int = 2
    ) -> pygame.Rect:
        """绘制带阴影的文字"""
        shadow_color = (0, 0, 0)
        
        # 阴影
        shadow_surf = font.render(text, True, shadow_color)
        main_surf = font.render(text, True, color)
        
        if center:
            shadow_rect = shadow_surf.get_rect(center=(x + shadow_offset, y + shadow_offset))
            main_rect = main_surf.get_rect(center=(x, y))
        else:
            shadow_rect = shadow_surf.get_rect(topleft=(x + shadow_offset, y + shadow_offset))
            main_rect = main_surf.get_rect(topleft=(x, y))
        
        self.screen.blit(shadow_surf, shadow_rect)
        self.screen.blit(main_surf, main_rect)
        
        return main_rect
    
    def _draw_title_screen(self) -> None:
        """绘制标题画面"""
        # 标题
        title_y = 120
        wave = math.sin(self.time * 2) * 5
        
        # 游戏标题
        self._draw_text_with_shadow(
            "MajoSaipanKontonSei",
            self.font_title,
            (255, 220, 100),
            self.width // 2,
            int(title_y + wave),
            center=True,
            shadow_offset=3
        )
        
        # 副标题
        self._draw_text_with_shadow(
            "~ Chaos Reign ~",
            self.font_subtitle,
            (200, 180, 255),
            self.width // 2,
            title_y + 60,
            center=True
        )
        
        # 菜单选项
        menu_start_y = 300
        menu_spacing = 50
        
        for i, item in enumerate(self.menu_items):
            is_selected = (i == self.selected_index)
            
            # 选中效果
            if is_selected:
                # 闪烁高亮
                alpha = int(180 + 75 * math.sin(self.time * 6))
                color = (255, 255, alpha)
                # 箭头指示器
                arrow_x = self.width // 2 - 100
                arrow_wave = math.sin(self.time * 8) * 5
                self._draw_text_with_shadow(
                    "▶",
                    self.font_menu,
                    (255, 100, 100),
                    int(arrow_x + arrow_wave),
                    menu_start_y + i * menu_spacing,
                    center=True
                )
            else:
                color = (180, 180, 180)
            
            self._draw_text_with_shadow(
                item,
                self.font_menu,
                color,
                self.width // 2,
                menu_start_y + i * menu_spacing,
                center=True
            )
        
        # 底部提示
        hint_y = self.height - 60
        self._draw_text_with_shadow(
            "↑↓ 选择  Z 确认  X 返回",
            self.font_small,
            (150, 150, 150),
            self.width // 2,
            hint_y,
            center=True
        )
        
        # 版权信息
        self._draw_text_with_shadow(
            "© 2024 Touhou KontonSei Project",
            self.font_small,
            (100, 100, 100),
            self.width // 2,
            hint_y + 30,
            center=True
        )
    
    def _draw_character_select(self) -> None:
        """绘制角色选择画面"""
        from model.character import get_all_characters, CharacterId
        
        characters = get_all_characters()
        
        # 标题
        self._draw_text_with_shadow(
            "角色选择",
            self.font_title,
            (255, 200, 150),
            self.width // 2,
            80,
            center=True,
            shadow_offset=3
        )
        
        if not characters:
            self._draw_text_with_shadow(
                "没有可用角色",
                self.font_menu,
                (255, 100, 100),
                self.width // 2,
                self.height // 2,
                center=True
            )
            return
        
        # 角色卡片
        card_width = 200
        card_height = 280
        start_x = (self.width - card_width * len(characters) - 20 * (len(characters) - 1)) // 2
        card_y = 160
        
        for i, preset in enumerate(characters):
            is_selected = (i == self.character_index)
            card_x = start_x + i * (card_width + 20)
            
            # 卡片背景
            if is_selected:
                # 选中卡片发光效果
                glow_alpha = int(100 + 50 * math.sin(self.time * 4))
                glow_surf = pygame.Surface((card_width + 20, card_height + 20), pygame.SRCALPHA)
                pygame.draw.rect(
                    glow_surf, 
                    (255, 200, 100, glow_alpha), 
                    (0, 0, card_width + 20, card_height + 20),
                    border_radius=12
                )
                self.screen.blit(glow_surf, (card_x - 10, card_y - 10))
                
                bg_color = (60, 50, 80)
                border_color = (255, 200, 100)
            else:
                bg_color = (40, 40, 60)
                border_color = (80, 80, 100)
            
            # 卡片主体
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, card_rect, 2, border_radius=8)
            
            # 角色名称
            name_color = (255, 255, 200) if is_selected else (200, 200, 200)
            self._draw_text_with_shadow(
                preset.name,
                self.font_menu,
                name_color,
                card_x + card_width // 2,
                card_y + 30,
                center=True
            )
            
            # 角色描述
            desc_color = (180, 180, 220) if is_selected else (140, 140, 160)
            self._draw_text_with_shadow(
                preset.description,
                self.font_small,
                desc_color,
                card_x + card_width // 2,
                card_y + 70,
                center=True
            )
            
            # 角色属性
            attr_y = card_y + 120
            attr_spacing = 28
            attrs = [
                f"速度: {preset.speed_normal:.1f}",
                f"集中: {preset.speed_focus:.1f}",
            ]
            for j, attr in enumerate(attrs):
                attr_color = (150, 200, 255) if is_selected else (120, 150, 180)
                self._draw_text_with_shadow(
                    attr,
                    self.font_small,
                    attr_color,
                    card_x + card_width // 2,
                    attr_y + j * attr_spacing,
                    center=True
                )
        
        # 底部提示
        hint_y = self.height - 60
        self._draw_text_with_shadow(
            "←→ 选择角色  Z 确认  X 返回",
            self.font_small,
            (150, 150, 150),
            self.width // 2,
            hint_y,
            center=True
        )
    
    def handle_input(self, dt: float) -> MenuResult:
        """处理输入，返回菜单结果"""
        self.input_cooldown -= dt
        if self.input_cooldown > 0:
            return MenuResult.NONE
        
        keys = pygame.key.get_pressed()
        
        if self.state == MenuState.TITLE:
            # 标题菜单
            if keys[pygame.K_UP]:
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                self.input_cooldown = 0.15
            elif keys[pygame.K_DOWN]:
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                self.input_cooldown = 0.15
            elif keys[pygame.K_z] or keys[pygame.K_RETURN]:
                self.input_cooldown = 0.2
                if self.selected_index == 0:
                    # 开始游戏 -> 先选择角色
                    self.state = MenuState.CHARACTER_SELECT
                    self.character_index = 0
                elif self.selected_index == 1:
                    # 退出
                    return MenuResult.EXIT
            elif keys[pygame.K_ESCAPE]:
                return MenuResult.EXIT
        
        elif self.state == MenuState.CHARACTER_SELECT:
            from model.character import get_all_characters, CharacterId
            characters = get_all_characters()
            
            if keys[pygame.K_LEFT]:
                self.character_index = (self.character_index - 1) % len(characters)
                self.input_cooldown = 0.15
            elif keys[pygame.K_RIGHT]:
                self.character_index = (self.character_index + 1) % len(characters)
                self.input_cooldown = 0.15
            elif keys[pygame.K_z] or keys[pygame.K_RETURN]:
                # 选中角色并开始游戏
                self.selected_character_id = list(CharacterId)[self.character_index]
                self.input_cooldown = 0.2
                return MenuResult.START_GAME
            elif keys[pygame.K_x] or keys[pygame.K_ESCAPE]:
                # 返回标题
                self.state = MenuState.TITLE
                self.input_cooldown = 0.2
        
        return MenuResult.NONE
    
    def update(self, dt: float) -> MenuResult:
        """更新菜单状态"""
        self.time += dt
        self._update_stars(dt)
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return MenuResult.EXIT
        
        return self.handle_input(dt)
    
    def render(self) -> None:
        """渲染菜单"""
        # 背景
        self.screen.fill((15, 10, 30))
        
        # 星星粒子
        self._draw_stars()
        
        # 根据状态绘制
        if self.state == MenuState.TITLE:
            self._draw_title_screen()
        elif self.state == MenuState.CHARACTER_SELECT:
            self._draw_character_select()
        
        pygame.display.flip()
    
    def run(self) -> tuple[MenuResult, "CharacterId | None"]:
        """运行菜单循环，返回结果和选中的角色 ID"""
        from model.character import CharacterId
        
        clock = pygame.time.Clock()
        
        while True:
            dt = clock.tick(60) / 1000.0
            
            result = self.update(dt)
            
            if result == MenuResult.START_GAME:
                # 如果没有在角色选择中选择角色，使用默认
                if self.selected_character_id is None:
                    self.selected_character_id = list(CharacterId)[0]
                return (result, self.selected_character_id)
            elif result == MenuResult.EXIT:
                return (result, None)
            
            self.render()
