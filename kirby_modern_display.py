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
# Default runtime window size (can be changed to fit target displays)
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 480
MIN_WINDOW_WIDTH = 600
MIN_WINDOW_HEIGHT = 360

# Base design size (used for scaling UI elements to smaller/larger screens)
BASE_WIDTH = 1200
BASE_HEIGHT = 800

class ModernKirbyDisplay:
    def __init__(self, fullscreen=False):
        # Initialize display mode
        if fullscreen:
            # Force 800x480 for fullscreen to match target display
            global WINDOW_WIDTH, WINDOW_HEIGHT
            WINDOW_WIDTH = 800
            WINDOW_HEIGHT = 480
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
            self.fullscreen = True
        else:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
            self.fullscreen = False
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
        
        # Scaling factor and fonts (computed from window size)
        self.scale = 1.0
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.update_scale()  # sets self.scale and fonts based on WINDOW_* and BASE_*
        
        # UI state
        self.current_weather = None
        self.current_message = None
        self.kirby_image = None
        
        # Message cycling system
        self.messages = []
        self.current_message_index = 0
        self.has_new_messages = False
        self.last_message_count = 0
        
        # Unread message tracking
        self.viewed_message_ids = set()  # Track which messages have been actively viewed
        self.last_viewed_index = -1      # Track last message that was actively displayed
        
        # Click areas for interaction
        self.message_card_rect = None
        self.emulationstation_button_rect = None
        
        # EmulationStation launch state
        self.emulation_launching = False
        self.launch_countdown = 0
        self.launch_start_time = 0
        
        # Server polling for real-time updates
        self.server_url = "http://localhost:5000"
        self.last_server_check = 0
        self.server_check_interval = 30000  # Check every 30 seconds (matches message update)
        self.server_available = False
        
        # Load initial data
        self.load_weather_data()
        self.load_all_messages()
        self.check_server_availability()
        
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

    def update_scale(self):
        """Update scale and recreate fonts when the window size changes."""
        try:
            global WINDOW_WIDTH, WINDOW_HEIGHT
            sx = WINDOW_WIDTH / BASE_WIDTH
            sy = WINDOW_HEIGHT / BASE_HEIGHT
            # Use the smaller ratio to preserve layout proportions
            self.scale = max(0.5, min(sx, sy))
        except Exception:
            self.scale = 1.0

        # Compute font sizes with sensible minimums
        large_size = max(12, int(42 * self.scale))
        medium_size = max(10, int(28 * self.scale))
        small_size = max(8, int(21 * self.scale))

        try:
            self.font_large = pygame.font.Font("fonts/kirby-classic.ttf", large_size)
            self.font_medium = pygame.font.Font("fonts/kirby-classic.ttf", medium_size)
            self.font_small = pygame.font.Font("fonts/kirby-classic.ttf", small_size)
        except Exception:
            self.font_large = pygame.font.Font(None, large_size)
            self.font_medium = pygame.font.Font(None, medium_size)
            self.font_small = pygame.font.Font(None, small_size)
    
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
        float_offset = math.sin(self.time * 0.003) * (15 * self.scale)
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
                radius = self.kirby_image.get_width()//2 + int(40 * self.scale) - i * int(4 * self.scale)
                pygame.draw.circle(glow_surface, glow_color, 
                                 (glow_surface.get_width()//2, glow_surface.get_height()//2), 
                                 radius)
            
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
                pygame.draw.circle(self.screen, glow_color, (x, int(kirby_y)), int(radius + i * int(6 * self.scale)))
            
            # Main body with gradient effect
            pygame.draw.circle(self.screen, Colors.KIRBY_PINK, (x, int(kirby_y)), int(radius))
            
            # Add inner highlight for 3D effect
            highlight_radius = int(radius * 0.7)
            pygame.draw.circle(self.screen, Colors.KIRBY_LIGHT, 
                             (x - int(radius*0.2), int(kirby_y - radius*0.2)), highlight_radius)
            
            # Eyes with blink animation (scaled to new size)
            eye_scale = radius / (80 * self.scale)  # Scale relative to base size and current scale
            blink = 1 if math.sin(self.time * 0.002) > 0.95 else 0
            eye_height = int(25 * eye_scale) if not blink else max(1, int(5 * eye_scale))
            eye_width = max(1, int(15 * eye_scale))
            
            pygame.draw.ellipse(self.screen, (0, 0, 0), (x-int(25*eye_scale), kirby_y-int(20*eye_scale), eye_width, eye_height))
            pygame.draw.ellipse(self.screen, (0, 0, 0), (x+int(10*eye_scale), kirby_y-int(20*eye_scale), eye_width, eye_height))
            
            # Mouth (scaled)
            mouth_width = max(1, int(20 * eye_scale))
            mouth_height = max(1, int(15 * eye_scale))
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
        temp_rect = temp_surface.get_rect(centerx=x + width // 2, y=y + int(20 * self.scale))
        self.screen.blit(temp_surface, temp_rect)

        # Location (smaller, below temp)
        location_text = "Lethbridge, AB"
        location_surface = self.font_small.render(location_text, True, Colors.TEXT_SECONDARY)
        location_rect = location_surface.get_rect(centerx=x + width // 2, y=temp_rect.bottom + int(6 * self.scale))
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
        condition_rect = condition_surface.get_rect(centerx=x + width // 2, y=location_rect.bottom + int(12 * self.scale))
        self.screen.blit(condition_surface, condition_rect)

        # Additional weather details
        details_y = condition_rect.bottom + int(12 * self.scale)
        details = [
            f"Feels like: {self.current_weather.get('feels_like', 'N/A')}°",
            f"Humidity: {self.current_weather.get('humidity', 'N/A')}%",
            f"Wind: {self.current_weather.get('wind_speed', 'N/A')} km/h"
        ]

        for detail in details:
            detail_surface = self.font_small.render(detail, True, Colors.TEXT_SECONDARY)
            detail_rect = detail_surface.get_rect(centerx=x + width // 2, y=details_y)
            self.screen.blit(detail_surface, detail_rect)
            details_y += int(24 * self.scale)
    
    def draw_message_card(self, x, y, width, height):
        """Draw modern message display card with click interaction"""
        if not self.current_message:
            return
        
        # Store click area for interaction
        self.message_card_rect = pygame.Rect(x, y, width, height)
        
        # Glass card background with enhanced border if clickable
        card_surface = self.create_glass_surface(width, height, 25)
        
        # Add special border if there are multiple messages or new messages
        if len(self.messages) > 1 or self.has_new_messages:
            # Animated border for clickable/new messages
            pulse_alpha = int(80 + 30 * math.sin(self.time * 0.008))
            
            # Use different color for unread messages
            if self.is_current_message_unread():
                border_color = (*Colors.TEXT_ACCENT[:3], pulse_alpha)  # Bright pink for unread
            else:
                border_color = (*Colors.ACCENT[:3], pulse_alpha)       # Normal pink for read
                
            pygame.draw.rect(card_surface, border_color, (0, 0, width, height), 4)
        
        self.screen.blit(card_surface, (x, y))
        
        # Title with message count and new indicator
        title_text = "💌 Community Message"
        
        if len(self.messages) > 1:
            title_text += f" ({self.current_message_index + 1}/{len(self.messages)})"
            
        if self.has_new_messages:
            title_text += " 🆕"
        
        # Add unread dot for current message
        if self.is_current_message_unread():
            title_text += " 🔴"
            
        title_surface = self.font_medium.render(title_text, True, Colors.TEXT_PRIMARY)
        title_rect = title_surface.get_rect(centerx=x + width//2, y=y + int(16 * self.scale))
        self.screen.blit(title_surface, title_rect)
        
        # Click hint if multiple messages
        if len(self.messages) > 1:
            unread_count = self.get_unread_count()
            if unread_count > 0:
                hint_text = f"👆 Click to cycle unread ({unread_count} remaining)"
            else:
                hint_text = "👆 Click to cycle all messages"
            hint_surface = self.font_small.render(hint_text, True, Colors.TEXT_ACCENT)
            hint_rect = hint_surface.get_rect(centerx=x + width//2, y=title_rect.bottom + int(6 * self.scale))
            self.screen.blit(hint_surface, hint_rect)
            message_start_y = hint_rect.bottom + int(10 * self.scale)
        else:
            message_start_y = title_rect.bottom + int(12 * self.scale)
        
        # Message content
        message_text = self.current_message.get('message', 'No message')
        from_text = f"- {self.current_message.get('name', 'Anonymous')}"
        
        # Create a slightly larger font for message text
        try:
            message_font = pygame.font.Font("fonts/kirby-classic.ttf", max(10, int(22 * self.scale)))
            author_font = pygame.font.Font("fonts/kirby-classic.ttf", max(10, int(22 * self.scale)))
        except:
            message_font = pygame.font.Font(None, max(10, int(22 * self.scale)))
            author_font = pygame.font.Font(None, max(10, int(22 * self.scale)))
        
        # Word wrap for message
        words = message_text.split()
        lines = []
        current_line = []
        max_width = width - 40
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = message_font.render(test_line, True, Colors.TEXT_SECONDARY)
            if test_surface.get_width() > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw message lines
        message_y = message_start_y
        for line in lines:
            line_surface = message_font.render(line, True, Colors.TEXT_SECONDARY)
            line_rect = line_surface.get_rect(centerx=x + width//2, y=message_y)
            self.screen.blit(line_surface, line_rect)
            message_y += int(20 * self.scale)
        
        # Draw author
        from_surface = author_font.render(from_text, True, Colors.TEXT_ACCENT)
        from_rect = from_surface.get_rect(right=x + width - int(16 * self.scale), bottom=y + height - int(12 * self.scale))
        self.screen.blit(from_surface, from_rect)
    
    def draw_time_display(self):
        """Draw current time and server status in top corner"""
        now = datetime.now()
        time_text = now.strftime("%H:%M")
        date_text = now.strftime("%B %d, %Y")
        
        # Add server status indicator
        if self.server_available:
            status_text = "🌐 Live Updates"
            status_color = Colors.TEXT_ACCENT
        else:
            status_text = "📡 Local Only"
            status_color = Colors.TEXT_SECONDARY
        
        # Glass background for time (make it taller for status)
        bg_w = max(120, int(180 * self.scale))
        bg_h = max(64, int(105 * self.scale))
        time_bg = self.create_glass_surface(bg_w, bg_h, 25)
        
        # Position time display to ensure it stays on screen
        time_bg_x = max(0, WINDOW_WIDTH - bg_w - int(8 * self.scale))
        time_bg_y = int(8 * self.scale)
        self.screen.blit(time_bg, (time_bg_x, time_bg_y))

        # Center text within the background
        time_surface = self.font_medium.render(time_text, True, Colors.TEXT_PRIMARY)
        time_rect = time_surface.get_rect(centerx=time_bg_x + bg_w//2, y=time_bg_y + int(8 * self.scale))
        self.screen.blit(time_surface, time_rect)
        
        date_surface = self.font_small.render(date_text, True, Colors.TEXT_SECONDARY)
        date_rect = date_surface.get_rect(centerx=time_bg_x + bg_w//2, y=time_rect.bottom + int(4 * self.scale))
        self.screen.blit(date_surface, date_rect)
        
        status_surface = self.font_small.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(centerx=time_bg_x + bg_w//2, y=date_rect.bottom + int(4 * self.scale))
        self.screen.blit(status_surface, status_rect)
    
    def draw_date_header(self, x, y, width, height):
        """Draw date header at top of right section (matching poster style)"""
        # Glass background for date
        date_bg = self.create_glass_surface(width, height, 30)
        self.screen.blit(date_bg, (x, y))
        
        # Get current date and time in comprehensive format
        now = datetime.now()
        date_text = now.strftime("%m/%Y")  # MM/YYYY
        time_text = now.strftime("%H:%M:%S")  # HH:MM:SS
        
        # Combine date and time inline
        combined_text = f"{date_text}  {time_text}"
        
        # Draw combined date/time in large, centered text - pink color
        combined_surface = self.font_large.render(combined_text, True, Colors.TEXT_TITLE)
        combined_rect = combined_surface.get_rect(centerx=x + width // 2, centery=y + height // 2)
        self.screen.blit(combined_surface, combined_rect)
    
    def draw_vertical_title_sidebar(self, x, y, width, height):
        """Draw vertical title sidebar on the right (matching 'EMULATION' vertical text style)"""
        # Glass background for sidebar
        sidebar_bg = self.create_glass_surface(width, height, 35, pink_tint=True)
        self.screen.blit(sidebar_bg, (x, y))
        
        # Get the original title: "Kirby's Dream Weather Station"
        title_text = "Kirby's Dream Weather Station"
        
        # Draw title vertically with larger spacing
        char_height = int(28 * self.scale)  # Increased from 20 to 28
        chars = list(title_text)
        
        # Calculate starting position to center vertically
        total_height = len(chars) * char_height
        start_y = y + (height - total_height) // 2
        
        # Draw each character vertically using medium font instead of small
        for i, char in enumerate(chars):
            char_surface = self.font_medium.render(char, True, Colors.TEXT_TITLE)
            char_x = x + width // 2 - char_surface.get_width() // 2
            char_y = start_y + i * char_height
            self.screen.blit(char_surface, (char_x, char_y))
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        global WINDOW_WIDTH, WINDOW_HEIGHT
        
        if self.fullscreen:
            # Switch to windowed mode
            WINDOW_WIDTH = 800
            WINDOW_HEIGHT = 480
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
            self.fullscreen = False
            print("🪟 Switched to windowed mode (800x480)")
        else:
            # Switch to fullscreen mode with fixed 800x480
            WINDOW_WIDTH = 800
            WINDOW_HEIGHT = 480
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
            self.fullscreen = True
            print(f"🖥️ Switched to fullscreen mode (800x480)")
        
        # Update scaling for new resolution
        try:
            self.update_scale()
        except Exception as e:
            print(f"⚠️ Error updating scale: {e}")
    
    def update_animations(self):
        """Update all animation timers"""
        self.time = pygame.time.get_ticks()
    
    def load_weather_data(self):
        """Load real weather data from API"""
        try:
            # Import weather functions
            from weather_fetcher import get_weather_openweather, get_weather_weatherapi
            
            # Set city to Lethbridge, Alberta by default
            city = "Lethbridge"
            
            # Try OpenWeatherMap first, then WeatherAPI as backup
            print(f"🌡️ Fetching weather for {city}...")
            weather_data = get_weather_openweather(city)
            
            if not weather_data:
                print("🔄 Trying WeatherAPI as backup...")
                weather_data = get_weather_weatherapi(city)
            
            if weather_data:
                # Map the API data to our format
                self.current_weather = {
                    'temperature': weather_data['temperature'],
                    'condition': weather_data['condition'],
                    'feels_like': weather_data['feels_like'],
                    'humidity': weather_data['humidity'],
                    'wind_speed': weather_data['wind_speed'],  # Add wind speed mapping
                    'description': weather_data.get('description', weather_data['condition']),
                    'city': weather_data['city'],
                    'country': weather_data['country']
                }
                print(f"🌡️ Temperature: {weather_data['temperature']}°C -> Season: {self.get_season()}")
            else:
                # Fallback to placeholder if API fails
                print("❌ Weather API failed, using placeholder data")
                self.current_weather = {
                    'temperature': 4,  # More realistic Alberta winter temp
                    'condition': 'Cloudy',
                    'feels_like': 2,
                    'humidity': 65,
                    'wind_speed': 15.2,  # Add realistic wind speed
                    'description': 'Partly Cloudy',
                    'city': 'Lethbridge',
                    'country': 'Canada'
                }
        except Exception as e:
            print(f"❌ Error loading weather: {e}")
            # Fallback to placeholder
            self.current_weather = {
                'temperature': 4,
                'condition': 'Cloudy', 
                'feels_like': 2,
                'humidity': 65,
                'wind_speed': 15.2,  # Add realistic wind speed
                'description': 'Partly Cloudy',
                'city': 'Lethbridge',
                'country': 'Canada'
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
            max_kirby_width = WINDOW_WIDTH // 2 + int(300 * self.scale)  # Half the screen plus extra space
            max_kirby_height = WINDOW_HEIGHT - int(200 * self.scale)     # Most of the height minus title and status
            self.kirby_image = load_kirby_image_by_temperature(temp, max_width=max_kirby_width, max_height=max_kirby_height)
        except:
            self.kirby_image = None
    
    def get_season(self):
        """Get season name from current temperature"""
        try:
            from kirby_display import get_season_from_temperature
            temp = self.current_weather.get('temperature', 20)
            return get_season_from_temperature(temp)
        except:
            return "Unknown"
    
    def draw_emulationstation_button(self, x, y, width, height):
        """Draw EmulationStation launch button"""
        # Store click area for interaction
        self.emulationstation_button_rect = pygame.Rect(x, y, width, height)
        
        # Glass button background
        button_surface = self.create_glass_surface(width, height, 15)
        
        # Add animated border
        pulse_alpha = int(100 + 50 * math.sin(self.time * 0.005))
        border_color = (*Colors.ACCENT[:3], pulse_alpha)
        pygame.draw.rect(button_surface, border_color, (0, 0, width, height), 3)
        
        self.screen.blit(button_surface, (x, y))
        
        # Button icon and text with improved spacing
        icon_text = "🎮"
        icon_surface = self.font_medium.render(icon_text, True, Colors.TEXT_PRIMARY)
        icon_rect = icon_surface.get_rect(centerx=x + width//2, y=y + int(-20 * self.scale))  # Move icon higher
        self.screen.blit(icon_surface, icon_rect)
        
        # Button label (brown text) - move up closer to icon
        label_text = "EmulationStation"
        label_surface = self.font_small.render(label_text, True, Colors.TEXT_SECONDARY)
        label_rect = label_surface.get_rect(centerx=x + width//2, y=icon_rect.bottom + int(4 * self.scale))  # Closer to icon
        self.screen.blit(label_surface, label_rect)
        
        # Subtitle (pink text) - move under the brown text
        subtitle_text = "Launch Games"
        subtitle_surface = self.font_small.render(subtitle_text, True, Colors.TEXT_ACCENT)
        subtitle_rect = subtitle_surface.get_rect(centerx=x + width//2, y=label_rect.bottom + int(6 * self.scale))  # Under brown text
        self.screen.blit(subtitle_surface, subtitle_rect)
    
    def draw_launch_overlay(self):
        """Draw the EmulationStation launch countdown overlay"""
        if not self.emulation_launching:
            return
        
        # Calculate countdown
        elapsed = pygame.time.get_ticks() - self.launch_start_time
        remaining = max(0, 5 - elapsed // 1000)  # 5 second countdown
        
        if remaining <= 0:
            # Launch EmulationStation
            self.emulation_launching = False
            self.actually_launch_emulationstation()
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Launch dialog box - scaled to current display
        dialog_width = max(200, int(480 * self.scale))  # Scaled from base
        dialog_height = max(120, int(200 * self.scale))
        dialog_x = (WINDOW_WIDTH - dialog_width) // 2
        dialog_y = (WINDOW_HEIGHT - dialog_height) // 2

        # Glass dialog background
        dialog_surface = self.create_glass_surface(dialog_width, dialog_height, 25)

        # Add bright border for attention
        border_color = (*Colors.ACCENT[:3], 200)
        pygame.draw.rect(dialog_surface, border_color, (0, 0, dialog_width, dialog_height), 4)

        self.screen.blit(dialog_surface, (dialog_x, dialog_y))

        # Title
        title_text = "🎮 Launching EmulationStation"
        title_surface = self.font_medium.render(title_text, True, Colors.TEXT_PRIMARY)
        title_rect = title_surface.get_rect(centerx=dialog_x + dialog_width // 2, y=dialog_y + int(20 * self.scale))
        self.screen.blit(title_surface, title_rect)

        # Countdown
        countdown_text = str(remaining)
        countdown_surface = self.font_large.render(countdown_text, True, Colors.TEXT_ACCENT)
        countdown_rect = countdown_surface.get_rect(centerx=dialog_x + dialog_width // 2, y=title_rect.bottom + int(12 * self.scale))
        self.screen.blit(countdown_surface, countdown_rect)

        # Cancel instruction
        cancel_text = "Click anywhere to cancel"
        cancel_surface = self.font_small.render(cancel_text, True, Colors.TEXT_SECONDARY)
        cancel_rect = cancel_surface.get_rect(centerx=dialog_x + dialog_width // 2, y=countdown_rect.bottom + int(10 * self.scale))
        self.screen.blit(cancel_surface, cancel_rect)
    
    def launch_emulationstation(self):
        """Start EmulationStation launch countdown"""
        print("🎮 EmulationStation launch initiated - starting countdown...")
        self.emulation_launching = True
        self.launch_start_time = pygame.time.get_ticks()
    
    def actually_launch_emulationstation(self):
        """Launch EmulationStation using TTY console method (like Ctrl+Alt+F4)"""
        import subprocess
        import os
        
        try:
            print("🎮 Launching EmulationStation...")
            print("📺 Switching to console mode (TTY4) like Ctrl+Alt+F4")
            print("🔐 This will require sudo access")
            
            # Get the script path (use the simple timed version)
            script_path = os.path.join(os.path.dirname(__file__), "launch_es.sh")
            
            # Check if script exists
            if not os.path.exists(script_path):
                print(f"❌ Script not found: {script_path}")
                return
            
            print("🚀 Running EmulationStation in console mode...")
            print("⚠️ Kirby display will be hidden until you exit EmulationStation")
            
            # Run the script that switches to TTY and launches EmulationStation
            # This will block until EmulationStation exits
            result = subprocess.call([script_path])
            
            if result == 0:
                print("✅ EmulationStation completed successfully!")
                print("📺 Returned to Kirby Weather Display")
            else:
                print(f"⚠️ EmulationStation script exited with code: {result}")
            
        except Exception as e:
            print(f"❌ Error launching EmulationStation: {e}")
            print("💡 Make sure you have sudo access and EmulationStation is installed")
    
    def load_all_messages(self):
        """Load all messages and detect new ones"""
        try:
            with open('messages.json', 'r') as f:
                new_messages = json.load(f)
            
            # Normalize message format: convert 'username' to 'name' for consistency
            normalized_messages = []
            for msg in new_messages:
                normalized_msg = msg.copy()
                if 'username' in normalized_msg and 'name' not in normalized_msg:
                    normalized_msg['name'] = normalized_msg['username']
                normalized_messages.append(normalized_msg)
            
            # Check for new messages
            current_count = len(normalized_messages)
            if self.last_message_count > 0 and current_count > self.last_message_count:
                self.has_new_messages = True
                print(f"📬 Found {current_count - self.last_message_count} new messages!")
            
            self.messages = normalized_messages
            self.last_message_count = current_count
            
            # Set current message if we have messages
            if self.messages:
                # Stay on current index if valid, otherwise reset to 0
                if self.current_message_index >= len(self.messages):
                    self.current_message_index = 0
                self.current_message = self.messages[self.current_message_index]
            else:
                self.current_message = {'message': 'Welcome to Kirby Weather!', 'name': 'System'}
                
        except:
            self.messages = [{'message': 'Welcome to Kirby Weather!', 'name': 'System'}]
            self.current_message = self.messages[0]
            self.current_message_index = 0
    
    def check_server_availability(self):
        """Check if the message server is available"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=2)
            self.server_available = response.status_code == 200
            if self.server_available:
                print(f"🌐 Connected to message server at {self.server_url}")
            return self.server_available
        except:
            self.server_available = False
            print("📡 Message server not available, using local file only")
            return False
    
    def load_messages_from_server(self):
        """Load messages from the server API"""
        if not self.server_available:
            return False
            
        try:
            response = requests.get(f"{self.server_url}/api/messages", timeout=3)
            if response.status_code == 200:
                data = response.json()
                server_messages = data.get('messages', [])
                
                # Normalize message format: convert 'username' to 'name' for consistency
                normalized_messages = []
                for msg in server_messages:
                    normalized_msg = msg.copy()
                    if 'username' in normalized_msg and 'name' not in normalized_msg:
                        normalized_msg['name'] = normalized_msg['username']
                    normalized_messages.append(normalized_msg)
                
                # Check if we have new messages by comparing IDs when possible
                old_ids = {msg.get('id', '') for msg in self.messages}
                new_ids = {msg.get('id', '') for msg in normalized_messages}
                truly_new_messages = [msg for msg in normalized_messages if msg.get('id', '') not in old_ids and msg.get('id', '')]
                
                if truly_new_messages:
                    new_count = len(truly_new_messages)
                    self.has_new_messages = True
                    print(f"📬 Received {new_count} new messages from server!")
                    
                    # If we're showing the last message, auto-advance to show new ones
                    if self.current_message_index == len(self.messages) - 1:
                        self.current_message_index = len(normalized_messages) - 1
                    
                    # New messages are automatically unread (not in viewed_message_ids)
                    print(f"📋 Total unread messages: {self.get_unread_count() + new_count}")
                
                self.messages = normalized_messages
                self.last_message_count = len(normalized_messages)
                
                # Update current message if index is valid
                if self.messages and self.current_message_index < len(self.messages):
                    self.current_message = self.messages[self.current_message_index]
                elif self.messages:
                    self.current_message_index = 0
                    self.current_message = self.messages[0]
                    
                return True
        except Exception as e:
            # Only print server errors occasionally, not every time
            if not hasattr(self, '_last_server_error') or time.time() - self._last_server_error > 30:
                print(f"⚠️ Server connection lost")
                self._last_server_error = time.time()
            self.server_available = False
        
        return False
    
    def next_message(self):
        """Smart message cycling: unread messages only if available, otherwise all messages"""
        if len(self.messages) <= 1:
            # Mark the single message as read
            if self.current_message:
                current_msg_id = self.current_message.get('id', '')
                if current_msg_id:
                    self.viewed_message_ids.add(current_msg_id)
            self.has_new_messages = False
            return
        
        # Get unread messages
        unread_messages = []
        unread_indices = []
        for i, msg in enumerate(self.messages):
            msg_id = msg.get('id', '')
            if msg_id and msg_id not in self.viewed_message_ids:
                unread_messages.append(msg)
                unread_indices.append(i)
        
        if unread_messages:
            # Cycle through unread messages only
            try:
                current_unread_index = unread_indices.index(self.current_message_index)
                next_unread_index = (current_unread_index + 1) % len(unread_indices)
                self.current_message_index = unread_indices[next_unread_index]
            except ValueError:
                # Current message is not in unread list, go to first unread
                self.current_message_index = unread_indices[0]
            
            # Mark this message as read
            self.current_message = self.messages[self.current_message_index]
            current_msg_id = self.current_message.get('id', '')
            if current_msg_id:
                self.viewed_message_ids.add(current_msg_id)
            
            remaining_unread = len(unread_messages) - 1
            print(f"💌 Showing unread message {unread_indices.index(self.current_message_index) + 1} of {len(unread_messages)} (marked as read, {remaining_unread} unread remaining)")
        else:
            # All messages are read, cycle through all messages
            self.current_message_index = (self.current_message_index + 1) % len(self.messages)
            self.current_message = self.messages[self.current_message_index]
            print(f"💌 Showing read message {self.current_message_index + 1} of {len(self.messages)} (all messages read)")
        
        # Clear new message indicator when manually cycling
        self.has_new_messages = False
    
    def auto_cycle_read_messages(self):
        """Auto-cycle through read messages only (ignores unread messages)"""
        if len(self.messages) <= 1:
            return
            
        # Get read messages only
        read_messages = []
        read_indices = []
        for i, msg in enumerate(self.messages):
            msg_id = msg.get('id', '')
            if not msg_id or msg_id in self.viewed_message_ids:
                read_messages.append(msg)
                read_indices.append(i)
        
        if read_messages and len(read_indices) > 1:
            # Find current position in read messages and advance
            try:
                current_read_index = read_indices.index(self.current_message_index)
                next_read_index = (current_read_index + 1) % len(read_indices)
                self.current_message_index = read_indices[next_read_index]
                self.current_message = self.messages[self.current_message_index]
                print(f"🔄 Auto-cycling to read message {next_read_index + 1} of {len(read_indices)}")
            except ValueError:
                # Current message is not read, stay where we are
                pass
    
    def get_unread_count(self):
        """Get count of unread messages"""
        unread_count = 0
        for msg in self.messages:
            msg_id = msg.get('id', '')
            if msg_id and msg_id not in self.viewed_message_ids:
                unread_count += 1
        return unread_count
    
    def is_current_message_unread(self):
        """Check if current message is unread"""
        if not self.current_message:
            return False
        msg_id = self.current_message.get('id', '')
        return msg_id and msg_id not in self.viewed_message_ids
    
    def check_for_updates(self):
        """Check if it's time to update weather data or messages"""
        current_time = pygame.time.get_ticks()
        
        # Check weather update
        if current_time - self.last_weather_update >= self.weather_update_interval:
            print("🔄 Updating weather data and Kirby image...")
            self.load_weather_data()
            self.last_weather_update = current_time
        
        # Check message update with server polling
        if current_time - self.last_message_update >= self.message_update_interval:
            print("💌 Checking for new messages...")
            old_count = len(self.messages)
            
            # Try server first, fallback to local file
            if self.server_available and self.load_messages_from_server():
                # Server success - messages already loaded
                pass
            else:
                # Server failed or unavailable - try local file and retry server connection
                self.load_all_messages()
                if not self.server_available:
                    self.check_server_availability()
            
            # Only announce if there are actually new messages
            if len(self.messages) > old_count:
                print(f"📬 Found {len(self.messages) - old_count} new messages!")
            
            # Auto-cycle through read messages as part of the main update cycle
            self.auto_cycle_read_messages()
            
            self.last_message_update = current_time
    
    def draw(self):
        """Main draw function - New layout matching Hamlet poster style"""
        # Update time for animations
        self.time = pygame.time.get_ticks()
        
        # Clear screen with gradient
        self.draw_gradient_background()
        
        # Calculate layout dimensions
        left_section_width = int(WINDOW_WIDTH * 0.55)  # Left side for Kirby (larger)
        title_box_width = int(60 * self.scale)  # Right sidebar width
        center_section_width = WINDOW_WIDTH - left_section_width - title_box_width  # Middle section (no overlap)
        
        # ===== LEFT SECTION: Kirby Image (Large focal point) =====
        kirby_x = left_section_width // 2
        kirby_y = WINDOW_HEIGHT // 2 + int(20 * self.scale)
        self.draw_floating_kirby(kirby_x, kirby_y)
        
        # ===== CENTER SECTION (Top to Bottom) =====
        center_start_x = left_section_width + int(10 * self.scale)
        right_padding = int(8 * self.scale)
        
        # 1. DATE/TIME at the very top (above message)
        date_height = int(50 * self.scale)
        date_y = int(10 * self.scale)
        self.draw_date_header(center_start_x + right_padding, date_y, center_section_width - right_padding * 2, date_height)
        
        # 2. COMMUNITY MESSAGE CARD (top-right, below date) - increased by 200px
        message_card_width = center_section_width - right_padding * 2
        message_card_height = int(320 * self.scale)  # Increased from 120 to 320
        message_y = date_y + date_height + int(5 * self.scale)
        self.draw_message_card(center_start_x + right_padding, message_y, message_card_width, message_card_height)
        
        # 3 & 4. STATS BOX and EMULATION STATION SIDE BY SIDE (below message)
        # Split the remaining space between stats (left) and emulation (right)
        stats_emulation_y = message_y + message_card_height + int(8 * self.scale)
        stats_emulation_height = int(240 * self.scale)
        available_width = center_section_width - right_padding * 2
        
        # Stats box takes 60% of width, EmulationStation takes 40%
        stats_width = int(available_width * 0.60)
        emulation_width = int(available_width * 0.40)
        gap = int(6 * self.scale)
        
        # Draw stats box (left side)
        stats_x = center_start_x + right_padding
        self.draw_weather_card(stats_x, stats_emulation_y, stats_width, stats_emulation_height)
        
        # Draw EmulationStation button (right side, vertical)
        emulation_x = stats_x + stats_width + gap
        self.draw_emulationstation_button(emulation_x, stats_emulation_y, emulation_width, stats_emulation_height)
        
        # 5. VERTICAL TITLE SIDEBAR (right edge, full height)
        self.draw_vertical_title_sidebar(WINDOW_WIDTH - title_box_width, 0, title_box_width, WINDOW_HEIGHT)
        
        # Draw EmulationStation launch overlay (if active) - must be last to appear on top
        self.draw_launch_overlay()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        print("🌟 Starting Modern Kirby Weather Display!")
        print("✨ Auto-updates every 30 seconds")
        print("🎮 Controls: R=refresh all, W=weather only, M=messages only, F11=fullscreen, ESC=exit")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_F11:
                        # Toggle fullscreen
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_r:
                        print("🔄 Manual refresh triggered!")
                        self.load_weather_data()
                        self.load_all_messages()
                        self.last_weather_update = pygame.time.get_ticks()
                        self.last_message_update = pygame.time.get_ticks()
                    elif event.key == pygame.K_w:
                        print("🌤️ Manual weather update!")
                        self.load_weather_data()
                        self.last_weather_update = pygame.time.get_ticks()
                    elif event.key == pygame.K_m:
                        print("💌 Manual message cycle!")
                        self.next_message()
                        self.last_message_update = pygame.time.get_ticks()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()
                        print(f"🖱️ Mouse clicked at: {mouse_pos}")
                        if self.emulationstation_button_rect:
                            print(f"🎮 Button rect: {self.emulationstation_button_rect}")
                        
                        # If launching EmulationStation, cancel on any click
                        if self.emulation_launching:
                            print("❌ EmulationStation launch cancelled by user")
                            self.emulation_launching = False
                            continue
                        
                        # Check if click is in message card area
                        if self.message_card_rect and self.message_card_rect.collidepoint(mouse_pos):
                            if len(self.messages) > 1:
                                print("👆 Message card clicked - cycling to next message!")
                                self.next_message()
                            else:
                                print("📝 Only one message available")
                        # Check if click is in EmulationStation button area
                        elif self.emulationstation_button_rect and self.emulationstation_button_rect.collidepoint(mouse_pos):
                            print("🎮 EmulationStation button clicked!")
                            self.launch_emulationstation()
                        else:
                            print("❓ Click not on any interactive element")
                elif event.type == pygame.VIDEORESIZE:
                    if not self.fullscreen:  # Only allow resize in windowed mode
                        global WINDOW_WIDTH, WINDOW_HEIGHT
                        WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                        # Recompute scale and fonts after resize
                        try:
                            self.update_scale()
                        except Exception:
                            pass
            
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
    import sys
    
    # Check for fullscreen argument
    fullscreen = "--fullscreen" in sys.argv or "-f" in sys.argv
    
    try:
        app = ModernKirbyDisplay(fullscreen=fullscreen)
        if fullscreen:
            print("🖥️ Starting in fullscreen mode (Press F11 to toggle, ESC to exit)")
        else:
            print("🪟 Starting in windowed mode (Press F11 for fullscreen, ESC to exit)")
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        pygame.quit()
        sys.exit()
