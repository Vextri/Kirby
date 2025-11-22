#!/usr/bin/env python3
import pygame
import sys
import os
import time
import math
import json
from datetime import datetime

pygame.init()

# ============================================================
# WINDOW DEFAULTS
# ============================================================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 720

# ============================================================
# COLORS
# ============================================================
class Colors:
    PRIMARY_BG = (255, 235, 245)
    SECONDARY_BG = (210, 230, 255)
    DREAMLAND_YELLOW = (255, 248, 210)
    DREAMLAND_BLUE = (190, 230, 255)
    DREAMLAND_PURPLE = (230, 200, 255)

    KIRBY_PINK = (255, 120, 160)
    TEXT_TITLE = (90, 50, 70)
    TEXT = (70, 40, 50)
    TEXT_LIGHT = (120, 80, 110)
    GLASS_BORDER = (255, 180, 220)

# ============================================================
# MAIN APPLICATION
# ============================================================
class KirbyDisplay:
    def __init__(self):
        global WINDOW_WIDTH, WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Kirby's Dream Weather Station")

        self.time = pygame.time.get_ticks()
        self.scale = 1.0
        self.fullscreen = False

        # Load fonts
        self.font_large = pygame.font.Font(None, int(48 * self.scale))
        self.font_medium = pygame.font.Font(None, int(32 * self.scale))
        self.font_small = pygame.font.Font(None, int(24 * self.scale))

        # Kirby image attempt
        self.kirby_image = None
        if os.path.exists("kirby.png"):
            img = pygame.image.load("kirby.png")
            w = int(250 * self.scale)
            h = int(250 * self.scale)
            self.kirby_image = pygame.transform.smoothscale(img, (w, h))

        # Dummy weather + messages
        self.current_weather = {
            "temperature": 3,
            "condition": "Partly Cloudy",
            "feels_like": 1,
            "humidity": 87,
            "wind_speed": 9,
            "city": "Lethbridge",
            "country": "CA"
        }

        self.messages = [
            {"name": "Jay", "message": "You're amazing, bestie!"},
            {"name": "Dad", "message": "Love the project!"},
            {"name": "Mom", "message": "Drink water <3"},
        ]
        self.current_message = self.messages[0]
        self.msg_index = 0

        self.es_rect = None
        self.message_rect = None

    # ============================================================
    # SOFT GRADIENT BACKGROUND
    # ============================================================
    def draw_gradient_background(self):
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            time_factor = math.sin(self.time * 0.001) * 0.05 + 1  # soft shift

            if ratio < 0.3:
                start = Colors.DREAMLAND_YELLOW
                end = Colors.PRIMARY_BG
                local = ratio / 0.3
            elif ratio < 0.7:
                start = Colors.PRIMARY_BG
                end = Colors.SECONDARY_BG
                local = (ratio - 0.3) / 0.4
            else:
                start = Colors.SECONDARY_BG
                end = Colors.DREAMLAND_BLUE
                local = (ratio - 0.7) / 0.3

            r = int(start[0] + (end[0] - start[0]) * local * time_factor)
            g = int(start[1] + (end[1] - start[1]) * local * time_factor)
            b = int(start[2] + (end[2] - start[2]) * local * time_factor)

            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

    # ============================================================
    # GLASS CARD
    # ============================================================
    def create_glass_surface(self, w, h, radius=30, pink_tint=False):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 255, 255, 90), (0, 0, w, h), border_radius=radius)

        if pink_tint:
            pygame.draw.rect(surf, (255, 200, 230, 50), (0, 0, w, h), border_radius=radius)

        pygame.draw.rect(surf, Colors.GLASS_BORDER, (0, 0, w, h), 2, border_radius=radius)
        return surf

    # ============================================================
    # FLOATING KIRBY (reduced glow)
    # ============================================================
    def draw_floating_kirby(self, x, y):
        float_offset = math.sin(self.time * 0.003) * (15 * self.scale)
        kirby_y = y + float_offset

        if not self.kirby_image:
            return

        glow_surface = pygame.Surface(
            (self.kirby_image.get_width() + 40, self.kirby_image.get_height() + 40),
            pygame.SRCALPHA
        )

        glow_colors = [
            Colors.KIRBY_PINK,
            Colors.DREAMLAND_PURPLE,
            Colors.DREAMLAND_BLUE,
        ]

        for i in range(3):  
            alpha = 40 - i * 8
            color = (*glow_colors[i % len(glow_colors)], alpha)
            radius = self.kirby_image.get_width() // 2 + 20 - i * 3
            pygame.draw.circle(glow_surface, color,
                               (glow_surface.get_width() // 2, glow_surface.get_height() // 2),
                               radius)

        glow_rect = glow_surface.get_rect(center=(x, kirby_y))
        self.screen.blit(glow_surface, glow_rect)

        kirby_rect = self.kirby_image.get_rect(center=(x, kirby_y))
        self.screen.blit(self.kirby_image, kirby_rect)

    # ============================================================
    # WEATHER CARD
    # ============================================================
    def draw_weather_card(self, x, y, w, h):
        card = self.create_glass_surface(w, h, 40)
        self.screen.blit(card, (x, y))

        wx = self.current_weather
        temp = f"{wx['temperature']}°"
        cond = wx["condition"]

        t_surf = self.font_large.render(temp, True, Colors.TEXT)
        c_surf = self.font_medium.render(cond, True, Colors.TEXT_LIGHT)

        self.screen.blit(t_surf, (x + 20, y + 20))
        self.screen.blit(c_surf, (x + 20, y + 70))

        details = [
            f"Feels Like: {wx['feels_like']}°",
            f"Humidity: {wx['humidity']}%",
            f"Wind: {wx['wind_speed']} km/h",
        ]

        dy = 130
        for d in details:
            surf = self.font_small.render(d, True, Colors.TEXT_LIGHT)
            self.screen.blit(surf, (x + 20, y + dy))
            dy += 35

    # ============================================================
    # EMULATIONSTATION BUTTON
    # ============================================================
    def draw_emulationstation_button(self, x, y, w, h):
        card = self.create_glass_surface(w, h, 30, pink_tint=True)
        self.screen.blit(card, (x, y))

        label = self.font_medium.render("🎮 Launch Games", True, Colors.TEXT_TITLE)
        self.screen.blit(label, (x + 20, y + 20))

        self.es_rect = pygame.Rect(x, y, w, h)

    # ============================================================
    # MESSAGE CARD
    # ============================================================
    def draw_message_card(self, x, y, w, h):
        card = self.create_glass_surface(w, h, 30)
        self.screen.blit(card, (x, y))

        msg = self.current_message
        text = msg["message"]
        name = msg["name"]

        msg_surf = self.font_small.render(text, True, Colors.TEXT)
        name_surf = self.font_small.render(f"- {name}", True, Colors.TEXT_LIGHT)

        self.screen.blit(msg_surf, (x + 20, y + 20))
        self.screen.blit(name_surf, (x + 20, y + 60))

        self.message_rect = pygame.Rect(x, y, w, h)

    # ============================================================
    # TIME DISPLAY
    # ============================================================
    def draw_time_display(self):
        now = datetime.now()
        time_surf = self.font_medium.render(now.strftime("%H:%M"), True, Colors.TEXT_TITLE)
        date_surf = self.font_small.render(now.strftime("%A, %b %d"), True, Colors.TEXT_LIGHT)

        self.screen.blit(time_surf, (20, 20))
        self.screen.blit(date_surf, (20, 60))

    # ============================================================
    # TITLE
    # ============================================================
    def draw_title(self):
        title_text = "Kirby's Dream Weather Station"
        title_surface = self.font_large.render(title_text, True, Colors.TEXT_TITLE)

        title_rect = title_surface.get_rect(centerx=WINDOW_WIDTH // 2,
                                            y=int(10 * self.scale))

        bg_w = title_surface.get_width() + int(40 * self.scale)
        bg_h = int(60 * self.scale)

        title_bg = self.create_glass_surface(bg_w, bg_h, 40, pink_tint=True)
        title_bg_rect = title_bg.get_rect(center=title_rect.center)

        self.screen.blit(title_bg, title_bg_rect)
        self.screen.blit(title_surface, title_rect)

    # ============================================================
    # MAIN DRAW
    # ============================================================
    def draw(self):
        self.time = pygame.time.get_ticks()
        self.draw_gradient_background()

        # Kirby (left)
        kirby_x = WINDOW_WIDTH // 4
        kirby_y = WINDOW_HEIGHT // 2
        self.draw_floating_kirby(kirby_x, kirby_y)

        # Right column layout
        right_margin = int(20 * self.scale)
        right_width = max(200, int(260 * self.scale))

        weather_x = WINDOW_WIDTH - right_width - right_margin
        weather_y = int(100 * self.scale)
        weather_h = int(300 * self.scale)
        self.draw_weather_card(weather_x, weather_y, right_width, weather_h)

        button_x = weather_x
        button_y = weather_y + weather_h + int(16 * self.scale)
        button_h = int(70 * self.scale)
        self.draw_emulationstation_button(button_x, button_y, right_width, button_h)

        msg_x = weather_x
        msg_y = button_y + button_h + int(16 * self.scale)
        msg_h = int(220 * self.scale)
        self.draw_message_card(msg_x, msg_y, right_width, msg_h)

        self.draw_time_display()
        self.draw_title()

    # ============================================================
    # RUN LOOP
    # ============================================================
    def run(self):
        global WINDOW_WIDTH, WINDOW_HEIGHT
        clock = pygame.time.Clock()
        running = True

        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False

                elif ev.type == pygame.VIDEORESIZE:
                    WINDOW_WIDTH, WINDOW_HEIGHT = ev.w, ev.h
                    self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self.es_rect and self.es_rect.collidepoint(ev.pos):
                        print("Launching EmulationStation...")

                    if self.message_rect and self.message_rect.collidepoint(ev.pos):
                        self.msg_index = (self.msg_index + 1) % len(self.messages)
                        self.current_message = self.messages[self.msg_index]

                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False

            self.draw()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


# ============================================================
# START
# ============================================================
if __name__ == "__main__":
    app = KirbyDisplay()
    app.run()
