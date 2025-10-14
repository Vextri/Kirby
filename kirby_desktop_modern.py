"""
Kirby Weather - Modern Desktop App using tkinter with custom styling
Beautiful, responsive desktop application with animations
"""

import tkinter as tk
from tkinter import ttk
import json
import math
import time
from datetime import datetime
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import threading
import os

class ModernKirbyApp:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("✨ Kirby Weather Station ✨")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0f172a')
        
        # Colors (modern palette)
        self.colors = {
            'bg_primary': '#0f172a',
            'bg_secondary': '#1e293b',
            'accent': '#6366f1',
            'accent_light': '#818cf8',
            'text_primary': '#f8fafc',
            'text_secondary': '#94a3b8',
            'glass': '#e5e7eb',
            'border': '#d1d5db'
        }
        
        # Animation variables
        self.animation_time = 0
        self.kirby_float_offset = 0
        
        # Configure styles
        self.setup_styles()
        
        # Create UI
        self.setup_ui()
        
        # Start animations
        self.start_animations()
        
        # Load initial data
        self.load_data()
    
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        # Configure modern card style
        style.configure('Card.TFrame', 
                       background=self.colors['bg_secondary'],
                       relief='flat',
                       borderwidth=1)
        
        # Configure modern label styles
        style.configure('Title.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Heading.TLabel',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Body.TLabel',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 12))
        
        style.configure('Temperature.TLabel',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['accent_light'],
                       font=('Segoe UI', 48, 'bold'))
    
    def create_glass_frame(self, parent, **kwargs):
        """Create a frame with glassmorphism effect"""
        frame = tk.Frame(parent, 
                        bg=self.colors['bg_secondary'],
                        highlightbackground=self.colors['border'],
                        highlightthickness=1,
                        **kwargs)
        return frame
    
    def setup_ui(self):
        """Create the main UI layout"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = self.create_glass_frame(main_container, height=100)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_label = ttk.Label(header_frame, 
                               text="✨ Kirby Weather Station ✨",
                               style='Title.TLabel')
        title_label.pack(expand=True)
        
        subtitle_label = ttk.Label(header_frame,
                                  text="Lethbridge, Alberta • Real-time Weather",
                                  style='Body.TLabel')
        subtitle_label.pack()
        
        # Content area
        content_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_frame.pack(fill='both', expand=True)
        
        # Left side - Kirby
        left_frame = self.create_glass_frame(content_frame, width=400)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Kirby container
        kirby_container = tk.Frame(left_frame, bg=self.colors['bg_secondary'])
        kirby_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.kirby_label = tk.Label(kirby_container, 
                                   bg=self.colors['bg_secondary'],
                                   text="🌸", 
                                   font=('Segoe UI', 120))
        self.kirby_label.pack(expand=True)
        
        # Season info
        self.season_label = ttk.Label(left_frame,
                                     text="Season: Loading...",
                                     style='Heading.TLabel')
        self.season_label.pack(pady=10)
        
        # Right side - Weather and Messages
        right_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Weather card
        weather_frame = self.create_glass_frame(right_frame, height=350)
        weather_frame.pack(fill='x', pady=(0, 20))
        weather_frame.pack_propagate(False)
        
        # Weather content
        weather_content = tk.Frame(weather_frame, bg=self.colors['bg_secondary'])
        weather_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Temperature display
        self.temp_label = ttk.Label(weather_content,
                                   text="--°",
                                   style='Temperature.TLabel')
        self.temp_label.pack()
        
        # Condition
        self.condition_label = ttk.Label(weather_content,
                                        text="Loading weather...",
                                        style='Heading.TLabel')
        self.condition_label.pack(pady=(0, 20))
        
        # Weather details grid
        details_frame = tk.Frame(weather_content, bg=self.colors['bg_secondary'])
        details_frame.pack(fill='x')
        
        # Create weather detail items
        self.weather_items = {}
        details = [
            ('feels_like', 'Feels like'),
            ('humidity', 'Humidity'),
            ('wind_speed', 'Wind Speed'),
            ('updated', 'Last Updated')
        ]
        
        for i, (key, label) in enumerate(details):
            row = i // 2
            col = i % 2
            
            item_frame = tk.Frame(details_frame, bg=self.colors['bg_secondary'])
            item_frame.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
            
            ttk.Label(item_frame, text=label, style='Body.TLabel').pack()
            
            value_label = ttk.Label(item_frame, text="--", style='Heading.TLabel')
            value_label.pack()
            
            self.weather_items[key] = value_label
        
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Messages card
        messages_frame = self.create_glass_frame(right_frame)
        messages_frame.pack(fill='both', expand=True)
        
        # Messages header
        messages_header = ttk.Label(messages_frame,
                                   text="💌 Community Messages",
                                   style='Heading.TLabel')
        messages_header.pack(pady=(20, 10))
        
        # Messages container with scrollbar
        messages_container = tk.Frame(messages_frame, bg=self.colors['bg_secondary'])
        messages_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Scrollable text widget for messages
        self.messages_text = tk.Text(messages_container,
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_secondary'],
                                    font=('Segoe UI', 11),
                                    wrap='word',
                                    relief='flat',
                                    highlightthickness=0)
        
        scrollbar = ttk.Scrollbar(messages_container, orient='vertical', command=self.messages_text.yview)
        self.messages_text.configure(yscrollcommand=scrollbar.set)
        
        self.messages_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Time display (top right)
        self.time_frame = self.create_glass_frame(self.root, width=180, height=80)
        self.time_frame.place(x=self.root.winfo_reqwidth()-200, y=20)
        
        self.time_label = ttk.Label(self.time_frame,
                                   text="--:--",
                                   style='Heading.TLabel')
        self.time_label.pack(expand=True)
        
        self.date_label = ttk.Label(self.time_frame,
                                   text="Loading...",
                                   style='Body.TLabel')
        self.date_label.pack()
    
    def animate_kirby_float(self):
        """Animate Kirby floating effect"""
        self.animation_time += 0.1
        offset = int(math.sin(self.animation_time) * 10)
        
        # Update Kirby position
        current_y = self.kirby_label.winfo_y()
        if current_y != -1:  # Widget is mapped
            self.kirby_label.place_configure(y=current_y + offset - self.kirby_float_offset)
            self.kirby_float_offset = offset
    
    def update_time(self):
        """Update time display"""
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%B %d, %Y")
        
        self.time_label.config(text=time_str)
        self.date_label.config(text=date_str)
    
    def load_weather_data(self):
        """Load and display weather data"""
        # Simulated weather data (replace with actual API call)
        weather_data = {
            'temperature': 24,
            'condition': 'Sunny',
            'feels_like': 26,
            'humidity': 45,
            'wind_speed': 12,
            'season': 'summer'
        }
        
        # Update UI
        self.temp_label.config(text=f"{weather_data['temperature']}°C")
        self.condition_label.config(text=weather_data['condition'])
        self.weather_items['feels_like'].config(text=f"{weather_data['feels_like']}°")
        self.weather_items['humidity'].config(text=f"{weather_data['humidity']}%")
        self.weather_items['wind_speed'].config(text=f"{weather_data['wind_speed']} km/h")
        self.weather_items['updated'].config(text=datetime.now().strftime("%H:%M"))
        
        self.season_label.config(text=f"Season: {weather_data['season'].title()}")
        
        # Load Kirby image
        self.load_kirby_image(weather_data['season'])
    
    def load_kirby_image(self, season):
        """Load and display Kirby image for the season"""
        try:
            image_path = f"images/{season}/kirby.png"
            if os.path.exists(image_path):
                # Load and resize image
                img = Image.open(image_path)
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                
                # Add glow effect
                glow = img.copy()
                glow = glow.filter(ImageFilter.GaussianBlur(10))
                
                # Create final image with glow
                final_img = Image.new('RGBA', (240, 240), (0, 0, 0, 0))
                final_img.paste(glow, (20, 20), glow)
                final_img.paste(img, (20, 20), img)
                
                photo = ImageTk.PhotoImage(final_img)
                self.kirby_label.config(image=photo, text="")
                self.kirby_label.image = photo  # Keep a reference
            else:
                # Fallback to emoji if image not found
                self.kirby_label.config(image="", text="🌸")
                
        except Exception as e:
            print(f"Error loading Kirby image: {e}")
            self.kirby_label.config(image="", text="🌸")
    
    def load_messages(self):
        """Load and display messages"""
        try:
            with open('messages.json', 'r') as f:
                messages = json.load(f)
            
            # Clear current messages
            self.messages_text.delete(1.0, tk.END)
            
            # Add messages
            for i, message in enumerate(messages[:5]):
                message_text = f"💌 {message['message']}\n   — {message['name']}\n\n"
                self.messages_text.insert(tk.END, message_text)
            
        except Exception as e:
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.insert(tk.END, "Unable to load messages\n")
    
    def load_data(self):
        """Load all data"""
        self.load_weather_data()
        self.load_messages()
    
    def start_animations(self):
        """Start all animations and updates"""
        def update_loop():
            while True:
                try:
                    self.root.after(0, self.animate_kirby_float)
                    self.root.after(0, self.update_time)
                    time.sleep(0.05)  # 20 FPS
                except:
                    break
        
        def data_update_loop():
            while True:
                try:
                    time.sleep(30)  # Update every 30 seconds
                    self.root.after(0, self.load_data)
                except:
                    break
        
        # Start animation thread
        animation_thread = threading.Thread(target=update_loop, daemon=True)
        animation_thread.start()
        
        # Start data update thread
        data_thread = threading.Thread(target=data_update_loop, daemon=True)
        data_thread.start()
    
    def run(self):
        """Start the application"""
        print("🌟 Starting Modern Kirby Weather Desktop App!")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        finally:
            print("👋 Modern Kirby Desktop App closed!")

def main():
    try:
        app = ModernKirbyApp()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
