# Kirby Modern Display - New Layout Guide

## Overview
The UI has been reorganized to match the style shown in the Hamlet poster, with a large focal point (Kirby) on the left and organized UI elements on the right.

## Layout Structure

```
┌─────────────────────────────────────────────────────┐
│  LEFT SECTION (55%)        │  RIGHT SECTION (45%)   │
│                            │                        │
│                            ├─ [  DATE/TIME  ]      │
│                            │   (MM/YYYY format)     │
│                            │                        │
│     KIRBY IMAGE            ├─ [COMMUNITY MESSAGE]   │
│     (Large Focal           │   Community Message    │
│      Point Center)         │   From: Username       │
│                            │                        │
│                            ├─ [EMULATION STATION]   │
│                            │   🎮 Vertical Layout   │
│                            │   Launch Games         │
│                            │                        │
│                            ├─ [STATS BOX] ☀️        │
│                            │   Temperature, Weather │
│                            │   Humidity, Wind Speed │
│                            │                        │
│                            │  [K│]  VERTICAL       │
│                            │  [I│]  TITLE          │
│                            │  [R│]  SIDEBAR        │
│                            │  [B│]  (Right Edge)   │
│                            │  [Y│]                 │
└─────────────────────────────────────────────────────┘
```

## Component Details

### 1. Left Section (55% width)
- **Kirby Image**: The main focal point, centered vertically
- Takes up most of the left side with floating animation
- Rainbow glow effect around Kirby

### 2. Right Section (45% width) - Top to Bottom

#### Date Header
- **Position**: Top of right section
- **Format**: MM/YYYY (e.g., "11/2025")
- **Style**: Glass card with pink border
- **Height**: ~50px scaled

#### Community Message Card
- **Title**: "💌 Community Message"
- **Content**: Current message from the messages.json file
- **Features**: 
  - Shows message count (e.g., "1/5")
  - Shows new message indicator 🆕 if new messages exist
  - Shows unread indicator 🔴 for unread messages
  - Click to cycle through messages
- **Height**: ~120px scaled

#### EmulationStation Button
- **Title**: "🎮 EmulationStation"
- **Subtitle**: "Launch Games"
- **Style**: Animated pulsing border, glass background
- **Action**: Click to launch EmulationStation
- **Height**: ~80px scaled

#### Stats Box (Weather Card)
- **Content**: Weather information
  - Temperature (large)
  - Weather condition (sunny, cloudy, etc.)
  - Humidity percentage
  - Wind speed
  - Location
- **Style**: Similar to community message card with glass effect
- **Height**: ~100px scaled

#### Vertical Title Sidebar (Right Edge)
- **Width**: ~60px scaled
- **Text**: "Kirby" displayed vertically
- **Style**: Glass background with pink tint
- **Position**: Right edge, spans full height
- **Effect**: Creates a vertical accent frame

## Color Scheme

- **Background**: Gradient (light pink to cream to light blue)
- **Cards**: Glass morphism effect with pink tint
- **Borders**: Pink accents (#FFB8C1)
- **Text Primary**: Warm brown (#8B4513)
- **Text Accent**: Hot pink (#FF69B4)
- **Kirby Pink**: #FFB6C1

## Responsive Design

The layout scales based on window size:
- **Minimum**: 600x360
- **Default**: 800x480
- **Scalable**: Resizable window mode or fullscreen

All elements use the `self.scale` factor for responsive sizing.

## Interactions

- **Message Card**: Click to cycle through messages
- **EmulationStation Button**: Click to launch EmulationStation with 5-second countdown
- **F11**: Toggle fullscreen mode
- **ESC**: Exit application
- **R**: Manual refresh all
- **W**: Refresh weather only
- **M**: Cycle messages

## Animation Features

1. **Kirby Floating**: Continuous sine-wave vertical bobbing
2. **Kirby Glow**: Rainbow-colored glow layers
3. **Border Pulse**: Buttons and cards pulse with animation
4. **Gradient Background**: Animated color shifts for dreamy effect
5. **Time Updates**: Live clock updates every second

## Font Sizes (Scaled)

- **Large**: ~42px base (titles)
- **Medium**: ~28px base (section headers)
- **Small**: ~21px base (body text)

## File Updates

The main function `draw()` in `kirby_modern_display.py` now calls:
- `draw_date_header()` - NEW
- `draw_vertical_title_sidebar()` - NEW
- `draw_message_card()` - repositioned
- `draw_emulationstation_button()` - repositioned
- `draw_weather_card()` - repositioned as stats box
- `draw_floating_kirby()` - repositioned to center
- `draw_launch_overlay()` - unchanged

## Future Customization

To modify the layout further:
1. Adjust `left_section_width` ratio (currently 0.55 = 55%)
2. Modify card heights in the draw function
3. Change colors in the `Colors` class
4. Update animation speeds by modifying time multipliers
