#!/usr/bin/env python3
"""
Kirby Touch Weather Display
Lightweight touchscreen-friendly interface with swipe gestures
Main focus: Full-screen art that changes with weather
Swipe right for messages panel
"""

import pygame
import sys
import os
import time
import math
import json
import random
import requests
import threading
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize pygame
pygame.init()

# Kirby-Themed Color Palette
class Colors:
    PRIMARY_BG = (255, 239, 248)      # Very light pink/cream
    SECONDARY_BG = (255, 228, 241)    # Soft pink
    ACCENT = (255, 182, 193)          # Classic Kirby pink
    ACCENT_LIGHT = (255, 204, 219)    # Light pink
    
    TEXT_PRIMARY = (139, 69, 19)      # Warm brown
    TEXT_SECONDARY = (160, 82, 45)    # Saddle brown
    TEXT_ACCENT = (255, 105, 180)     # Hot pink
    
    KIRBY_PINK = (255, 182, 193)
    KIRBY_LIGHT = (255, 214, 221)
    
    NOTIFICATION = (255, 69, 0)       # Red orange for notifications
    GLASS_OVERLAY = (255, 255, 255, 150)  # Semi-transparent white

# Window configuration - optimized for touch
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 30  # Lower FPS for resource efficiency

class TouchWeatherDisplay:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🌸 Kirby Touch Weather")
        
        # App state
        self.current_view = "art"  # "art" or "messages"
        self.panel_offset = 0      # 0 = art view, WINDOW_WIDTH = messages view
        self.animating = False
        self.animation_start = 0
        self.animation_duration = 300  # milliseconds
        
        # Message scrolling state
        self.message_scroll_y = 0  # Current scroll position
        self.max_scroll_y = 0      # Maximum scroll (calculated dynamically)
        
        # Touch/scroll tracking for messages panel
        self.scroll_dragging = False
        self.scroll_start_y = 0
        self.scroll_last_y = 0
        
        # Unread message tracking
        self.viewed_message_ids = set()  # Track which messages have been actively viewed
        
        # Touch state
        self.dragging = False
        self.drag_start_x = 0
        self.drag_current_x = 0
        
        # Data
        self.current_weather = None
        self.messages = []
        self.unread_count = 0  # Start with no notifications
        self.kirby_image = None
        self.last_update = 0
        
        # Fonts - load once for efficiency
        try:
            self.font_large = pygame.font.Font("fonts/kirby-classic.ttf", 36)
            self.font_medium = pygame.font.Font("fonts/kirby-classic.ttf", 24)
            self.font_small = pygame.font.Font("fonts/kirby-classic.ttf", 18)
        except:
            self.font_large = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
        
        # Animation variables
        self.time = 0
        
        # Performance optimization: Pre-rendered surfaces and dirty flags
        self.background_surface = None
        self.kirby_glow_surface = None
        self.messages_surface = None
        self.background_dirty = True
        self.messages_dirty = True
        self.glow_dirty = True
        
        # Server polling for real-time updates
        self.server_url = "http://localhost:5000"
        self.last_server_check = 0
        self.server_check_interval = 30000  # Check every 30 seconds (matches full update)
        self.server_available = False
        
        # Load initial data
        self.load_all_data()
        self.check_server_availability()
    
    def load_all_data(self, quiet=False):
        """Load weather and messages data"""
        self.load_weather_data()
        self.load_kirby_image(quiet=quiet)
        self.load_messages()
        self.last_update = pygame.time.get_ticks()
    
    def load_weather_data(self):
        """Load real weather data from API"""
        try:
            from weather_fetcher import get_weather_weatherapi
            weather_data = get_weather_weatherapi("Lethbridge, Alberta")
            
            if weather_data:
                self.current_weather = {
                    'temperature': weather_data['temperature'],
                    'condition': weather_data['condition'],
                    'feels_like': weather_data.get('feels_like', weather_data['temperature']),
                    'humidity': weather_data.get('humidity', 50),
                    'wind_speed': weather_data.get('wind_speed', 0),
                    'city': weather_data.get('city', 'Lethbridge')
                }
                print(f"🌤️ Weather updated: {self.current_weather['temperature']}°C, {self.current_weather['condition']}")
            else:
                # Fallback to default data if API fails
                print("⚠️ Weather API failed, using fallback data")
                self.current_weather = {
                    'temperature': 20,
                    'condition': 'Unknown',
                    'feels_like': 20,
                    'humidity': 50,
                    'wind_speed': 0,
                    'city': 'Lethbridge'
                }
        except Exception as e:
            print(f"⚠️ Weather fetch error: {e}")
            # Fallback weather data
            self.current_weather = {
                'temperature': 20,
                'condition': 'Unknown',
                'feels_like': 20,
                'humidity': 50,
                'wind_speed': 0,
                'city': 'Lethbridge'
            }
    
    def load_kirby_image(self, quiet=False):
        """Load Kirby image based on weather"""
        try:
            from kirby_display import get_season_from_temperature, load_kirby_image_by_temperature
            temp = self.current_weather.get('temperature', 20)
            # Load large image for full-screen display
            max_size = min(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 150)
            old_image = self.kirby_image
            
            # Temporarily suppress print statements if quiet
            if quiet:
                import os
                import sys
                devnull = open(os.devnull, 'w')
                old_stdout = sys.stdout
                sys.stdout = devnull
                
            self.kirby_image = load_kirby_image_by_temperature(temp, max_width=max_size, max_height=max_size)
            
            if quiet:
                sys.stdout = old_stdout
                devnull.close()
            
            # Mark glow as dirty if image changed
            if old_image != self.kirby_image:
                self.glow_dirty = True
        except:
            self.kirby_image = None
    
    def load_messages(self):
        """Load messages from local file and check for unread ones"""
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
            
            # Check if we have new messages by comparing IDs when possible
            if hasattr(self, 'messages'):
                old_ids = {msg.get('id', '') for msg in self.messages}
                new_ids = {msg.get('id', '') for msg in normalized_messages}
                truly_new_messages = [msg for msg in normalized_messages if msg.get('id', '') not in old_ids and msg.get('id', '')]
                
                if truly_new_messages:
                    new_count = len(truly_new_messages)
                    self.unread_count += new_count
                    self.messages_dirty = True
                    print(f"📬 Found {new_count} new messages in local file!")
                    print(f"🔔 Unread count now: {self.unread_count}")
            else:
                # First load - don't mark as unread
                if not hasattr(self, 'unread_count'):
                    self.unread_count = 0
            
            self.messages = normalized_messages
                
        except:
            self.messages = [{'message': 'Welcome to Kirby Weather!', 'name': 'System'}]
            if not hasattr(self, 'unread_count'):
                self.unread_count = 0
    
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
        """Load messages from the server API (silent unless changes detected)"""
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
                
                # Check if we have new messages by comparing IDs, not just count
                old_ids = {msg.get('id', '') for msg in self.messages}
                new_ids = {msg.get('id', '') for msg in normalized_messages}
                truly_new_messages = [msg for msg in normalized_messages if msg.get('id', '') not in old_ids]
                
                if truly_new_messages:
                    new_count = len(truly_new_messages)
                    self.unread_count += new_count
                    self.messages_dirty = True
                    print(f"📬 Received {new_count} new messages from server!")
                    print(f"🔔 Unread count now: {self.unread_count}")
                
                self.messages = normalized_messages
                return True
        except Exception as e:
            # Only print server errors occasionally, not every time
            if not hasattr(self, '_last_server_error') or time.time() - self._last_server_error > 30:
                print(f"⚠️ Server connection lost")
                self._last_server_error = time.time()
            self.server_available = False
        
        return False
    
    def simulate_new_message(self):
        """Simulate receiving a new message for testing"""
        test_messages = [
            "Beautiful weather today! 🌞",
            "Kirby looks so cute in this season! 💕",
            "Hope everyone is staying warm/cool! ❄️☀️",
            "Love this weather display! 🌸",
            "The colors are so pretty! 🌈"
        ]
        
        new_msg = {
            "message": random.choice(test_messages),
            "name": f"Tester{random.randint(1, 99)}"
        }
        
        # Add to current messages list
        self.messages.append(new_msg)
        self.unread_count += 1
        self.messages_dirty = True  # Mark for re-render
        
        print(f"✨ Added test message: '{new_msg['message'][:30]}...' from {new_msg['name']}")
        print(f"📊 Total messages now: {len(self.messages)}, Unread: {self.unread_count}")
    
    def get_unread_count(self):
        """Get count of unread messages"""
        unread_count = 0
        for msg in self.messages:
            msg_id = msg.get('id', '')
            if msg_id and msg_id not in self.viewed_message_ids:
                unread_count += 1
        return unread_count
    
    def mark_messages_as_read(self):
        """Mark all currently loaded messages as read when entering messages view"""
        for msg in self.messages:
            msg_id = msg.get('id', '')
            if msg_id:
                self.viewed_message_ids.add(msg_id)
        print(f"📖 Marked {len(self.messages)} messages as read")
    
    def handle_touch_start(self, x, y):
        """Handle touch/click start"""
        self.dragging = True
        self.drag_start_x = x
        self.drag_current_x = x
        
        # Check if we're in messages view and in the scrollable area for scrolling
        if self.current_view == "messages":
            messages_area_top = 120
            messages_area_height = WINDOW_HEIGHT - 200
            if messages_area_top <= y <= messages_area_top + messages_area_height:
                self.scroll_dragging = True
                self.scroll_start_y = y
                self.scroll_last_y = y
    
    def handle_touch_move(self, x, y):
        """Handle touch/drag movement"""
        if self.dragging and not self.animating:
            self.drag_current_x = x
            
            # Handle vertical scrolling in messages view
            if self.scroll_dragging and self.current_view == "messages":
                scroll_delta = self.scroll_last_y - y  # Inverted for natural scrolling
                self.message_scroll_y += scroll_delta
                self.message_scroll_y = max(0, min(self.message_scroll_y, self.max_scroll_y))
                self.scroll_last_y = y
                # Don't mark dirty during active scrolling for smoother performance
            else:
                # Handle horizontal swiping for view switching
                drag_distance = x - self.drag_start_x
                
                if self.current_view == "art":
                    # Dragging from art view - only allow right swipe
                    self.panel_offset = max(0, min(drag_distance, WINDOW_WIDTH))
                else:
                    # Dragging from messages view - only allow left swipe
                    self.panel_offset = max(0, min(WINDOW_WIDTH + drag_distance, WINDOW_WIDTH))
    
    def handle_touch_end(self):
        """Handle touch/click end - decide whether to switch views"""
        if not self.dragging:
            return
            
        was_scrolling = self.scroll_dragging
        self.dragging = False
        self.scroll_dragging = False
        
        # Mark messages dirty after scrolling to refresh static content
        if was_scrolling:
            self.messages_dirty = True
            return
        
        # Determine if we should switch views based on drag distance
        drag_distance = abs(self.drag_current_x - self.drag_start_x)
        threshold = WINDOW_WIDTH * 0.3  # 30% of screen width
        
        if drag_distance > threshold:
            # Switch views
            if self.current_view == "art" and self.drag_current_x > self.drag_start_x:
                self.switch_to_messages()
            elif self.current_view == "messages" and self.drag_current_x < self.drag_start_x:
                self.switch_to_art()
            else:
                self.snap_back()
        else:
            self.snap_back()
    
    def switch_to_messages(self):
        """Animate to messages view and mark messages as read"""
        self.current_view = "messages"
        
        # Mark all visible messages as read when user opens messages panel
        self.mark_messages_as_read()
        self.unread_count = 0  # Clear unread count since user is viewing messages
        
        self.start_animation(WINDOW_WIDTH)
    
    def switch_to_art(self):
        """Animate to art view"""
        self.current_view = "art"
        self.start_animation(0)
    
    def snap_back(self):
        """Snap back to current view"""
        target = WINDOW_WIDTH if self.current_view == "messages" else 0
        self.start_animation(target)
    
    def start_animation(self, target_offset):
        """Start smooth animation to target offset"""
        self.animating = True
        self.animation_start = pygame.time.get_ticks()
        self.animation_start_offset = self.panel_offset
        self.animation_target = target_offset
    
    def update_animation(self):
        """Update panel animation"""
        if not self.animating:
            return
            
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.animation_start
        
        if elapsed >= self.animation_duration:
            # Animation complete
            self.panel_offset = self.animation_target
            self.animating = False
        else:
            # Smooth easing animation
            progress = elapsed / self.animation_duration
            # Ease out cubic for smooth deceleration
            eased_progress = 1 - (1 - progress) ** 3
            
            self.panel_offset = self.animation_start_offset + (
                self.animation_target - self.animation_start_offset
            ) * eased_progress
    
    def draw_art_view(self):
        """Draw the main art view with optimized rendering"""
        # Use pre-rendered background
        self.create_background_surface()
        self.screen.blit(self.background_surface, (0, 0))
        
        # Draw Kirby image centered
        if self.kirby_image:
            kirby_rect = self.kirby_image.get_rect()
            kirby_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20)
            
            # Use pre-rendered glow effect
            self.create_kirby_glow_surface()
            if self.kirby_glow_surface:
                glow_rect = self.kirby_glow_surface.get_rect()
                glow_rect.center = kirby_rect.center
                self.screen.blit(self.kirby_glow_surface, glow_rect)
            
            self.screen.blit(self.kirby_image, kirby_rect)
        else:
            # Simplified fallback circle (no expensive glow)
            center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20)
            radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 6
            
            # Simple single glow circle
            pygame.draw.circle(self.screen, (*Colors.KIRBY_LIGHT, 100), center, radius + 20)
            pygame.draw.circle(self.screen, Colors.KIRBY_PINK, center, radius)
        
        # Weather info at bottom
        self.draw_weather_info()
        
        # Swipe hint (only if not dragging)
        if not self.dragging and self.current_view == "art":
            self.draw_swipe_hint()
    
    def create_background_surface(self):
        """Create pre-rendered gradient background surface for performance"""
        if not self.background_dirty and self.background_surface:
            return
            
        self.background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Optimized gradient: Use fewer lines for better performance
        start_color = Colors.PRIMARY_BG
        end_color = Colors.SECONDARY_BG
        
        # Draw gradient in larger steps for performance
        step_size = 4  # Draw every 4th line, then stretch
        for y in range(0, WINDOW_HEIGHT, step_size):
            ratio = y / WINDOW_HEIGHT
            
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            
            # Draw a thicker line to fill gaps
            rect = pygame.Rect(0, y, WINDOW_WIDTH, step_size)
            pygame.draw.rect(self.background_surface, (r, g, b), rect)
        
        self.background_dirty = False
    
    def create_kirby_glow_surface(self):
        """Create pre-rendered glow effect surface for performance"""
        if not self.glow_dirty and self.kirby_glow_surface and self.kirby_image:
            return
            
        if not self.kirby_image:
            return
            
        # Create glow surface with padding for glow effect
        glow_size = self.kirby_image.get_width() + 100
        self.kirby_glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        
        center = (glow_size // 2, glow_size // 2)
        glow_colors = [Colors.KIRBY_PINK, Colors.KIRBY_LIGHT, Colors.ACCENT_LIGHT]
        
        # Pre-render glow circles with reduced alpha blending
        for i, color in enumerate(glow_colors):
            alpha = 30 - i * 8  # Reduced alpha for better performance
            glow_color = (*color, alpha)
            radius = self.kirby_image.get_width() // 2 + 15 + i * 12
            pygame.draw.circle(self.kirby_glow_surface, glow_color, center, radius)
        
        self.glow_dirty = False
    
    def draw_weather_info(self):
        """Draw compact weather info at bottom"""
        if not self.current_weather:
            return
            
        # Weather text
        temp_text = f"{self.current_weather.get('temperature', '?')}°C"
        condition_text = self.current_weather.get('condition', 'Unknown')
        
        # Temperature
        temp_surface = self.font_large.render(temp_text, True, Colors.TEXT_PRIMARY)
        temp_rect = temp_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80))
        self.screen.blit(temp_surface, temp_rect)
        
        # Condition
        condition_surface = self.font_medium.render(condition_text, True, Colors.TEXT_SECONDARY)
        condition_rect = condition_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(condition_surface, condition_rect)
        
        # Time and server status
        time_text = datetime.now().strftime("%H:%M")
        if self.server_available:
            time_text += " 🌐"  # Online indicator
        else:
            time_text += " 📡"  # Offline indicator
        time_surface = self.font_small.render(time_text, True, Colors.TEXT_SECONDARY)
        time_rect = time_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25))
        self.screen.blit(time_surface, time_rect)
    
    def draw_swipe_hint(self):
        """Draw subtle swipe hint"""
        hint_text = "← Swipe for messages"
        hint_surface = self.font_small.render(hint_text, True, Colors.TEXT_SECONDARY)
        
        # Position hint lower if there's a notification to avoid overlap
        if self.unread_count > 0:
            hint_rect = hint_surface.get_rect(right=WINDOW_WIDTH - 20, top=70)  # Below notification
        else:
            hint_rect = hint_surface.get_rect(right=WINDOW_WIDTH - 20, top=20)  # Normal position
        
        # Add subtle background
        bg_rect = hint_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (*Colors.GLASS_OVERLAY[:3], 100), bg_rect, border_radius=15)
        
        self.screen.blit(hint_surface, hint_rect)
    
    def draw_messages_view(self):
        """Draw the messages panel with scrolling support"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(Colors.PRIMARY_BG)
        self.screen.blit(overlay, (0, 0))
        
        # Title with unread count
        unread_count = self.get_unread_count()
        title_text = "💌 Messages"
        if unread_count > 0:
            title_text += f" ({unread_count} unread)"
            
        title_surface = self.font_large.render(title_text, True, Colors.TEXT_PRIMARY)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title_surface, title_rect)
        
        # Close hint
        close_hint = "Swipe left to close →"
        close_surface = self.font_small.render(close_hint, True, Colors.TEXT_SECONDARY)
        close_rect = close_surface.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(close_surface, close_rect)
        
        # Messages list area
        messages_area_top = 120
        messages_area_height = WINDOW_HEIGHT - 200  # Leave space for title and debug info
        message_height = 80
        
        # Calculate scrolling parameters
        all_messages = list(reversed(self.messages))  # Newest first
        total_messages_height = len(all_messages) * message_height
        self.max_scroll_y = max(0, total_messages_height - messages_area_height)
        
        # Ensure scroll position is within bounds
        self.message_scroll_y = max(0, min(self.message_scroll_y, self.max_scroll_y))
        
        # Create or reuse clipping surface for messages
        if self.messages_dirty or not hasattr(self, 'messages_clip_surface'):
            self.messages_clip_surface = pygame.Surface((WINDOW_WIDTH, messages_area_height))
        
        self.messages_clip_surface.fill(Colors.PRIMARY_BG)
        
        if not all_messages:
            # No messages to show
            no_msg_text = "No messages yet..."
            no_msg_surface = self.font_medium.render(no_msg_text, True, Colors.TEXT_SECONDARY)
            no_msg_rect = no_msg_surface.get_rect(center=(WINDOW_WIDTH // 2, 40))
            self.messages_clip_surface.blit(no_msg_surface, no_msg_rect)
        else:
            # Draw all messages with scroll offset
            for i, message in enumerate(all_messages):
                y = i * message_height - self.message_scroll_y
                
                # Skip messages that are completely outside the visible area
                if y + message_height < 0 or y > messages_area_height:
                    continue
                
                # Message background - use different color for unread
                msg_rect = pygame.Rect(40, y, WINDOW_WIDTH - 80, message_height - 10)
                
                # Check if message is unread
                msg_id = message.get('id', '')
                is_unread = msg_id and msg_id not in self.viewed_message_ids
                
                if is_unread:
                    # Bright background for unread messages
                    pygame.draw.rect(self.messages_clip_surface, Colors.KIRBY_PINK, msg_rect, border_radius=10)
                    pygame.draw.rect(self.messages_clip_surface, Colors.ACCENT, msg_rect, width=3, border_radius=10)
                else:
                    # Normal background for read messages
                    pygame.draw.rect(self.messages_clip_surface, Colors.ACCENT_LIGHT, msg_rect, border_radius=10)
                    pygame.draw.rect(self.messages_clip_surface, Colors.ACCENT, msg_rect, width=2, border_radius=10)
                
                # Message text (truncated)
                msg_text = message.get('message', '')[:60] + ('...' if len(message.get('message', '')) > 60 else '')
                author_text = f"- {message.get('name', 'Anonymous')}"
                
                # Add unread indicator to text
                if is_unread:
                    author_text += " 🔴"
                
                msg_surface = self.font_medium.render(msg_text, True, Colors.TEXT_PRIMARY)
                author_surface = self.font_small.render(author_text, True, Colors.TEXT_SECONDARY)
                
                self.messages_clip_surface.blit(msg_surface, (msg_rect.x + 15, msg_rect.y + 10))
                self.messages_clip_surface.blit(author_surface, (msg_rect.x + 15, msg_rect.y + 40))
        
        # Blit the clipped messages surface to the main screen
        self.screen.blit(self.messages_clip_surface, (0, messages_area_top))
        
        # Draw scroll indicator if there are more messages
        if self.max_scroll_y > 0:
            # Scroll bar background
            scrollbar_x = WINDOW_WIDTH - 20
            scrollbar_y = messages_area_top
            scrollbar_height = messages_area_height
            scrollbar_width = 8
            
            pygame.draw.rect(self.screen, (*Colors.TEXT_SECONDARY, 100), 
                           (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), 
                           border_radius=4)
            
            # Scroll thumb
            thumb_height = max(20, scrollbar_height * messages_area_height / total_messages_height)
            thumb_y = scrollbar_y + (self.message_scroll_y / self.max_scroll_y) * (scrollbar_height - thumb_height)
            
            pygame.draw.rect(self.screen, Colors.ACCENT, 
                           (scrollbar_x, thumb_y, scrollbar_width, thumb_height), 
                           border_radius=4)
            
            # Scroll hint
            if len(all_messages) > 6:  # Only show hint if there are many messages
                scroll_hint = f"↕ Scroll to see all {len(all_messages)} messages"
                scroll_surface = self.font_small.render(scroll_hint, True, Colors.TEXT_SECONDARY)
                scroll_rect = scroll_surface.get_rect(center=(WINDOW_WIDTH // 2, messages_area_top + messages_area_height + 10))
                self.screen.blit(scroll_surface, scroll_rect)
        
        # Debug info at bottom
        debug_text = f"Total messages: {len(self.messages)} | Unread: {self.unread_count}"
        debug_surface = self.font_small.render(debug_text, True, Colors.TEXT_SECONDARY)
        debug_rect = debug_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        self.screen.blit(debug_surface, debug_rect)
    
    def draw_notification(self):
        """Draw unread message notification"""
        if self.unread_count <= 0 or self.current_view == "messages":
            return
        
        # Debug: Print when we're about to show notification (remove this later)
        if not hasattr(self, '_last_notification_debug') or self.unread_count != self._last_notification_debug:
            print(f"🔔 Drawing notification badge: {self.unread_count} unread")
            self._last_notification_debug = self.unread_count
            
        # Notification badge in top-right
        badge_x, badge_y = WINDOW_WIDTH - 60, 30
        badge_radius = 20
        
        # Badge background
        pygame.draw.circle(self.screen, Colors.NOTIFICATION, (badge_x, badge_y), badge_radius)
        pygame.draw.circle(self.screen, Colors.PRIMARY_BG, (badge_x, badge_y), badge_radius, width=3)
        
        # Badge text
        badge_text = str(min(self.unread_count, 99))
        badge_surface = self.font_small.render(badge_text, True, Colors.PRIMARY_BG)
        badge_rect = badge_surface.get_rect(center=(badge_x, badge_y))
        self.screen.blit(badge_surface, badge_rect)
    
    def update(self):
        """Update app state with synchronized polling"""
        self.time = pygame.time.get_ticks()
        self.update_animation()
        
        # Unified update check (every 30 seconds)
        if self.time - self.last_update > 30000:
            old_message_count = len(self.messages)
            
            # Try server first, fallback to local file
            if self.server_available and self.load_messages_from_server():
                # Server success - still load weather data (quietly)
                self.load_weather_data()
                self.load_kirby_image(quiet=True)
            else:
                # Server failed or unavailable - try local file and retry server connection
                self.load_all_data(quiet=True)
                if not self.server_available:
                    self.check_server_availability()
            
            new_message_count = len(self.messages)
            
            # Only print updates when there are actual changes
            if new_message_count > old_message_count:
                print(f"📬 Found {new_message_count - old_message_count} new messages!")
            
            self.last_update = self.time
    
    def draw(self):
        """Main draw function with optimized rendering"""
        # Draw main content
        self.draw_art_view()
        
        # Draw messages panel if needed
        if self.panel_offset > 0:
            # Create or reuse messages surface only when dirty
            if self.messages_dirty or not hasattr(self, 'cached_messages_surface'):
                self.cached_messages_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                self.cached_messages_surface.set_alpha(255)  # Ensure full opacity
                self.cached_messages_surface.fill(Colors.PRIMARY_BG)
                
                # Draw messages on cached surface
                temp_screen = self.screen
                self.screen = self.cached_messages_surface
                self.draw_messages_view()
                self.screen = temp_screen
                self.messages_dirty = False
            
            # Blit cached surface with offset for sliding effect
            messages_rect = (WINDOW_WIDTH - self.panel_offset, 0)
            self.screen.blit(self.cached_messages_surface, messages_rect)
        
        # Draw notification badge
        self.draw_notification()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        print("🌸 Starting Kirby Touch Weather Display!")
        print("👆 Touch/drag to navigate, swipe right for messages")
        print("🎮 Keys: R=refresh, N=simulate new message, M=toggle messages")
        print("📜 In messages: UP/DOWN arrows or touch-drag to scroll, ESC=exit")
        if self.server_available:
            print(f"🌐 Real-time updates enabled from {self.server_url}")
        else:
            print("📡 Using local messages only (server not available)")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_RIGHT and self.current_view == "art":
                        self.switch_to_messages()
                    elif event.key == pygame.K_LEFT and self.current_view == "messages":
                        self.switch_to_art()
                    elif event.key == pygame.K_r:
                        print("🔄 Manual refresh...")
                        self.load_all_data()
                    elif event.key == pygame.K_n:
                        # Simulate new message for testing
                        print("📬 Simulating new message...")
                        self.simulate_new_message()
                    elif event.key == pygame.K_m:
                        # Quick toggle to messages view for testing
                        if self.current_view == "art":
                            print("📱 Quick switch to messages view")
                            self.switch_to_messages()
                        else:
                            print("📱 Quick switch to art view")  
                            self.switch_to_art()
                    elif event.key == pygame.K_UP and self.current_view == "messages":
                        # Scroll up in messages
                        self.message_scroll_y = max(0, self.message_scroll_y - 40)
                    elif event.key == pygame.K_DOWN and self.current_view == "messages":
                        # Scroll down in messages
                        self.message_scroll_y = min(self.max_scroll_y, self.message_scroll_y + 40)
                
                # Touch/mouse events
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_touch_start(event.pos[0], event.pos[1])
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self.handle_touch_move(event.pos[0], event.pos[1])
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.handle_touch_end()
            
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
        
        print("👋 Goodbye!")
        pygame.quit()

if __name__ == "__main__":
    try:
        app = TouchWeatherDisplay()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        pygame.quit()
        sys.exit()
