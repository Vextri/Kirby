# Kirby Image Organization Guide

## Temperature-Based Seasonal Folders

Your Kirby images should be organized by Lethbridge, Alberta's typical seasonal temperature ranges:

### 🌞 Summer Folder (`images/summer/`)
**Temperature Range: 20°C and above (68°F+)**
- Hot summer days in Lethbridge
- Beach scenes, sunny weather, swimming
- Kirby enjoying warm weather activities
- Example: `kirby_beach.png`, `kirby_sunshine.jpg`

### 🌸 Spring Folder (`images/spring/`)
**Temperature Range: 10°C to 19°C (50-66°F)**
- Mild spring and pleasant fall weather
- Kirby with flowers, light activities
- Moderate weather scenes
- Example: `kirby_flowers.png`, `kirby_picnic.jpg`

### 🍂 Fall Folder (`images/fall/`)
**Temperature Range: 0°C to 9°C (32-48°F)**
- Cool fall weather, crisp days
- Kirby with autumn leaves, cozy scenes
- Light jacket weather
- Example: `kirby_leaves.png`, `kirby_cozy.jpg`

### ❄️ Winter Folder (`images/winter/`)
**Temperature Range: Below 0°C (Below 32°F)**
- Cold Lethbridge winters
- Kirby in snow, bundled up, winter activities
- Freezing temperatures
- Example: `kirby_snow.png`, `kirby_cold.jpg`

## How It Works

1. **Temperature Detection**: The app checks the current temperature in Lethbridge
2. **Season Selection**: Based on temperature, it selects the appropriate seasonal folder
3. **Image Cycling**: Images in that folder cycle every 30 seconds
4. **Fallback**: If no seasonal images are found, it uses images from the main `images/` folder

## Lethbridge Climate Reference

- **Summer**: June-August, often 20-30°C+ (68-86°F+)
- **Spring**: March-May, typically 10-20°C (50-68°F)  
- **Fall**: September-November, usually 0-15°C (32-59°F)
- **Winter**: December-February, frequently below 0°C (32°F), can reach -20°C (-4°F)

## File Format Support

- PNG (recommended for transparency)
- JPG/JPEG
- GIF
- BMP

## Tips

- Use consistent naming for easy identification
- Images will be automatically scaled to fit the window
- Add multiple images per season for variety
- The app will cycle through all images in the selected season folder

## Current Status

Your current image `wp12205377-1040338272.jpg` is in the main folder and will be used as a fallback until you organize images into seasonal folders.
