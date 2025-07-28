"""
Create a custom icon for IB Data Manager
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Create a custom application icon"""
    # Create a new image with RGBA mode
    size = 256
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Define colors
    primary_color = (0, 80, 200)  # Blue
    secondary_color = (0, 150, 50)  # Green
    accent_color = (255, 165, 0)  # Orange
    
    # Draw background circle
    margin = 20
    draw.ellipse([margin, margin, size-margin, size-margin], fill=primary_color)
    
    # Draw chart bars
    bar_width = 20
    bar_spacing = 10
    bar_x_start = 80
    bar_colors = [secondary_color, accent_color, secondary_color, accent_color]
    bar_heights = [100, 140, 80, 120]
    
    for i, (height, color) in enumerate(zip(bar_heights, bar_colors)):
        x = bar_x_start + i * (bar_width + bar_spacing)
        y = size - margin - height - 20
        draw.rectangle([x, y, x + bar_width, size - margin - 20], fill=color)
    
    # Draw line chart on top
    points = [(80, 120), (110, 80), (140, 100), (170, 60), (200, 90)]
    draw.line(points, fill='white', width=4)
    
    # Draw data points
    for x, y in points:
        draw.ellipse([x-4, y-4, x+4, y+4], fill='white')
    
    # Add text (if font is available)
    try:
        font = ImageFont.truetype("arial.ttf", 32)
        draw.text((size//2, size-60), "IB", font=font, fill='white', anchor='mm')
    except:
        # If font is not available, draw simple text
        pass
    
    # Save as ICO with multiple sizes
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # Create list of images at different sizes
    icon_images = []
    for icon_size in icon_sizes:
        icon_images.append(img.resize(icon_size, Image.Resampling.LANCZOS))
    
    # Save as ICO
    icon_images[0].save(
        'ib_data_manager.ico',
        format='ICO',
        sizes=icon_sizes,
        append_images=icon_images[1:]
    )
    
    print("✓ Icon created successfully: ib_data_manager.ico")
    return True

if __name__ == "__main__":
    try:
        create_app_icon()
        print("\nYou can now use this icon for your shortcuts!")
    except ImportError:
        print("This script requires the Pillow library.")
        print("Install it with: pip install Pillow")
