#!/usr/bin/env python3
"""
Kirby Weather Display - Milestone 2
Display Kirby placeholder with weather information using pygame
"""

import pygame
import sys
import os
import time
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Initialize pygame
pygame.init()

# Constants
INITIAL_WINDOW_WIDTH = 800
INITIAL_WINDOW_HEIGHT = 600
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 300
BACKGROUND_COLOR = (135, 206, 235)  # Sky blue
KIRBY_COLOR = (255, 182, 193)       # Pink
TEXT_COLOR = (255, 255, 255)        # White
SHADOW_COLOR = (0, 0, 0)            # Black

# Font config (quiet logs and caching)
DEBUG_FONT_LOG = False
_FONT_CACHE = {}
_FONT_BASE = None  # either a file path or a system font name
_FONT_BASE_IS_FILE = False
_FONT_INFO_PRINTED = False

def _resolve_kirby_font_base():
    """Pick the best available Kirby-like font once per run.
    Priority: env override -> local Kirby TTF -> Kirby-like names -> system rounded fonts -> default.
    """
    global _FONT_BASE, _FONT_BASE_IS_FILE
    if _FONT_BASE is not None:
        return

    # Environment override
    env_path = os.getenv("KIRBY_FONT_PATH")
    if env_path and os.path.exists(env_path):
        _FONT_BASE = env_path
        _FONT_BASE_IS_FILE = True
        _print_font_info_once()
        return

    # Try local Kirby fonts (you can drop a Kirby TTF into fonts/)
    local_candidates = [
        "fonts/kirby.ttf",
        "fonts/Kirby.ttf",
        "fonts/KIRBY.TTF",
    "fonts/kirby-classic.ttf",
    "fonts/Kirby-Classic.ttf",
        "fonts/kirby_classic.ttf",
        "fonts/KirbyClassic.ttf",
        "fonts/Nintendo.ttf",
        "fonts/nintendo.ttf",
        "assets/fonts/kirby.ttf",
        "kirby.ttf",
    ]
    for path in local_candidates:
        if os.path.exists(path):
            _FONT_BASE = path
            _FONT_BASE_IS_FILE = True
            _print_font_info_once()
            return

    # System fonts (lowercase names per pygame)
    system_candidates = [
        "comicsansms",
        "comic",
        "arialroundedmtbold",
        "trebuchetms",
        "verdana",
        "dejavusans",
        "liberation",
        "ubuntu",
    ]
    available = set(pygame.font.get_fonts())
    for name in system_candidates:
        if name in available:
            _FONT_BASE = name
            _FONT_BASE_IS_FILE = False
            _print_font_info_once()
            return

    # Default
    _FONT_BASE = None
    _FONT_BASE_IS_FILE = False
    _print_font_info_once()

def _print_font_info_once():
    """Print a single confirmation of the chosen font without spamming."""
    global _FONT_INFO_PRINTED
    if _FONT_INFO_PRINTED:
        return
    if _FONT_BASE and _FONT_BASE_IS_FILE:
        print(f"🎨 Kirby font: file -> {_FONT_BASE}")
    elif _FONT_BASE and not _FONT_BASE_IS_FILE:
        print(f"🎨 Kirby font: system -> {_FONT_BASE}")
    else:
        print("🎨 Kirby font: pygame default (add fonts/kirby.ttf or set KIRBY_FONT_PATH)")
    _FONT_INFO_PRINTED = True

def load_kirby_font(size):
    """Load Kirby-style font at a given size with caching and quiet logs."""
    _resolve_kirby_font_base()
    key = (size, _FONT_BASE, _FONT_BASE_IS_FILE)
    cached = _FONT_CACHE.get(key)
    if cached:
        return cached

    try:
        if _FONT_BASE and _FONT_BASE_IS_FILE:
            font = pygame.font.Font(_FONT_BASE, size)
        elif _FONT_BASE and not _FONT_BASE_IS_FILE:
            font = pygame.font.SysFont(_FONT_BASE, size)
        else:
            font = pygame.font.Font(None, size)
    except Exception:
        font = pygame.font.Font(None, size)

    _FONT_CACHE[key] = font
    return font

def get_fitting_font_and_surface(text: str, base_size: int, max_width: int, color=TEXT_COLOR):
    """Return a (font, surface) tuple sized so the text fits within max_width.

    Uses a quick two-step strategy to minimize iterations and avoid log spam.
    """
    # First try base size
    font = load_kirby_font(base_size)
    surf = font.render(text, True, color)
    w = surf.get_width()
    if w <= max_width:
        return font, surf

    # Estimate a better size proportionally
    if w > 0:
        est = max(int(base_size * max_width / w), 12)
    else:
        est = base_size

    # Clamp and render once more
    est = min(est, base_size)
    font2 = load_kirby_font(est)
    surf2 = font2.render(text, True, color)
    w2 = surf2.get_width()
    if w2 <= max_width or est <= 12:
        return font2, surf2

    # Final small decrement loop (few steps max)
    size = est
    while size > 12 and surf2.get_width() > max_width:
        size -= 2
        font2 = load_kirby_font(size)
        surf2 = font2.render(text, True, color)
    return font2, surf2

def get_weather_data(city="Lethbridge, Alberta"):
    """Fetch weather data using WeatherAPI - always for Lethbridge, Alberta"""
    api_key = os.getenv('WEATHERAPI_KEY')
    
    if not api_key:
        print("❌ Error: No WeatherAPI key found!")
        return None
    
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': api_key,
        'q': city,
        'aqi': 'no'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'condition': data['current']['condition']['text'],
            'temperature': round(data['current']['temp_c']),
            'city': data['location']['name'],
            'country': data['location']['country'],
            'region': data['location']['region']
        }
    except Exception as e:
        print(f"❌ Error fetching weather: {e}")
        return None

def get_latest_message():
    """Fetch the latest message from the web server"""
    try:
        response = requests.get("http://localhost:5000/api/latest", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('message'):
                return data
        return None
    except Exception as e:
        if DEBUG_FONT_LOG:  # Only show debug if enabled
            print(f"🔗 Message fetch failed: {e}")
        return None

def get_all_messages():
    """Fetch all messages from the web server"""
    try:
        response = requests.get("http://localhost:5000/api/messages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # The API returns {"messages": [...]} so extract the messages array
            if isinstance(data, dict) and 'messages' in data:
                messages = data['messages']
                if isinstance(messages, list) and len(messages) > 0:
                    return messages
        return []
    except Exception as e:
        if DEBUG_FONT_LOG:  # Only show debug if enabled
            print(f"🔗 All messages fetch failed: {e}")
        return []

def get_season_from_temperature(temperature):
    """
    Determine season based on Lethbridge, Alberta temperature ranges
    Based on typical seasonal temperatures for southern Alberta
    """
    if temperature >= 20:
        return 'summer'      # 20°C+ (68°F+) - Hot summer days
    elif temperature >= 10:
        return 'spring'      # 10-19°C (50-66°F) - Mild spring/fall weather  
    elif temperature >= 0:
        return 'fall'        # 0-9°C (32-48°F) - Cool fall weather
    else:
        return 'winter'      # Below 0°C (32°F) - Cold winter weather

def load_kirby_image_by_temperature(temperature, weather_condition="default", max_width=None, max_height=None):
    """Load Kirby image based on temperature (season) with cycling/random selection"""
    import glob
    import random
    import time
    
    # Use default sizes if not provided
    if max_width is None:
        max_width = INITIAL_WINDOW_WIDTH - 100
    if max_height is None:
        max_height = INITIAL_WINDOW_HEIGHT - 250
    
    # Get the season based on temperature
    season = get_season_from_temperature(temperature)
    
    print(f"🌡️ Temperature: {temperature}°C -> Season: {season.title()}")
    
    # Look for images in the seasonal folder
    season_folder = f"images/{season}"
    
    # Get all images from the season folder
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']
    season_images = []
    
    for ext in image_extensions:
        season_images.extend(glob.glob(f"{season_folder}/{ext}"))
        season_images.extend(glob.glob(f"{season_folder}/{ext.upper()}"))
    
    if season_images:
        # Option 1: Cycle through images based on time (changes every 30 seconds)
        # This ensures you see different images if you keep the app open
        cycle_interval = 30  # seconds
        current_time = int(time.time())
        image_index = (current_time // cycle_interval) % len(season_images)
        selected_image = season_images[image_index]
        
        # Option 2: Uncomment this for random selection instead
        # selected_image = random.choice(season_images)
        
        try:
            kirby_image = pygame.image.load(selected_image)
            
            # Scale to fit nicely in the window while maintaining aspect ratio
            img_rect = kirby_image.get_rect()
            
            # Use the provided max dimensions
            if img_rect.width > max_width or img_rect.height > max_height:
                scale_factor = min(max_width/img_rect.width, max_height/img_rect.height)
                new_width = int(img_rect.width * scale_factor)
                new_height = int(img_rect.height * scale_factor)
                kirby_image = pygame.transform.scale(kirby_image, (new_width, new_height))
            
            image_name = selected_image.split('/')[-1]
            print(f"✅ Loaded {season} Kirby image: {image_name} ({len(season_images)} available)")
            return kirby_image
            
        except Exception as e:
            print(f"❌ Failed to load {selected_image}: {e}")
    
    # Fallback: try to load from main images folder
    print(f"ℹ️ No images found in {season_folder}, trying main images folder...")
    
    # Get all images from main images folder as fallback
    fallback_images = []
    for ext in image_extensions:
        fallback_images.extend(glob.glob(f"images/{ext}"))
        fallback_images.extend(glob.glob(f"images/{ext.upper()}"))
    
    if fallback_images:
        # Apply cycling logic to fallback images too
        cycle_interval = 30  # seconds
        current_time = int(time.time())
        image_index = (current_time // cycle_interval) % len(fallback_images)
        fallback_image = fallback_images[image_index]
        
        try:
            kirby_image = pygame.image.load(fallback_image)
            
            # Scale appropriately using provided max dimensions
            img_rect = kirby_image.get_rect()
            
            if img_rect.width > max_width or img_rect.height > max_height:
                scale_factor = min(max_width/img_rect.width, max_height/img_rect.height)
                new_width = int(img_rect.width * scale_factor)
                new_height = int(img_rect.height * scale_factor)
                kirby_image = pygame.transform.scale(kirby_image, (new_width, new_height))
            
            print(f"✅ Using fallback image: {fallback_image.split('/')[-1]} ({len(fallback_images)} available)")
            return kirby_image
            
        except Exception as e:
            print(f"❌ Failed to load fallback image: {e}")
    
    print(f"ℹ️ No images found, will draw placeholder circle for {season}")
    return None

def draw_kirby_placeholder(screen, x, y, radius=100):
    """Draw a pink Kirby placeholder circle with simple features"""
    # Main body (pink circle)
    pygame.draw.circle(screen, KIRBY_COLOR, (x, y), radius)
    
    # Eyes (black ovals)
    eye_width, eye_height = 15, 25
    left_eye_x, left_eye_y = x - 25, y - 20
    right_eye_x, right_eye_y = x + 25, y - 20
    
    pygame.draw.ellipse(screen, (0, 0, 0), (left_eye_x - eye_width//2, left_eye_y - eye_height//2, eye_width, eye_height))
    pygame.draw.ellipse(screen, (0, 0, 0), (right_eye_x - eye_width//2, right_eye_y - eye_height//2, eye_width, eye_height))
    
    # Mouth (small pink oval, slightly darker)
    mouth_color = (255, 150, 180)
    pygame.draw.ellipse(screen, mouth_color, (x - 10, y + 10, 20, 15))
    
    # Cheek blush (light pink circles)
    blush_color = (255, 200, 220)
    pygame.draw.circle(screen, blush_color, (x - 60, y + 10), 15)
    pygame.draw.circle(screen, blush_color, (x + 60, y + 10), 15)

def draw_text_with_shadow(screen, text, font, x, y, text_color=TEXT_COLOR, shadow_color=SHADOW_COLOR):
    """Draw text with a shadow for better readability"""
    # Draw shadow first (offset by 2 pixels)
    shadow_surface = font.render(text, True, shadow_color)
    screen.blit(shadow_surface, (x + 2, y + 2))
    
    # Draw main text
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (x, y))
    
    return text_surface.get_width()

def get_dynamic_sizes(window_width, window_height):
    """Calculate dynamic sizes based on current window dimensions"""
    # Scale factors based on window size
    width_scale = window_width / INITIAL_WINDOW_WIDTH
    height_scale = window_height / INITIAL_WINDOW_HEIGHT
    scale = min(width_scale, height_scale)  # Use the smaller scale to maintain proportions
    
    return {
        'title_font_size': max(int(48 * scale), 24),  # Increased minimum
        'temp_font_size': max(int(72 * scale), 36),   # Increased minimum
        'header_font_size': max(int(28 * scale), 20), # Increased minimum
        'message_font_size': max(int(36 * scale), 24), # Increased minimum
        'counter_font_size': max(int(20 * scale), 16), # Increased minimum
        'side_margin': max(int(20 * scale), 15),
        'top_margin': max(int(20 * scale), 15),
        'kirby_max_width': window_width - max(int(100 * scale), 80),
        'kirby_max_height': max(window_height - max(int(250 * scale), 200), 150), # Ensure minimum space
        'kirby_radius': max(int(100 * scale), 60)
    }

def main():
    """Main pygame loop"""
    print("🎮 Starting Kirby Weather Display for Lethbridge, Alberta!")
    
    # Always use Lethbridge, Alberta
    city = "Lethbridge, Alberta"
    
    weather_data = get_weather_data(city)
    if not weather_data:
        # Fallback data for demo
        weather_data = {
            'condition': 'Demo Mode',
            'temperature': 20,
            'city': 'Lethbridge',
            'country': 'Canada',
            'region': 'Alberta'
        }
    
    # Initialize display with resizable window
    screen = pygame.display.set_mode((INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Kirby Weather Display - Lethbridge, AB (Resizable)")
    clock = pygame.time.Clock()
    
    # Current window dimensions (will be updated on resize)
    current_width = INITIAL_WINDOW_WIDTH
    current_height = INITIAL_WINDOW_HEIGHT
    
    # Load Kirby-style fonts (will be recalculated on resize)
    sizes = get_dynamic_sizes(current_width, current_height)
    
    # Load Kirby image based on temperature/season
    kirby_image = load_kirby_image_by_temperature(
        weather_data['temperature'], 
        weather_data['condition'],
        sizes['kirby_max_width'],
        sizes['kirby_max_height']
    )
    
    # Track last image reload time for cycling
    last_image_reload = time.time()
    image_cycle_interval = 30  # seconds
    
    # Track message fetching and rotation
    last_message_fetch = 0
    message_fetch_interval = 10  # Check for new messages every 10 seconds
    all_messages = []  # Store all messages
    current_message_index = 0  # Index of currently displayed message
    current_message = None  # Currently displayed message
    message_display_start = 0
    message_display_duration = 30  # Show each message for 30 seconds (same as image cycle)
    last_message_rotation = 0
    message_rotation_interval = 30  # Rotate messages every 30 seconds
    
    # Main game loop
    running = True
    while running:
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                new_width = max(event.w, MIN_WINDOW_WIDTH)
                new_height = max(event.h, MIN_WINDOW_HEIGHT)
                screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                current_width = new_width
                current_height = new_height
                sizes = get_dynamic_sizes(current_width, current_height)
                # Reload image with new size constraints
                kirby_image = load_kirby_image_by_temperature(
                    weather_data['temperature'], 
                    weather_data['condition'],
                    sizes['kirby_max_width'],
                    sizes['kirby_max_height']
                )
                print(f"🔄 Window resized to {new_width}x{new_height}")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    # Refresh weather data
                    print("🔄 Refreshing weather data...")
                    new_data = get_weather_data(city)
                    if new_data:
                        weather_data = new_data
                        sizes = get_dynamic_sizes(current_width, current_height)
                        # Reload image for new temperature/season
                        kirby_image = load_kirby_image_by_temperature(
                            weather_data['temperature'], 
                            weather_data['condition'],
                            sizes['kirby_max_width'],
                            sizes['kirby_max_height']
                        )
                        last_image_reload = current_time
        
        # Auto-cycle images every 30 seconds
        if current_time - last_image_reload >= image_cycle_interval:
            sizes = get_dynamic_sizes(current_width, current_height)
            kirby_image = load_kirby_image_by_temperature(
                weather_data['temperature'], 
                weather_data['condition'],
                sizes['kirby_max_width'],
                sizes['kirby_max_height']
            )
            last_image_reload = current_time
        
        # Check for new messages periodically
        if current_time - last_message_fetch >= message_fetch_interval:
            new_messages = get_all_messages()
            if new_messages:
                # Check if we have new messages by comparing list length or latest message
                if len(new_messages) != len(all_messages) or (new_messages and all_messages and new_messages[-1] != all_messages[-1]):
                    all_messages = new_messages
                    print(f"📬 Updated message list: {len(all_messages)} messages available")
            last_message_fetch = current_time
        
        # Rotate through messages every 30 seconds (sync with image cycling)
        if all_messages and current_time - last_message_rotation >= message_rotation_interval:
            current_message_index = (current_message_index + 1) % len(all_messages)
            last_message_rotation = current_time
            current_message = all_messages[current_message_index]
            username = current_message.get('username', 'Anonymous')
            print(f"💌 Showing message {current_message_index + 1}/{len(all_messages)} from {username}")
        
        # Initialize message display if we have messages but no current message
        if all_messages and current_message_index < len(all_messages):
            current_message = all_messages[current_message_index]
        else:
            current_message = None
        
        # Fill background
        screen.fill(BACKGROUND_COLOR)

        # Get dynamic sizes for current window
        sizes = get_dynamic_sizes(current_width, current_height)
        avail_width = current_width - sizes['side_margin'] * 2

        # Draw title - auto-fit and centered
        title_text = f"Kirby Weather — {weather_data['city']}, {weather_data.get('region', 'AB')}"
        dyn_title_font, title_surface = get_fitting_font_and_surface(title_text, sizes['title_font_size'], avail_width)
        title_x = (current_width - title_surface.get_width()) // 2
        title_y = sizes['top_margin']
        draw_text_with_shadow(screen, title_text, dyn_title_font, title_x, title_y)

        # Draw Kirby (image or placeholder) - centered under title
        kirby_center_y = current_height // 2 - int(30 * (current_height / INITIAL_WINDOW_HEIGHT))
        if kirby_image:
            kirby_rect = kirby_image.get_rect(center=(current_width // 2, kirby_center_y))
            screen.blit(kirby_image, kirby_rect)
            text_start_y = kirby_rect.bottom + int(24 * (current_height / INITIAL_WINDOW_HEIGHT))
        else:
            draw_kirby_placeholder(screen, current_width // 2, kirby_center_y, sizes['kirby_radius'])
            text_start_y = kirby_center_y + sizes['kirby_radius'] + int(24 * (current_height / INITIAL_WINDOW_HEIGHT))

        # Temperature and condition on same line - auto-fit and centered
        temp_condition_text = f"{weather_data['temperature']}°C • {weather_data['condition']}"
        dyn_temp_font, temp_surface = get_fitting_font_and_surface(temp_condition_text, sizes['temp_font_size'], avail_width)
        temp_x = (current_width - temp_surface.get_width()) // 2
        temp_y = text_start_y
        draw_text_with_shadow(screen, temp_condition_text, dyn_temp_font, temp_x, temp_y)

        # Display message if we have one
        if current_message:
            message_y = temp_y + temp_surface.get_height() + 30
            
            # Extract message data safely
            username = current_message.get('username', 'Anonymous')
            if not isinstance(username, str):
                username = str(username) if username else 'Anonymous'
            username = username.strip() if username else 'Anonymous'
            
            message_text = current_message.get('message', '')
            if not isinstance(message_text, str):
                message_text = str(message_text)
            
            # Format timestamp nicely - just hour:minute AM/PM
            timestamp = current_message.get('timestamp', '')
            formatted_time = ""
            if timestamp:
                try:
                    # Parse ISO timestamp and format nicely
                    if 'T' in timestamp:
                        date_part, time_part = timestamp.split('T')
                        time_only = time_part.split('.')[0]  # Remove microseconds
                        # Convert to 12-hour format
                        hour, minute, second = time_only.split(':')
                        hour_int = int(hour)
                        ampm = "AM" if hour_int < 12 else "PM"
                        if hour_int == 0:
                            hour_int = 12
                        elif hour_int > 12:
                            hour_int -= 12
                        formatted_time = f"{hour_int}:{minute} {ampm}"
                except Exception as e:
                    formatted_time = "recently"
            else:
                formatted_time = "recently"
            
            # Create header with username and time - clean format
            if not username or username.strip() == '':
                header_text = f"💌 Message for Kirby • {formatted_time}"
            else:
                header_text = f"💌 From {username} • {formatted_time}"
            
            dyn_header_font, header_surface = get_fitting_font_and_surface(header_text, sizes['header_font_size'], avail_width, (200, 200, 255))
            header_x = (current_width - header_surface.get_width()) // 2
            draw_text_with_shadow(screen, header_text, dyn_header_font, header_x, message_y, (200, 200, 255), (0, 0, 0))
            
            # Add message counter as a small line below the header if multiple messages
            message_text_y = message_y + header_surface.get_height() + int(15 * (current_height / INITIAL_WINDOW_HEIGHT))
            if len(all_messages) > 1:
                counter_text = f"Message {current_message_index + 1} of {len(all_messages)}"
                counter_font, counter_surface = get_fitting_font_and_surface(counter_text, sizes['counter_font_size'], avail_width, (150, 150, 200))
                counter_x = (current_width - counter_surface.get_width()) // 2
                draw_text_with_shadow(screen, counter_text, counter_font, counter_x, message_text_y, (150, 150, 200), (0, 0, 0))
                message_text_y += counter_surface.get_height() + int(10 * (current_height / INITIAL_WINDOW_HEIGHT))
            
            # Message text with better formatting
            
            # Handle long messages by wrapping
            words = message_text.split()
            lines = []
            current_line = ""
            test_font = load_kirby_font(sizes['message_font_size'])  # Use dynamic size
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surface = test_font.render(test_line, True, TEXT_COLOR)
                if test_surface.get_width() <= avail_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        lines.append(word)  # Single long word
            
            if current_line:
                lines.append(current_line)
            
            # Draw message lines with bright yellow color for visibility
            for i, line in enumerate(lines[:3]):  # Max 3 lines
                dyn_msg_font, msg_surface = get_fitting_font_and_surface(line, sizes['message_font_size'], avail_width, (255, 255, 150))  # Bright yellow
                msg_x = (current_width - msg_surface.get_width()) // 2
                line_y = message_text_y + i * (msg_surface.get_height() + int(8 * (current_height / INITIAL_WINDOW_HEIGHT)))
                draw_text_with_shadow(screen, line, dyn_msg_font, msg_x, line_y, (255, 255, 150), (0, 0, 0))

        # Instructions removed but functionality preserved
        
        # Instructions removed but functionality preserved
        
        # Update display
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    # Cleanup
    pygame.quit()
    print("👋 Thanks for using Kirby Weather Display!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        pygame.quit()
        sys.exit(1)
