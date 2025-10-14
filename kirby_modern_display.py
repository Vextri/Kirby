#!/usr/bin/env python3
"""
Modern Kirby Weather Display with Enhanced UI
A sleek, animated weather display with glassmorphism effects
"""

import pygame
import sys
import os
import time
import math
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
import glob
import random

# Load environment variables
load_dotenv()

# Initialize pygame
pygame.init()

# Kirby-Themed Color Palette (Dreamy Pastels)
class Colors:
    # Base colors - Soft Kirby-inspired pastels
    PRIMARY_BG = (255, 239, 248)      # Very light pink/cream
    SECONDARY_BG = (255, 228, 241)    # Soft pink
    ACCENT = (255, 182, 193)          # Classic Kirby pink
    ACCENT_LIGHT = (255, 204, 219)    # Light pink
    
    # Glass effect colors (with alpha) - Pink tinted
    GLASS_WHITE = (255, 255, 255, 30)
    GLASS_BORDER = (255, 192, 203, 60)  # Pink border
    GLASS_PINK = (255, 182, 193, 40)    # Pink glass tint
    
    # Text colors - Darker for readability on light background
    TEXT_PRIMARY = (139, 69, 19)       # Warm brown
    TEXT_SECONDARY = (160, 82, 45)     # Saddle brown
    TEXT_ACCENT = (255, 105, 180)      # Hot pink
    TEXT_TITLE = (199, 21, 133)        # Deep pink
    
    # Weather colors - Soft pastels
    SUNNY = (255, 223, 0)        # Bright yellow
    CLOUDY = (176, 196, 222)     # Light steel blue
    RAINY = (135, 206, 235)      # Sky blue
    SNOWY = (240, 248, 255)      # Alice blue
    
    # Kirby colors - Enhanced pink palette
    KIRBY_PINK = (255, 182, 193)      # Main Kirby pink
    KIRBY_DARKER = (255, 150, 170)    # Darker pink
    KIRBY_LIGHT = (255, 214, 221)     # Light pink
    KIRBY_GLOW = (255, 192, 203, 80)  # Pink glow with alpha
    
    # Dream Land colors - Soft pastels
    DREAMLAND_BLUE = (173, 216, 230)  # Light blue
    DREAMLAND_GREEN = (152, 251, 152) # Pale green  
    DREAMLAND_PURPLE = (221, 160, 221)# Plum
    DREAMLAND_YELLOW = (255, 255, 224) # Light yellow

# Window configuration
WINDOW_WIDTH = 1200  # Increased from 1000
WINDOW_HEIGHT = 800  # Increased from 700
MIN_WINDOW_WIDTH = 900  # Increased from 800
MIN_WINDOW_HEIGHT = 650  # Increased from 600

class ModernKirbyDisplay:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Kirby Weather Station 🌸")
        
        # Animation variables
        self.time = 0
        self.kirby_float_offset = 0
        self.weather_particles = []
        
        # Update timing (in milliseconds)
        self.last_weather_update = pygame.time.get_ticks()
        self.last_message_update = pygame.time.get_ticks()
        self.weather_update_interval = 30000  # 30 seconds
        self.message_update_interval = 30000   # 30 seconds
        
        # Fonts
        try:
            self.font_large = pygame.font.Font("fonts/kirby-classic.ttf", 42)
            self.font_medium = pygame.font.Font("fonts/kirby-classic.ttf", 28)
            self.font_small = pygame.font.Font("fonts/kirby-classic.ttf", 18)
        except:
            self.font_large = pygame.font.Font(None, 42)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 18)
        
        # UI state
        self.current_weather = None
        self.current_message = None
        self.kirby_image = None
        
        # Load initial data
        self.load_weather_data()
        self.load_current_message()
        
    def create_glass_surface(self, width, height, alpha=30, pink_tint=True):
        """Create a surface with Kirby-themed glassmorphism effect"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Create glass background with pink tint
        if pink_tint:
            glass_color = (*Colors.GLASS_PINK[:3], alpha)
        else:
            glass_color = (*Colors.GLASS_WHITE[:3], alpha)
        surface.fill(glass_color)
        
        # Add subtle pink border
        border_color = (*Colors.ACCENT[:3], 80)
        pygame.draw.rect(surface, border_color, (0, 0, width, height), 3)
        
        # Add inner highlight for extra gloss
        highlight_color = (*Colors.KIRBY_LIGHT[:3], 40)
        pygame.draw.rect(surface, highlight_color, (2, 2, width-4, height-4), 1)
        
        return surface
    
    def draw_gradient_background(self):
        """Draw animated Kirby-themed gradient background"""
        # Create dreamy multi-color gradient from top to bottom
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            
            # Animated color shift for dreamy effect
            time_factor = math.sin(self.time * 0.001) * 0.15 + 1
            
            # Create a dreamy gradient through Kirby colors
            if ratio < 0.3:
                # Top: Light pink to cream
                start_color = Colors.DREAMLAND_YELLOW
                end_color = Colors.PRIMARY_BG
                local_ratio = ratio / 0.3
            elif ratio < 0.7:
                # Middle: Cream to soft pink  
                start_color = Colors.PRIMARY_BG
                end_color = Colors.SECONDARY_BG
                local_ratio = (ratio - 0.3) / 0.4
            else:
                # Bottom: Soft pink to light blue
                start_color = Colors.SECONDARY_BG
                end_color = Colors.DREAMLAND_BLUE
                local_ratio = (ratio - 0.7) / 0.3
            
            # Interpolate colors with animation
            r = int(start_color[0] + (end_color[0] - start_color[0]) * local_ratio * time_factor)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * local_ratio * time_factor)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * local_ratio * time_factor)
            
            # Ensure colors stay in valid range
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))
    
    def draw_floating_kirby(self, x, y):
        """Draw Kirby with floating animation"""
        # Floating animation
        float_offset = math.sin(self.time * 0.003) * 15
        kirby_y = y + float_offset
        
        if self.kirby_image:
            # Add glow effect around Kirby
            glow_surface = pygame.Surface((self.kirby_image.get_width() + 80, 
                                         self.kirby_image.get_height() + 80), pygame.SRCALPHA)
            
            # Create magical rainbow glow layers
            glow_colors = [
                Colors.KIRBY_PINK,
                Colors.DREAMLAND_PURPLE, 
                Colors.DREAMLAND_BLUE,
                Colors.DREAMLAND_GREEN,
                Colors.DREAMLAND_YELLOW
            ]
            
            for i in range(8):
                alpha = 50 - i * 6
                color_index = i % len(glow_colors)
                glow_color = (*glow_colors[color_index], alpha)
                pygame.draw.circle(glow_surface, glow_color, 
                                 (glow_surface.get_width()//2, glow_surface.get_height()//2), 
                                 self.kirby_image.get_width()//2 + 40 - i*4)
            
            # Blit glow then Kirby
            glow_rect = glow_surface.get_rect(center=(x, kirby_y))
            self.screen.blit(glow_surface, glow_rect)
            
            kirby_rect = self.kirby_image.get_rect(center=(x, kirby_y))
            self.screen.blit(self.kirby_image, kirby_rect)
        else:
            # Fallback: draw animated Kirby circle (much larger)
            base_radius = min(WINDOW_WIDTH // 8, WINDOW_HEIGHT // 6)  # Responsive size
            radius = base_radius + math.sin(self.time * 0.005) * 8
            
            # Magical rainbow glow effect
            glow_colors = [
                Colors.KIRBY_PINK,
                Colors.DREAMLAND_PURPLE, 
                Colors.DREAMLAND_BLUE,
                Colors.DREAMLAND_GREEN,
                Colors.DREAMLAND_YELLOW,
                Colors.ACCENT_LIGHT
            ]
            
            for i in range(15):
                alpha = 60 - i * 3
                color_index = i % len(glow_colors)
                glow_color = (*glow_colors[color_index], alpha)
                pygame.draw.circle(self.screen, glow_color, (x, int(kirby_y)), int(radius + i*6))
            
            # Main body with gradient effect
            pygame.draw.circle(self.screen, Colors.KIRBY_PINK, (x, int(kirby_y)), int(radius))
            
            # Add inner highlight for 3D effect
            highlight_radius = int(radius * 0.7)
            pygame.draw.circle(self.screen, Colors.KIRBY_LIGHT, 
                             (x - int(radius*0.2), int(kirby_y - radius*0.2)), highlight_radius)
            
            # Eyes with blink animation (scaled to new size)
            eye_scale = radius / 80  # Scale based on original 80px radius
            blink = 1 if math.sin(self.time * 0.002) > 0.95 else 0
            eye_height = int(25 * eye_scale) if not blink else int(5 * eye_scale)
            eye_width = int(15 * eye_scale)
            
            pygame.draw.ellipse(self.screen, (0, 0, 0), (x-int(25*eye_scale), kirby_y-int(20*eye_scale), eye_width, eye_height))
            pygame.draw.ellipse(self.screen, (0, 0, 0), (x+int(10*eye_scale), kirby_y-int(20*eye_scale), eye_width, eye_height))
            
            # Mouth (scaled)
            mouth_width = int(20 * eye_scale)
            mouth_height = int(15 * eye_scale)
            pygame.draw.ellipse(self.screen, Colors.KIRBY_DARKER, (x-mouth_width//2, kirby_y+int(10*eye_scale), mouth_width, mouth_height))
    
    def draw_weather_card(self, x, y, width, height):
        """Draw modern weather information card"""
        if not self.current_weather:
            return
        
        # Glass card background
        card_surface = self.create_glass_surface(width, height, 30)
        card_rect = pygame.Rect(x, y, width, height)
        self.screen.blit(card_surface, card_rect)
        
        # Weather icon area (top)
        icon_area_height = height // 3
        
        # Temperature (large, centered)
        temp_text = f"{self.current_weather.get('temperature', 'N/A')}°"
        temp_surface = self.font_large.render(temp_text, True, Colors.TEXT_PRIMARY)
        temp_rect = temp_surface.get_rect(centerx=x + width//2, y=y + 20)
        self.screen.blit(temp_surface, temp_rect)
        
        # Location (smaller, below temp)
        location_text = "Lethbridge, AB"
        location_surface = self.font_small.render(location_text, True, Colors.TEXT_SECONDARY)
        location_rect = location_surface.get_rect(centerx=x + width//2, y=temp_rect.bottom + 5)
        self.screen.blit(location_surface, location_rect)
        
        # Weather condition with cute emoji
        condition_text = self.current_weather.get('condition', 'Unknown')
        
        # Add weather emoji based on condition
        weather_emoji = "☀️" if "sunny" in condition_text.lower() else \
                       "☁️" if "cloud" in condition_text.lower() else \
                       "🌧️" if "rain" in condition_text.lower() else \
                       "❄️" if "snow" in condition_text.lower() else "🌸"
        
        condition_display = f"{weather_emoji} {condition_text} {weather_emoji}"
        condition_surface = self.font_medium.render(condition_display, True, Colors.TEXT_ACCENT)
        condition_rect = condition_surface.get_rect(centerx=x + width//2, y=location_rect.bottom + 20)
        self.screen.blit(condition_surface, condition_rect)
        
        # Additional weather details
        details_y = condition_rect.bottom + 30
        details = [
            f"Feels like: {self.current_weather.get('feels_like', 'N/A')}°",
            f"Humidity: {self.current_weather.get('humidity', 'N/A')}%",
            f"Wind: {self.current_weather.get('wind_speed', 'N/A')} km/h"
        ]
        
        for detail in details:
            detail_surface = self.font_small.render(detail, True, Colors.TEXT_SECONDARY)
            detail_rect = detail_surface.get_rect(centerx=x + width//2, y=details_y)
            self.screen.blit(detail_surface, detail_rect)
            details_y += 25
    
    def draw_message_card(self, x, y, width, height):
        """Draw modern message display card"""
        if not self.current_message:
            return
        
        # Glass card background
        card_surface = self.create_glass_surface(width, height, 25)
        self.screen.blit(card_surface, (x, y))
        
        # Title
        title_surface = self.font_medium.render("💌 Community Message", True, Colors.TEXT_PRIMARY)
        title_rect = title_surface.get_rect(centerx=x + width//2, y=y + 20)
        self.screen.blit(title_surface, title_rect)
        
        # Message content
        message_text = self.current_message.get('message', 'No message')
        from_text = f"- {self.current_message.get('name', 'Anonymous')}"
        
        # Word wrap for message
        words = message_text.split()
        lines = []
        current_line = []
        max_width = width - 40
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font_small.render(test_line, True, Colors.TEXT_SECONDARY)
            if test_surface.get_width() > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw message lines
        message_y = title_rect.bottom + 20
        for line in lines:
            line_surface = self.font_small.render(line, True, Colors.TEXT_SECONDARY)
            line_rect = line_surface.get_rect(centerx=x + width//2, y=message_y)
            self.screen.blit(line_surface, line_rect)
            message_y += 22
        
        # Draw author
        from_surface = self.font_small.render(from_text, True, Colors.TEXT_ACCENT)
        from_rect = from_surface.get_rect(right=x + width - 20, bottom=y + height - 20)
        self.screen.blit(from_surface, from_rect)
    
    def draw_time_display(self):
        """Draw current time in top corner"""
        now = datetime.now()
        time_text = now.strftime("%H:%M")
        date_text = now.strftime("%B %d, %Y")
        
        # Glass background for time
        time_bg = self.create_glass_surface(180, 80, 25)
        self.screen.blit(time_bg, (WINDOW_WIDTH - 200, 20))
        
        time_surface = self.font_medium.render(time_text, True, Colors.TEXT_PRIMARY)
        time_rect = time_surface.get_rect(centerx=WINDOW_WIDTH - 110, y=35)
        self.screen.blit(time_surface, time_rect)
        
        date_surface = self.font_small.render(date_text, True, Colors.TEXT_SECONDARY)
        date_rect = date_surface.get_rect(centerx=WINDOW_WIDTH - 110, y=time_rect.bottom + 5)
        self.screen.blit(date_surface, date_rect)
    
    def update_animations(self):
        """Update all animation timers"""
        self.time = pygame.time.get_ticks()
    
    def load_weather_data(self):
        """Load weather data (placeholder for now)"""
        # This would connect to your actual weather API
        self.current_weather = {
            'temperature': 24,
            'condition': 'Sunny',
            'feels_like': 26,
            'humidity': 45,
            'wind_speed': 12
        }
        
        # Load appropriate Kirby image
        self.load_kirby_image()
    
    def load_kirby_image(self):
        """Load Kirby image based on weather"""
        try:
            # Use your existing season logic
            from kirby_display import get_season_from_temperature, load_kirby_image_by_temperature
            
            temp = self.current_weather.get('temperature', 20)
            # Much larger Kirby image - use more of the available space
            max_kirby_width = WINDOW_WIDTH // 2 - 100  # Half the screen minus some margin
            max_kirby_height = WINDOW_HEIGHT - 300     # Most of the height minus title and status
            self.kirby_image = load_kirby_image_by_temperature(temp, max_width=max_kirby_width, max_height=max_kirby_height)
        except:
            self.kirby_image = None
    
    def load_current_message(self):
        """Load current message"""
        try:
            with open('messages.json', 'r') as f:
                messages = json.load(f)
            if messages:
                self.current_message = random.choice(messages)
        except:
            self.current_message = {'message': 'Welcome to Kirby Weather!', 'name': 'System'}
    
    def check_for_updates(self):
        """Check if it's time to update weather data or messages"""
        current_time = pygame.time.get_ticks()
        
        # Check weather update
        if current_time - self.last_weather_update >= self.weather_update_interval:
            print("🔄 Updating weather data and Kirby image...")
            self.load_weather_data()
            self.last_weather_update = current_time
        
        # Check message update  
        if current_time - self.last_message_update >= self.message_update_interval:
            print("💌 Loading new message...")
            self.load_current_message()
            self.last_message_update = current_time
    
    def draw(self):
        """Main draw function"""
        # Clear screen with gradient
        self.draw_gradient_background()
        
        # Draw floating Kirby (left side)
        kirby_x = WINDOW_WIDTH // 4
        kirby_y = WINDOW_HEIGHT // 2
        self.draw_floating_kirby(kirby_x, kirby_y)
        
        # Draw weather card (top right)
        weather_card_width = 280
        weather_card_height = 300
        weather_x = WINDOW_WIDTH - weather_card_width - 40
        weather_y = 120
        self.draw_weather_card(weather_x, weather_y, weather_card_width, weather_card_height)
        
        # Draw message card (bottom right)
        message_card_width = 350
        message_card_height = 200
        message_x = WINDOW_WIDTH - message_card_width - 40
        message_y = WINDOW_HEIGHT - message_card_height - 40
        self.draw_message_card(message_x, message_y, message_card_width, message_card_height)
        
        # Draw time display
        self.draw_time_display()
        
        # Draw title with Kirby-themed styling
        title_text = "🌸 Kirby's Dream Weather Station 🌸"
        
        # Create a gradient title effect
        title_surface = self.font_large.render(title_text, True, Colors.TEXT_TITLE)
        title_rect = title_surface.get_rect(centerx=WINDOW_WIDTH//2, y=30)
        
        # Title background with pink theme
        title_bg = self.create_glass_surface(title_surface.get_width() + 60, 80, 40, pink_tint=True)
        title_bg_rect = title_bg.get_rect(center=title_rect.center)
        self.screen.blit(title_bg, title_bg_rect)
        
        # Add a shadow effect for the title
        shadow_surface = self.font_large.render(title_text, True, Colors.KIRBY_DARKER)
        shadow_rect = shadow_surface.get_rect(centerx=WINDOW_WIDTH//2 + 2, y=32)
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(title_bg, title_bg_rect)
        self.screen.blit(title_surface, title_rect)
        
        # Draw update status (bottom left corner)
        self.draw_update_status()
    
    def draw_update_status(self):
        """Draw small status showing time until next updates"""
        current_time = pygame.time.get_ticks()
        
        # Calculate time until next updates
        weather_time_left = (self.weather_update_interval - (current_time - self.last_weather_update)) // 1000
        message_time_left = (self.message_update_interval - (current_time - self.last_message_update)) // 1000
        
        # Only show if positive
        weather_time_left = max(0, weather_time_left)
        message_time_left = max(0, message_time_left)
        
        # Status text
        status_lines = [
            f"Next weather update: {weather_time_left}s",
            f"Next message update: {message_time_left}s",
            "Press: R=refresh, W=weather, M=message, ESC=exit"
        ]
        
        # Add Kirby image info if available
        if self.kirby_image:
            img_w, img_h = self.kirby_image.get_size()
            status_lines.append(f"Kirby image: {img_w}x{img_h}px")
        
        # Background
        status_bg = self.create_glass_surface(350, 100, 15)  # Slightly larger for extra info
        self.screen.blit(status_bg, (20, WINDOW_HEIGHT - 120))
        
        # Text
        y_offset = WINDOW_HEIGHT - 110  # Adjusted for larger status box
        for line in status_lines:
            text_surface = self.font_small.render(line, True, Colors.TEXT_SECONDARY)
            self.screen.blit(text_surface, (30, y_offset))
            y_offset += 20
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        print("🌟 Starting Modern Kirby Weather Display!")
        print("✨ Auto-updates every 30 seconds")
        print("🎮 Controls: R=refresh all, W=weather only, M=messages only, ESC=exit")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        print("🔄 Manual refresh triggered!")
                        self.load_weather_data()
                        self.load_current_message()
                        self.last_weather_update = pygame.time.get_ticks()
                        self.last_message_update = pygame.time.get_ticks()
                    elif event.key == pygame.K_w:
                        print("🌤️ Manual weather update!")
                        self.load_weather_data()
                        self.last_weather_update = pygame.time.get_ticks()
                    elif event.key == pygame.K_m:
                        print("💌 Manual message update!")
                        self.load_current_message()
                        self.last_message_update = pygame.time.get_ticks()
                elif event.type == pygame.VIDEORESIZE:
                    global WINDOW_WIDTH, WINDOW_HEIGHT
                    WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                    self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
            
            # Update animations
            self.update_animations()
            
            # Check for periodic updates
            self.check_for_updates()
            
            # Draw everything
            self.draw()
            
            # Update display
            pygame.display.flip()
            clock.tick(60)  # 60 FPS for smooth animations
        
        print("👋 Modern Kirby Display closed!")
        pygame.quit()

if __name__ == "__main__":
    try:
        app = ModernKirbyDisplay()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        pygame.quit()
        sys.exit()
