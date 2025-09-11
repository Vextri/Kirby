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

# Load environment variables
load_dotenv()

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
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

def load_kirby_image_by_temperature(temperature, weather_condition="default"):
    """Load Kirby image based on temperature (season) with cycling/random selection"""
    import glob
    import random
    import time
    
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
            
            # Calculate max size based on window dimensions (leave room for text)
            max_width = WINDOW_WIDTH - 100  # 50px padding on each side
            max_height = WINDOW_HEIGHT - 250  # Leave room for title and text below
            
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
            
            # Scale appropriately
            img_rect = kirby_image.get_rect()
            max_width = WINDOW_WIDTH - 100
            max_height = WINDOW_HEIGHT - 250
            
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
    
    # Initialize display
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Kirby Weather Display - Lethbridge, AB")
    clock = pygame.time.Clock()
    
    # Load Kirby-style fonts
    title_font = load_kirby_font(48)
    temp_font = load_kirby_font(72)
    info_font = load_kirby_font(36)
    small_font = load_kirby_font(24)
    
    # Load Kirby image based on temperature/season
    kirby_image = load_kirby_image_by_temperature(weather_data['temperature'], weather_data['condition'])
    
    # Track last image reload time for cycling
    last_image_reload = time.time()
    image_cycle_interval = 30  # seconds
    
    # Main game loop
    running = True
    while running:
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    # Refresh weather data
                    print("🔄 Refreshing weather data...")
                    new_data = get_weather_data(city)
                    if new_data:
                        weather_data = new_data
                        # Reload image for new temperature/season
                        kirby_image = load_kirby_image_by_temperature(weather_data['temperature'], weather_data['condition'])
                        last_image_reload = current_time
        
        # Auto-cycle images every 30 seconds
        if current_time - last_image_reload >= image_cycle_interval:
            kirby_image = load_kirby_image_by_temperature(weather_data['temperature'], weather_data['condition'])
            last_image_reload = current_time
        
        # Fill background
        screen.fill(BACKGROUND_COLOR)

        # Safe margins and available width for text
        side_margin = 20
        top_margin = 20
        avail_width = WINDOW_WIDTH - side_margin * 2

        # Draw title - auto-fit and centered
        title_text = f"Kirby Weather — {weather_data['city']}, {weather_data.get('region', 'AB')}"
        dyn_title_font, title_surface = get_fitting_font_and_surface(title_text, 48, avail_width)
        title_x = (WINDOW_WIDTH - title_surface.get_width()) // 2
        title_y = top_margin
        draw_text_with_shadow(screen, title_text, dyn_title_font, title_x, title_y)

        # Draw Kirby (image or placeholder) - centered under title
        kirby_center_y = WINDOW_HEIGHT // 2 - 30
        if kirby_image:
            kirby_rect = kirby_image.get_rect(center=(WINDOW_WIDTH // 2, kirby_center_y))
            screen.blit(kirby_image, kirby_rect)
            text_start_y = kirby_rect.bottom + 24
        else:
            draw_kirby_placeholder(screen, WINDOW_WIDTH // 2, kirby_center_y, 100)
            text_start_y = kirby_center_y + 100 + 24

        # Temperature and condition on same line - auto-fit and centered
        temp_condition_text = f"{weather_data['temperature']}°C • {weather_data['condition']}"
        dyn_temp_font, temp_surface = get_fitting_font_and_surface(temp_condition_text, 72, avail_width)
        temp_x = (WINDOW_WIDTH - temp_surface.get_width()) // 2
        temp_y = text_start_y
        draw_text_with_shadow(screen, temp_condition_text, dyn_temp_font, temp_x, temp_y)

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
