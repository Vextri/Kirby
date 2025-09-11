#!/usr/bin/env python3
"""
Create a simple Kirby PNG placeholder using PIL/Pillow
"""

try:
    from PIL import Image, ImageDraw
    
    # Create a 200x200 pink circle as Kirby placeholder
    size = 200
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(image)
    
    # Draw main pink circle (Kirby's body)
    margin = 10
    draw.ellipse([margin, margin, size-margin, size-margin], fill=(255, 182, 193, 255))
    
    # Draw eyes
    eye_size = 15
    left_eye = [70, 70, 70+eye_size, 70+20]
    right_eye = [115, 70, 115+eye_size, 70+20]
    draw.ellipse(left_eye, fill=(0, 0, 0, 255))
    draw.ellipse(right_eye, fill=(0, 0, 0, 255))
    
    # Draw mouth
    mouth = [90, 120, 110, 135]
    draw.ellipse(mouth, fill=(255, 150, 180, 255))
    
    # Save the image
    image.save('kirby.png')
    print("✅ Created kirby.png placeholder!")
    
except ImportError:
    print("ℹ️ PIL/Pillow not available - that's okay, the pygame version will draw a circle instead")
except Exception as e:
    print(f"❌ Error creating PNG: {e}")

if __name__ == "__main__":
    pass
