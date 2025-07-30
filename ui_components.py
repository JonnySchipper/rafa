"""
Disney Wish Oracle - UI Components
Tkinter-based GUI for the magical gift-revealing experience.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from PIL import Image, ImageTk, ImageDraw
import os
import threading
import time
import math
from typing import Optional, Dict, Any
import logging
import random

from game_logic import GameLogic, Gift, Character
from api_integration import grok_client, vapi_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_special_gift_by_position(position):
    """Check if a gift is special based on its position (1-indexed)."""
    return position % 5 == 0

def is_special_gift(gift_id, gifts_list=None):
    """Check if a gift is special based on the specified gift IDs."""
    # Use the exact gift IDs specified by the user
    SPECIAL_GIFT_IDS = {28, 24, 19}
    is_special = gift_id in SPECIAL_GIFT_IDS
    if is_special:
        logger.info(f"Special gift identified: Gift #{gift_id}")
    return is_special

class SpinningWheel:
    """Animated spinning wheel for gift selection."""
    
    def __init__(self, canvas, x, y, radius=200):  # Increased from 120 to 200
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = 0
        self.spinning = False
        self.segments = []
        self.colors = [
            "#FFD700", "#FF69B4", "#87CEEB", "#98FB98", "#DDA0DD", "#F0E68C",
            "#FFA07A", "#20B2AA", "#DA70D6", "#32CD32", "#FF6347", "#4169E1",
            "#DC143C", "#00CED1", "#FF1493", "#228B22", "#B22222", "#4682B4",
            "#D2691E", "#9370DB", "#008B8B", "#FF4500", "#2E8B57", "#800080",
            "#CD853F", "#5F9EA0", "#7B68EE", "#A0522D", "#808000", "#483D8B"
        ]
        
    def create_segments(self, items, full_gifts_list=None):
        """Create wheel segments for items."""
        self.segments = []
        if not items:
            return
            
        segment_angle = 360 / len(items)
        for i, item in enumerate(items):
            start_angle = i * segment_angle
            # Always use the actual gift ID from the item object
            gift_id = item.id if hasattr(item, 'id') else None
            
            # Check if this is a special surprise gift based on the gift ID
            is_special = is_special_gift(gift_id, full_gifts_list) if gift_id is not None else False
            
            # Debug logging for special gifts
            if is_special:
                logger.info(f"Creating special segment for Gift #{gift_id}")
            
            # Use gold colors for special gifts, regular colors for others
            if is_special:
                # Gold gradient colors for special gifts
                special_colors = ["#FFD700", "#FFA500", "#FF8C00", "#FF6347", "#FF4500", "#FFD700"]
                color = special_colors[i % len(special_colors)]
            else:
                color = self.colors[i % len(self.colors)]
            
            segment = {
                'start_angle': start_angle,
                'extent': segment_angle,
                'color': color,
                'item': item,
                'gift_id': gift_id,
                'is_special': is_special
            }
            self.segments.append(segment)
    
    def draw(self):
        """Draw the spinning wheel."""
        try:
            self.canvas.delete("wheel")
        except tk.TclError:
            # Canvas no longer exists, ignore
            return
        
        if not self.segments:
            # Draw empty wheel
            self.canvas.create_oval(
                self.x - self.radius, self.y - self.radius,
                self.x + self.radius, self.y + self.radius,
                fill="#CCCCCC", outline="white", width=5,  # Increased border width
                tags="wheel"
            )
            self.canvas.create_text(
                self.x, self.y,
                text="All Gifts\nRevealed!",
                font=("Arial", 24, "bold"),  # Increased font size
                fill="white",
                tags="wheel"
            )
            return
        
        # Draw segments
        for segment in self.segments:
            start_angle = segment['start_angle'] + self.angle
            is_special = segment.get('is_special', False)
            
            # Use thicker border for special gifts
            border_width = 5 if is_special else 3
            
            self.canvas.create_arc(
                self.x - self.radius, self.y - self.radius,
                self.x + self.radius, self.y + self.radius,
                start=start_angle, extent=segment['extent'],
                fill=segment['color'], outline="white", width=border_width,
                tags="wheel"
            )
            
            # Add gift number text to each segment
            mid_angle = math.radians(start_angle + segment['extent'] / 2)
            text_radius = self.radius * 0.7
            text_x = self.x + text_radius * math.cos(mid_angle)
            text_y = self.y + text_radius * math.sin(mid_angle)
            
            gift_text = str(segment['gift_id']) if 'gift_id' in segment else str(segment['item']).replace('Gift #', '')
            
            # Dynamic font size based on number of segments, larger for special gifts
            base_font_size = max(12, min(18, 300 // len(self.segments)))
            font_size = base_font_size + 2 if is_special else base_font_size
            
            # Use different text color for special gifts
            if is_special:
                text_color = "#1e3a8a"  # Dark blue for gold segments
            else:
                text_color = "white" if segment['color'] in ["#DC143C", "#B22222", "#800080", "#483D8B"] else "black"
            
            self.canvas.create_text(
                text_x, text_y,
                text=gift_text,
                font=("Arial", font_size, "bold"),
                fill=text_color,
                tags="wheel"
            )
            
            # Add sparkle emoji for special gifts
            if is_special:
                sparkle_radius = self.radius * 0.85
                sparkle_x = self.x + sparkle_radius * math.cos(mid_angle)
                sparkle_y = self.y + sparkle_radius * math.sin(mid_angle)
                
                self.canvas.create_text(
                    sparkle_x, sparkle_y,
                    text="✨",
                    font=("Arial", 12),
                    fill="#FFD700",
                    tags="wheel"
                )
        
        # Draw center circle - bigger
        center_radius = 35  # Increased from 25
        self.canvas.create_oval(
            self.x - center_radius, self.y - center_radius,
            self.x + center_radius, self.y + center_radius,
            fill="#1e3a8a", outline="white", width=4,  # Increased border
            tags="wheel"
        )
        
        # Add magical sparkle in center - bigger
        self.canvas.create_text(
            self.x, self.y,
            text="✨",
            font=("Arial", 24),  # Increased size
            fill="gold",
            tags="wheel"
        )
        
        # Draw pointer - much bigger
        pointer_size = 30  # Increased from 20
        self.canvas.create_polygon(
            self.x + self.radius + 20, self.y,
            self.x + self.radius + 20 + pointer_size, self.y - pointer_size//2,
            self.x + self.radius + 20 + pointer_size, self.y + pointer_size//2,
            fill="red", outline="white", width=4,  # Increased border
            tags="wheel"
        )
    
    def spin(self, duration=4.0, callback=None):
        """Animate the spinning wheel."""
        if self.spinning or not self.segments:
            return
            
        self.spinning = True
        start_time = time.time()
        
        # Randomize the final position for more excitement
        extra_spins = random.randint(3, 6) * 360
        target_angle = random.randint(0, 360) + extra_spins
        
        def animate():
            elapsed = time.time() - start_time
            if elapsed < duration:
                # Easing function for smooth deceleration
                progress = elapsed / duration
                eased_progress = 1 - (1 - progress) ** 3  # Cubic ease-out
                current_angle = target_angle * eased_progress
                self.angle = current_angle % 360
                self.draw()
                self.canvas.after(50, animate)
            else:
                self.angle = target_angle % 360
                self.draw()
                self.spinning = False
                if callback:
                    callback(self.get_selected_item())
        
        animate()
    
    def get_selected_item(self):
        """Get the item currently selected by the pointer."""
        if not self.segments:
            return None
            
        # The pointer is at 0 degrees (right side)
        # We need to find which segment the pointer is pointing to
        pointer_angle = (360 - self.angle) % 360
        
        for segment in self.segments:
            start = segment['start_angle']
            end = (start + segment['extent']) % 360
            
            if start <= end:
                if start <= pointer_angle <= end:
                    return segment
            else:  # Segment crosses 0 degrees
                if pointer_angle >= start or pointer_angle <= end:
                    return segment
        
        return self.segments[0] if self.segments else None
    
    def remove_segment(self, gift_id):
        """Remove a segment from the wheel after it's been revealed."""
        self.segments = [seg for seg in self.segments if seg.get('gift_id') != gift_id]
        
        # Recalculate segment angles to fill the space
        if self.segments:
            segment_angle = 360 / len(self.segments)
            for i, segment in enumerate(self.segments):
                segment['start_angle'] = i * segment_angle
                segment['extent'] = segment_angle
        
        # Only redraw if canvas still exists
        try:
            self.draw()
        except tk.TclError:
            # Canvas no longer exists, ignore
            pass

class DisneyWishOracleApp:
    """Main application window for the Disney Wish Oracle."""
    
    def __init__(self, root: tk.Tk, game_logic: GameLogic):
        self.root = root
        self.game_logic = game_logic
        
        # Configure main window - MUCH BIGGER
        self.root.title("Disney Wish Oracle - Rafa's 30th Birthday Adventure! 🎂✨")
        self.root.geometry("1400x900")  # Increased from 1200x800
        self.root.configure(bg="#0f1729")  # Darker magical blue
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Load fonts
        self.setup_fonts()
        
        # Current state
        self.current_screen = None
        self.current_gift = None
        self.current_character = None
        self.animation_running = False
        self.spinning_wheel = None
        
        # Create main container with bigger padding
        self.main_frame = tk.Frame(root, bg="#0f1729")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)  # Increased padding
        
        # Show welcome screen initially
        self.show_welcome_screen()
    
    def setup_fonts(self):
        """Set up custom fonts for the application - ALL BIGGER."""
        try:
            self.title_font = font.Font(family="Arial", size=36, weight="bold")  # Increased from 28
            self.subtitle_font = font.Font(family="Arial", size=24, weight="bold")  # Increased from 18
            self.body_font = font.Font(family="Arial", size=18)  # Increased from 14
            self.small_font = font.Font(family="Arial", size=14)  # Increased from 11
            self.large_font = font.Font(family="Arial", size=26, weight="bold")  # Increased from 20
            self.huge_font = font.Font(family="Arial", size=32, weight="bold")  # New huge font
        except:
            # Fallback to default fonts - bigger
            self.title_font = font.Font(size=36, weight="bold")
            self.subtitle_font = font.Font(size=24, weight="bold")
            self.body_font = font.Font(size=18)
            self.small_font = font.Font(size=14)
            self.large_font = font.Font(size=26, weight="bold")
            self.huge_font = font.Font(size=32, weight="bold")
    
    def clear_screen(self):
        """Clear the current screen contents."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_welcome_screen(self):
        """Display the main welcome screen."""
        self.clear_screen()
        self.current_screen = "welcome"
        
        # Title section with sparkle animation - bigger spacing
        title_frame = tk.Frame(self.main_frame, bg="#0f1729")
        title_frame.pack(pady=50)  # Increased padding
        
        title_label = tk.Label(
            title_frame,
            text="✨ Disney Wish Oracle ✨",
            font=self.title_font,
            bg="#0f1729",
            fg="#FFD700"  # Disney gold
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="🎂 Rafa's Magical 30th Birthday Adventure 🎂",
            font=self.subtitle_font,
            bg="#0f1729",
            fg="#FFFFFF"
        )
        subtitle_label.pack(pady=15)  # Increased padding
        
        subtitle2_label = tk.Label(
            title_frame,
            text="Fort Wilderness • Where Dreams Come True",
            font=self.body_font,
            bg="#0f1729",
            fg="#87CEEB"  # Light blue
        )
        subtitle2_label.pack()
        
        # Progress section with magic
        self.show_progress_info()
        
        # Main action button - MUCH BIGGER
        action_frame = tk.Frame(self.main_frame, bg="#0f1729")
        action_frame.pack(pady=60)  # Increased padding
        
        # Giant magical reveal button
        reveal_btn = tk.Button(
            action_frame,
            text="🎁 SPIN THE WHEEL OF WISHES! 🎁",
            font=self.huge_font,  # Using huge font
            bg="#FF1493",  # Deep pink
            fg="#FFFFFF",
            command=self.show_wheel_screen,
            width=35,  # Increased width
            height=4,  # Increased height
            relief="raised",
            bd=8,  # Increased border
            cursor="hand2"
        )
        reveal_btn.pack(pady=30)  # Increased padding
        
        # Options section - bigger buttons
        options_frame = tk.Frame(self.main_frame, bg="#0f1729")
        options_frame.pack(pady=40)  # Increased padding
        
        settings_btn = tk.Button(
            options_frame,
            text="⚙️ Settings",
            font=self.body_font,
            bg="#4169E1",
            fg="#FFFFFF",
            command=self.show_settings_screen,
            width=18,  # Increased width
            height=3  # Increased height
        )
        settings_btn.pack(side=tk.LEFT, padx=15)  # Increased padding
        
        progress_btn = tk.Button(
            options_frame,
            text="📊 View Progress",
            font=self.body_font,
            bg="#4169E1",
            fg="#FFFFFF",
            command=self.show_progress_screen,
            width=18,  # Increased width
            height=3  # Increased height
        )
        progress_btn.pack(side=tk.LEFT, padx=15)  # Increased padding
        
        vapi_btn = tk.Button(
            options_frame,
            text="🤖 VAPI Magic",
            font=self.body_font,
            bg="#FFD700",
            fg="#1e3a8a",
            command=self.show_vapi_magic_screen,
            width=18,  # Increased width
            height=3  # Increased height
        )
        vapi_btn.pack(side=tk.LEFT, padx=15)  # Increased padding
        
        if self.game_logic.session.total_revealed > 0:
            reset_btn = tk.Button(
                options_frame,
                text="🔄 Reset Game",
                font=self.body_font,
                bg="#DC143C",
                fg="#FFFFFF",
                command=self.confirm_reset,
                width=18,  # Increased width
                height=3  # Increased height
            )
            reset_btn.pack(side=tk.LEFT, padx=15)  # Increased padding
    
    def show_progress_info(self):
        """Display current progress information with magic."""
        summary = self.game_logic.get_game_summary()
        
        progress_frame = tk.Frame(self.main_frame, bg="#1e3a8a", relief="raised", bd=5)  # Increased border
        progress_frame.pack(pady=40, padx=120)  # Increased padding
        
        # Progress with sparkles - bigger
        progress_label = tk.Label(
            progress_frame,
            text=f"✨ Gifts Revealed: {summary['revealed_gifts']}/30 ✨",
            font=self.large_font,  # Using larger font
            bg="#1e3a8a",
            fg="#FFD700"
        )
        progress_label.pack(pady=20)  # Increased padding
        
        if summary['revealed_gifts'] > 0:
            percentage_label = tk.Label(
                progress_frame,
                text=f"🌟 Adventure Progress: {summary['completion_percentage']:.1f}% Complete 🌟",
                font=self.body_font,
                bg="#1e3a8a",
                fg="#87CEEB"
            )
            percentage_label.pack(pady=8)  # Increased padding
            
            if summary['is_complete']:
                complete_label = tk.Label(
                    progress_frame,
                    text="🏆 ALL WISHES GRANTED! 🏆",
                    font=self.huge_font,  # Using huge font
                    bg="#1e3a8a",
                    fg="#FFD700"
                )
                complete_label.pack(pady=15)  # Increased padding
    
    def show_wheel_screen(self):
        """Display the spinning wheel selection screen."""
        available_gifts = self.game_logic.get_available_gifts()
        
        if not available_gifts:
            messagebox.showinfo(
                "All Gifts Revealed! 🎉",
                "Congratulations! All 30 gifts have been revealed!\n\n"
                "Rafa's 30th birthday adventure is complete! ✨🎂"
            )
            return
        
        self.clear_screen()
        self.current_screen = "wheel"
        
        # Title - bigger
        title_label = tk.Label(
            self.main_frame,
            text="🎪 The Magical Wheel of Birthday Wishes! 🎪",
            font=self.title_font,
            bg="#0f1729",
            fg="#FFD700"
        )
        title_label.pack(pady=40)  # Increased padding
        
        # Instructions with count - bigger
        instruction_label = tk.Label(
            self.main_frame,
            text=f"✨ {len(available_gifts)} magical surprises await! Spin to choose your next gift! ✨",
            font=self.subtitle_font,
            bg="#0f1729",
            fg="#FFFFFF"
        )
        instruction_label.pack(pady=15)  # Increased padding
        
        # Canvas for the spinning wheel - MUCH BIGGER
        canvas_frame = tk.Frame(self.main_frame, bg="#0f1729")
        canvas_frame.pack(pady=40)  # Increased padding
        
        # Make the wheel MUCH bigger
        canvas_size = min(800, max(600, len(available_gifts) * 20))  # Increased base size
        wheel_radius = min(280, max(200, len(available_gifts) * 5))  # Much bigger radius
        
        self.wheel_canvas = tk.Canvas(
            canvas_frame,
            width=canvas_size,
            height=canvas_size,
            bg="#0f1729",
            highlightthickness=0
        )
        self.wheel_canvas.pack()
        
        # Create spinning wheel with ALL available gifts - BIGGER
        center_x, center_y = canvas_size // 2, canvas_size // 2
        self.spinning_wheel = SpinningWheel(self.wheel_canvas, center_x, center_y, wheel_radius)
        
        # Use ALL available gifts for the wheel
        self.spinning_wheel.create_segments(available_gifts, self.game_logic.gifts)
        self.spinning_wheel.draw()
        
        # Show gift count info - bigger text
        info_label = tk.Label(
            self.main_frame,
            text=f"🎁 Gifts on the wheel: {', '.join([str(gift.id) for gift in available_gifts])} 🎁",
            font=self.body_font,  # Increased font size
            bg="#0f1729",
            fg="#87CEEB",
            wraplength=1000  # Increased wrap length
        )
        info_label.pack(pady=15)  # Increased padding
        
        # Spin button - MUCH BIGGER
        button_frame = tk.Frame(self.main_frame, bg="#0f1729")
        button_frame.pack(pady=40)  # Increased padding
        
        spin_btn = tk.Button(
            button_frame,
            text="🌟 SPIN THE WHEEL! 🌟",
            font=self.huge_font,  # Using huge font
            bg="#FF4500",  # Orange red
            fg="#FFFFFF",
            command=self.spin_wheel,
            width=25,  # Increased width
            height=3,  # Increased height
            relief="raised",
            bd=8  # Increased border
        )
        spin_btn.pack(side=tk.LEFT, padx=15)  # Increased padding
        
        back_btn = tk.Button(
            button_frame,
            text="⬅️ Back",
            font=self.body_font,
            bg="#4169E1",
            fg="#FFFFFF",
            command=self.show_welcome_screen,
            width=15,
            height=3  # Increased height
        )
        back_btn.pack(side=tk.LEFT, padx=15)  # Increased padding
    
    def spin_wheel(self):
        """Start the wheel spinning animation."""
        available_gifts = self.game_logic.get_available_gifts()
        if not available_gifts:
            return
            
        # The wheel will determine which gift is selected
        # Start spinning animation
        if self.spinning_wheel:
            self.spinning_wheel.spin(duration=5.0, callback=self.on_wheel_stopped)
    
    def on_wheel_stopped(self, selected_segment):
        """Handle when the wheel stops spinning."""
        if not selected_segment:
            self.show_welcome_screen()
            return
            
        # Get the selected gift from the segment
        selected_gift_id = selected_segment.get('gift_id')
        if selected_gift_id:
            self.current_gift = self.game_logic.get_gift_by_id(selected_gift_id)
        else:
            # Fallback to the item if gift_id not found
            available_gifts = self.game_logic.get_available_gifts()
            self.current_gift = available_gifts[0] if available_gifts else None
            
        if not self.current_gift:
            self.show_welcome_screen()
            return
            
        # Check if this is a special phone call gift
        if is_special_gift(self.current_gift.id, self.game_logic.gifts):
            # Show phone call screen for special gifts
            self.root.after(1500, self.show_phone_call_screen)
        else:
            # Normal gift reveal
            self.current_character = self.game_logic.find_best_character_match(self.current_gift)
                    # Add a dramatic pause before revealing
        self.root.after(1500, self.show_character_entrance)
    
    def show_phone_call_screen(self):
        """Show the phone call screen for special gifts."""
        if not self.current_gift:
            self.show_welcome_screen()
            return
            
        self.clear_screen()
        self.current_screen = "phone_call"
        
        # Phone call frame
        phone_frame = tk.Frame(self.main_frame, bg="#0f1729")
        phone_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
        
        # Special gift title
        title_label = tk.Label(
            phone_frame,
            text="📞 SPECIAL PHONE CALL GIFT! 📞",
            font=self.title_font,
            bg="#0f1729",
            fg="#FFD700"
        )
        title_label.pack(pady=30)
        
        # Gift number
        gift_label = tk.Label(
            phone_frame,
            text=f"🎁 GIFT #{self.current_gift.id} 🎁",
            font=self.huge_font,
            bg="#0f1729",
            fg="#FF69B4"
        )
        gift_label.pack(pady=20)
        
        # Phone animation
        phone_animation_frame = tk.Frame(phone_frame, bg="#0f1729")
        phone_animation_frame.pack(pady=40)
        
        phone_icon = tk.Label(
            phone_animation_frame,
            text="📱",
            font=("Arial", 48),
            bg="#0f1729",
            fg="#32CD32"
        )
        phone_icon.pack()
        
        # Message
        message_label = tk.Label(
            phone_frame,
            text="✨ A magical phone call is about to begin! ✨\n\n"
                 "🎭 A Disney character will call you to reveal this special gift!\n\n"
                 "📞 Get ready for the surprise of a lifetime! 📞",
            font=self.body_font,
            bg="#0f1729",
            fg="#FFFFFF",
            wraplength=600,
            justify=tk.CENTER
        )
        message_label.pack(pady=30)
        
        # Trigger the phone call
        self.root.after(2000, self.trigger_birthday_call)
        
        # Back button
        button_frame = tk.Frame(phone_frame, bg="#0f1729")
        button_frame.pack(pady=40)
        
        back_btn = tk.Button(
            button_frame,
            text="⬅️ Back to Menu",
            font=self.body_font,
            bg="#4169E1",
            fg="#FFFFFF",
            command=self.show_welcome_screen,
            width=15,
            height=2
        )
        back_btn.pack()
    
    def show_character_entrance(self):
        """Show the Disney character entrance animation."""
        if not self.current_character:
            self.show_welcome_screen()
            return
            
        self.clear_screen()
        self.current_screen = "character_entrance"
        
        # Character entrance
        entrance_frame = tk.Frame(self.main_frame, bg="#0f1729")
        entrance_frame.pack(expand=True)
        
        # Magical entrance text
        entrance_label = tk.Label(
            entrance_frame,
            text="✨ A Disney friend approaches... ✨",
            font=self.title_font,
            bg="#0f1729",
            fg="#FFD700"
        )
        entrance_label.pack(pady=50)
        
        # Character appears
        char_label = tk.Label(
            entrance_frame,
            text=f"🌟 {self.current_character.name} appears! 🌟",
            font=self.huge_font,
            bg="#0f1729",
            fg="#FF69B4"
        )
        char_label.pack(pady=30)
        
        # Character image
        self.show_character_image(entrance_frame)
        
        # Generate magical message
        self.root.after(2000, self.generate_and_show_message)
    
    def generate_and_show_message(self):
        """Generate and show the magical character message."""
        try:
            if not self.current_character or not self.current_gift:
                raise ValueError("Missing character or gift data")
                
            character_dict = {
                'name': self.current_character.name,
                'personality': self.current_character.personality,
                'voice_style': self.current_character.voice_style
            }
            
            # Don't reveal the gift description - keep it mysterious!
            gift_dict = {
                'id': self.current_gift.id,
                'description': "a magical birthday surprise",  # Keep it secret!
                'themes': self.current_gift.themes
            }
            
            # Generate the reveal message
            reveal_message = grok_client.generate_gift_reveal(
                character_dict, 
                gift_dict, 
                ["birthday magic", "surprise", "wonder", "Disney dreams"]
            )
            
            self.show_gift_reveal_screen(reveal_message)
            
        except Exception as e:
            logger.error(f"Error generating reveal message: {e}")
            # Use magical fallback message
            char_name = self.current_character.name if self.current_character else "A Disney friend"
            gift_id = str(self.current_gift.id) if self.current_gift else "0"
            fallback_message = f"🎁 {char_name} has chosen a special magical surprise for you! The spirits have selected Gift #{gift_id}! Open it to discover the wonder within! Happy 30th Birthday, Rafa! ✨🎂"
            self.show_gift_reveal_screen(fallback_message)
    
    def show_gift_reveal_screen(self, reveal_message: str):
        """Display the gift reveal screen with the actual gift image."""
        if not self.current_character or not self.current_gift:
            self.show_welcome_screen()
            return
            
        self.animation_running = False
        self.clear_screen()
        self.current_screen = "reveal"
        
        # Create reveal frame
        reveal_frame = tk.Frame(self.main_frame, bg="#0f1729")
        reveal_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
        
        # Character message section
        message_frame = tk.Frame(reveal_frame, bg="#FFFFFF", relief="raised", bd=5)
        message_frame.pack(pady=20, fill=tk.X)
        
        char_message_label = tk.Label(
            message_frame,
            text=f"💬 {self.current_character.name} says:",
            font=self.subtitle_font,
            bg="#FFFFFF",
            fg="#1e3a8a"
        )
        char_message_label.pack(pady=10)
        
        message_label = tk.Label(
            message_frame,
            text=reveal_message,
            font=self.body_font,
            bg="#FFFFFF",
            fg="#1e3a8a",
            wraplength=800,
            justify=tk.CENTER
        )
        message_label.pack(pady=20, padx=30)
        
        # Gift reveal section
        gift_section = tk.Frame(reveal_frame, bg="#0f1729")
        gift_section.pack(pady=30)
        
        gift_label = tk.Label(
            gift_section,
            text=f"🎁 GIFT #{self.current_gift.id} 🎁",
            font=self.title_font,
            bg="#0f1729",
            fg="#FFD700"
        )
        gift_label.pack(pady=20)
        
        # Show the actual gift image!
        self.show_gift_image(gift_section)
        
        # Action buttons
        button_frame = tk.Frame(reveal_frame, bg="#0f1729")
        button_frame.pack(pady=40)
        
        confirm_btn = tk.Button(
            button_frame,
            text="🎉 ACCEPT THIS MAGICAL GIFT! 🎉",
            font=self.large_font,
            bg="#32CD32",
            fg="#FFFFFF",
            command=self.confirm_reveal,
            width=25,
            height=3,
            relief="raised",
            bd=5
        )
        confirm_btn.pack(side=tk.LEFT, padx=15)
        
        back_btn = tk.Button(
            button_frame,
            text="⬅️ Back to Menu",
            font=self.body_font,
            bg="#4169E1",
            fg="#FFFFFF",
            command=self.show_welcome_screen,
            width=15,
            height=2
        )
        back_btn.pack(side=tk.LEFT, padx=15)
    
    def show_character_image(self, parent_frame):
        """Display character image or placeholder."""
        if not self.current_character:
            return
            
        image_frame = tk.Frame(parent_frame, bg="#0f1729")
        image_frame.pack(pady=20)  # Increased padding
        
        try:
            # Try to load the character image - MUCH BIGGER
            if os.path.exists(self.current_character.image_path):
                img = Image.open(self.current_character.image_path)
                img = img.resize((300, 300), Image.Resampling.LANCZOS)  # Increased from 200x200
                photo = ImageTk.PhotoImage(img)
                
                img_label = tk.Label(image_frame, image=photo, bg="#0f1729")
                # Keep a reference to prevent garbage collection
                img_label.image = photo
                img_label.pack()
            else:
                # Magical placeholder for missing image - bigger
                placeholder_label = tk.Label(
                    image_frame,
                    text=f"✨\n{self.current_character.name}\n✨",
                    font=self.huge_font,  # Using huge font
                    bg="#4169E1",
                    fg="#FFFFFF",
                    width=25,  # Increased width
                    height=10,  # Increased height
                    relief="raised",
                    bd=8  # Increased border
                )
                placeholder_label.pack()
                
        except Exception as e:
            logger.warning(f"Could not load character image: {e}")
            # Fallback magical placeholder - bigger
            placeholder_label = tk.Label(
                image_frame,
                text=f"🌟 {self.current_character.name} 🌟",
                font=self.huge_font,  # Using huge font
                bg="#4169E1",
                fg="#FFFFFF",
                width=30,  # Increased width
                height=8,  # Increased height
                relief="raised",
                bd=8  # Increased border
            )
            placeholder_label.pack()
    
    def show_gift_image(self, parent_frame):
        """Display the actual gift image - the big reveal!"""
        if not self.current_gift:
            return
            
        image_frame = tk.Frame(parent_frame, bg="#FFD700", relief="raised", bd=10)  # Increased border
        image_frame.pack(pady=30)  # Increased padding
        
        try:
            # Try to load the gift image - MUCH BIGGER
            if os.path.exists(self.current_gift.image_path):
                img = Image.open(self.current_gift.image_path)
                # Resize to be very prominent
                img = img.resize((400, 400), Image.Resampling.LANCZOS)  # Increased from 300x300
                photo = ImageTk.PhotoImage(img)
                
                img_label = tk.Label(image_frame, image=photo, bg="#FFD700")
                # Keep a reference to prevent garbage collection  
                img_label.image = photo
                img_label.pack(padx=30, pady=30)  # Increased padding
                
                # Add sparkle text - bigger
                sparkle_label = tk.Label(
                    image_frame,
                    text="✨ Your magical surprise awaits! ✨",
                    font=self.large_font,  # Increased font size
                    bg="#FFD700",
                    fg="#1e3a8a"
                )
                sparkle_label.pack(pady=15)  # Increased padding
                
            else:
                # Mystery box placeholder - bigger
                mystery_label = tk.Label(
                    image_frame,
                    text=f"🎁\n\nMYSTERY GIFT\n#{self.current_gift.id}\n\n🎁",
                    font=self.huge_font,  # Using huge font
                    bg="#FFD700",
                    fg="#1e3a8a",
                    width=18,  # Increased width
                    height=12,  # Increased height
                    relief="raised",
                    bd=5
                )
                mystery_label.pack(padx=40, pady=40)  # Increased padding
                
        except Exception as e:
            logger.warning(f"Could not load gift image: {e}")
            # Fallback mystery box - bigger
            mystery_label = tk.Label(
                image_frame,
                text=f"🎁 SURPRISE GIFT #{self.current_gift.id} 🎁",
                font=self.huge_font,  # Using huge font
                bg="#FFD700",
                fg="#1e3a8a",
                width=25,  # Increased width
                height=10,  # Increased height
                relief="raised",
                bd=8  # Increased border
            )
            mystery_label.pack(padx=40, pady=40)  # Increased padding
    
    def confirm_reveal(self):
        """Confirm the gift reveal and update progress."""
        if not self.current_gift or not self.current_character:
            messagebox.showerror("Error", "Missing gift or character data. Please try again.")
            return
            
        success = self.game_logic.reveal_gift(self.current_gift, self.current_character)
        
        if success:
            # Remove the revealed gift from the spinning wheel
            if self.spinning_wheel:
                self.spinning_wheel.remove_segment(self.current_gift.id)
            
            # Show celebration screen
            self.show_celebration_screen()
        else:
            messagebox.showerror("Error", "Failed to reveal gift. Please try again.")
    
    def show_celebration_screen(self):
        """Show magical celebration after successful reveal."""
        self.clear_screen()
        
        # Celebration frame
        celebration_frame = tk.Frame(self.main_frame, bg="#0f1729")
        celebration_frame.pack(expand=True)
        
        # Success message with fireworks
        success_label = tk.Label(
            celebration_frame,
            text="🎆 MAGICAL GIFT REVEALED! 🎆",
            font=self.title_font,
            bg="#0f1729",
            fg="#FFD700"
        )
        success_label.pack(pady=60)
        
        # Show which gift was just revealed
        if self.current_gift:
            revealed_label = tk.Label(
                celebration_frame,
                text=f"🎁 Gift #{self.current_gift.id} has been added to your collection! 🎁",
                font=self.subtitle_font,
                bg="#0f1729",
                fg="#FF69B4"
            )
            revealed_label.pack(pady=20)
        
        # Updated progress with sparkles
        summary = self.game_logic.get_game_summary()
        progress_label = tk.Label(
            celebration_frame,
            text=f"✨ Progress: {summary['revealed_gifts']}/30 gifts revealed! ✨\n🌟 {summary['remaining_gifts']} more magical surprises await! 🌟",
            font=self.large_font,
            bg="#0f1729",
            fg="#FFFFFF",
            justify=tk.CENTER
        )
        progress_label.pack(pady=30)
        
        # Show remaining gift numbers
        if summary['remaining_gifts'] > 0:
            remaining_gifts = self.game_logic.get_available_gifts()
            remaining_numbers = [str(gift.id) for gift in remaining_gifts]
            remaining_text = ", ".join(remaining_numbers[:10])  # Show first 10
            if len(remaining_numbers) > 10:
                remaining_text += f"... and {len(remaining_numbers) - 10} more!"
                
            remaining_label = tk.Label(
                celebration_frame,
                text=f"🎯 Remaining gifts on wheel: {remaining_text} 🎯",
                font=self.body_font,
                bg="#0f1729",
                fg="#87CEEB",
                wraplength=800
            )
            remaining_label.pack(pady=15)
        
        # Action buttons
        button_frame = tk.Frame(celebration_frame, bg="#0f1729")
        button_frame.pack(pady=40)
        
        if summary['remaining_gifts'] > 0:
            next_btn = tk.Button(
                button_frame,
                text="🎡 SPIN AGAIN FOR ANOTHER GIFT! 🎡",
                font=self.large_font,
                bg="#FF1493",
                fg="#FFFFFF",
                command=self.show_wheel_screen,
                width=25,
                height=3,
                relief="raised",
                bd=5
            )
            next_btn.pack(side=tk.LEFT, padx=15)
        
        menu_btn = tk.Button(
            button_frame,
            text="🏠 Back to Menu",
            font=self.body_font,
            bg="#4169E1",
            fg="#FFFFFF",
            command=self.show_welcome_screen,
            width=15,
            height=2
        )
        menu_btn.pack(side=tk.LEFT, padx=15)
        
        if summary['is_complete']:
            # Game completion celebration
            self.show_completion_celebration()
    
    def show_completion_celebration(self):
        """Show special celebration for completing all gifts."""
        completion_label = tk.Label(
            self.main_frame,
            text="🏆 ALL 30 MAGICAL GIFTS REVEALED! 🏆\n\n"
                 "🎂 Rafa's 30th Birthday Adventure is Complete! 🎂\n"
                 "✨ Happy Birthday from all your Disney friends! ✨\n\n"
                 "🌟 May all your wishes come true! 🌟",
            font=self.title_font,
            bg="#0f1729",
            fg="#FFD700",
            justify=tk.CENTER
        )
        completion_label.pack(pady=80)
    
    def show_settings_screen(self):
        """Display the settings screen."""
        self.clear_screen()
        self.current_screen = "settings"
        
        # Settings title
        title_label = tk.Label(
            self.main_frame,
            text="⚙️ Oracle Settings",
            font=self.title_font,
            bg="#0f1729",
            fg="#FFD700"
        )
        title_label.pack(pady=40)
        
        # Game mode selection
        mode_frame = tk.Frame(self.main_frame, bg="#1e3a8a", relief="raised", bd=3)
        mode_frame.pack(pady=30, padx=100)
        
        tk.Label(
            mode_frame,
            text="🎮 Game Mode:",
            font=self.subtitle_font,
            bg="#1e3a8a",
            fg="#FFFFFF"
        ).pack(pady=15)
        
        mode_var = tk.StringVar(value=self.game_logic.session.mode)
        
        modes = [
            ("🎲 Random Magic", "random"),
            ("📋 Sequential Order", "sequential")
        ]
        
        for text, mode in modes:
            rb = tk.Radiobutton(
                mode_frame,
                text=text,
                variable=mode_var,
                value=mode,
                font=self.body_font,
                bg="#1e3a8a",
                fg="#FFFFFF",
                selectcolor="#4169E1",
                command=lambda m=mode: self.set_game_mode(m)
            )
            rb.pack(pady=8)
        
        # API status
        api_frame = tk.Frame(self.main_frame, bg="#1e3a8a", relief="raised", bd=3)
        api_frame.pack(pady=20, padx=100)
        
        api_status = "✅ Connected & Magical" if grok_client.is_api_available() else "❌ Using Backup Magic"
        tk.Label(
            api_frame,
            text=f"🤖 AI Magic Status: {api_status}",
            font=self.body_font,
            bg="#1e3a8a",
            fg="#FFFFFF"
        ).pack(pady=15)
        
        # Back button
        back_btn = tk.Button(
            self.main_frame,
            text="⬅️ Back to Menu",
            font=self.body_font,
            bg="#4169E1",
            fg="#FFFFFF",
            command=self.show_welcome_screen,
            width=20,
            height=2
        )
        back_btn.pack(pady=40)
    
    def show_progress_screen(self):
        """Display detailed progress information."""
        self.clear_screen()
        self.current_screen = "progress"
        
        # Progress title
        title_label = tk.Label(
            self.main_frame,
            text="📊 Birthday Adventure Progress",
            font=self.title_font,
            bg="#0f1729",
            fg="#FFD700"
        )
        title_label.pack(pady=30)
        
        # Overall progress
        summary = self.game_logic.get_game_summary()
        progress_frame = tk.Frame(self.main_frame, bg="#1e3a8a", relief="raised", bd=5)
        progress_frame.pack(pady=20, padx=100)
        
        overall_label = tk.Label(
            progress_frame,
            text=f"✨ Overall Progress: {summary['revealed_gifts']}/30 ({summary['completion_percentage']:.1f}%) ✨",
            font=self.large_font,
            bg="#1e3a8a",
            fg="#FFD700"
        )
        overall_label.pack(pady=20)
        
        remaining_label = tk.Label(
            progress_frame,
            text=f"🎁 Magical Surprises Remaining: {summary['remaining_gifts']} 🎁",
            font=self.subtitle_font,
            bg="#1e3a8a",
            fg="#FFFFFF"
        )
        remaining_label.pack(pady=10)
        
        # Back button
        back_btn = tk.Button(
            self.main_frame,
            text="⬅️ Back to Menu",
            font=self.body_font,
            bg="#4169E1",
            fg="#FFFFFF",
            command=self.show_welcome_screen,
            width=20,
            height=2
        )
        back_btn.pack(pady=40)
    
    def set_game_mode(self, mode: str):
        """Set the game mode."""
        self.game_logic.session.mode = mode
        self.game_logic.save_progress()
    
    def confirm_reset(self):
        """Confirm game reset with user."""
        result = messagebox.askyesno(
            "Reset Magical Adventure",
            "Are you sure you want to reset the entire magical adventure?\n\n"
            "This will clear all progress and start fresh.\n"
            "This action cannot be undone!"
        )
        
        if result:
            success = self.game_logic.reset_game()
            if success:
                messagebox.showinfo("Reset Complete", "Magical adventure has been reset successfully!")
                self.show_welcome_screen()
            else:
                messagebox.showerror("Reset Failed", "Could not reset the game. Please try again.")

    def show_vapi_magic_screen(self):
        """Display the Vapi magic call screen with options."""
        self.clear_screen()
        self.current_screen = "vapi_magic"
        
        # Title
        title_label = tk.Label(
            self.main_frame,
            text="🤖 VAPI BIRTHDAY MAGIC! 🤖",
            font=self.title_font,
            bg="#0f1729",
            fg="#FFD700"
        )
        title_label.pack(pady=40)
        
        # Description
        desc_label = tk.Label(
            self.main_frame,
            text="✨ Trigger a magical birthday call to Rafa! ✨\n"
                 "The AI assistant will call and deliver birthday wishes!",
            font=self.subtitle_font,
            bg="#0f1729",
            fg="#FFFFFF",
            justify=tk.CENTER
        )
        desc_label.pack(pady=30)
        
        # Call button
        call_frame = tk.Frame(self.main_frame, bg="#0f1729")
        call_frame.pack(pady=50)
        
        trigger_call_btn = tk.Button(
            call_frame,
            text="📞 TRIGGER BIRTHDAY CALL! 📞",
            font=self.huge_font,
            bg="#32CD32",  # Green
            fg="#FFFFFF",
            command=self.trigger_birthday_call,
            width=30,
            height=4,
            relief="raised",
            bd=8,
            cursor="hand2"
        )
        trigger_call_btn.pack(pady=30)
        
        # Info section
        info_frame = tk.Frame(self.main_frame, bg="#1e3a8a", relief="raised", bd=5)
        info_frame.pack(pady=40, padx=100)
        
        info_label = tk.Label(
            info_frame,
            text="🎂 Call Features 🎂\n\n"
                 "• AI-powered birthday wishes\n"
                 "• Disney-themed conversation\n"
                 "• Magical surprise delivery\n"
                 "• Real-time call initiation",
            font=self.body_font,
            bg="#1e3a8a",
            fg="#FFFFFF",
            justify=tk.LEFT
        )
        info_label.pack(pady=30, padx=30)
        
        # Back button
        back_btn = tk.Button(
            self.main_frame,
            text="🏠 Back to Home",
            font=self.body_font,
            bg="#4169E1",
            fg="#FFFFFF",
            command=self.show_welcome_screen,
            width=20,
            height=3
        )
        back_btn.pack(pady=40)

    def trigger_birthday_call(self):
        """Trigger a birthday call using Vapi API."""
        try:
            # Show loading message
            loading_popup = tk.Toplevel(self.root)
            loading_popup.title("Calling...")
            loading_popup.geometry("400x200")
            loading_popup.configure(bg="#0f1729")
            loading_popup.resizable(False, False)
            
            # Center the popup
            loading_popup.transient(self.root)
            loading_popup.grab_set()
            
            loading_label = tk.Label(
                loading_popup,
                text="📞 Initiating magical call...\n\n✨ Please wait ✨",
                font=self.subtitle_font,
                bg="#0f1729",
                fg="#FFD700",
                justify=tk.CENTER
            )
            loading_label.pack(expand=True)
            
            # Update the GUI
            self.root.update()
            
            # Get a random revealed gift for context (or None if no gifts revealed)
            revealed_gifts = [g for g in self.game_logic.gifts if g.revealed]
            present_id = revealed_gifts[-1].id if revealed_gifts else None
            
            # Make the API call
            logger.info("Attempting to trigger Vapi birthday call")
            result = vapi_client.create_call(
                present_id=present_id,
                custom_message="Happy 30th Birthday Rafa! Disney magic is calling!"
            )
            
            # Close loading popup
            loading_popup.destroy()
            
            # Show result
            if result["success"]:
                success_popup = tk.Toplevel(self.root)
                success_popup.title("🎉 Call Initiated!")
                success_popup.geometry("500x300")
                success_popup.configure(bg="#228B22")
                success_popup.resizable(False, False)
                
                success_popup.transient(self.root)
                success_popup.grab_set()
                
                success_title = tk.Label(
                    success_popup,
                    text="🎉 BIRTHDAY CALL INITIATED! 🎉",
                    font=self.large_font,
                    bg="#228B22",
                    fg="#FFFFFF"
                )
                success_title.pack(pady=20)
                
                success_message = tk.Label(
                    success_popup,
                    text=f"✨ {result['message']} ✨\n\n"
                         f"📞 The magical call is now in progress!\n"
                         f"🎂 Rafa should receive the birthday call shortly!\n\n"
                         f"Call ID: {result.get('call_id', 'N/A')}",
                    font=self.body_font,
                    bg="#228B22",
                    fg="#FFFFFF",
                    justify=tk.CENTER
                )
                success_message.pack(pady=20, padx=20)
                
                ok_btn = tk.Button(
                    success_popup,
                    text="🌟 Awesome! 🌟",
                    font=self.body_font,
                    bg="#FFD700",
                    fg="#000000",
                    command=success_popup.destroy,
                    width=15,
                    height=2
                )
                ok_btn.pack(pady=20)
                
                logger.info(f"Vapi call initiated successfully: {result['call_id']}")
                
            else:
                error_popup = tk.Toplevel(self.root)
                error_popup.title("❌ Call Failed")
                error_popup.geometry("500x300")
                error_popup.configure(bg="#DC143C")
                error_popup.resizable(False, False)
                
                error_popup.transient(self.root)
                error_popup.grab_set()
                
                error_title = tk.Label(
                    error_popup,
                    text="❌ CALL FAILED ❌",
                    font=self.large_font,
                    bg="#DC143C",
                    fg="#FFFFFF"
                )
                error_title.pack(pady=20)
                
                error_message = tk.Label(
                    error_popup,
                    text=f"😞 {result['message']}\n\n"
                         f"Error: {result.get('error', 'Unknown error')}\n\n"
                         f"Please check the configuration and try again.",
                    font=self.body_font,
                    bg="#DC143C",
                    fg="#FFFFFF",
                    justify=tk.CENTER
                )
                error_message.pack(pady=20, padx=20)
                
                retry_btn = tk.Button(
                    error_popup,
                    text="🔄 Close",
                    font=self.body_font,
                    bg="#FFFFFF",
                    fg="#DC143C",
                    command=error_popup.destroy,
                    width=15,
                    height=2
                )
                retry_btn.pack(pady=20)
                
                logger.error(f"Vapi call failed: {result.get('error')}")
                
        except Exception as e:
            # Close loading popup if it exists
            try:
                loading_popup.destroy()
            except:
                pass
                
            error_msg = f"Unexpected error during call: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror(
                "Call Error",
                f"An unexpected error occurred:\n\n{error_msg}\n\nPlease try again."
            )
    
    def show_error_and_return(self):
        """Show error message and return to welcome screen."""
        messagebox.showerror(
            "Oracle Error",
            "The Disney spirits encountered an issue.\n"
            "Returning to the main menu..."
        )
        self.show_welcome_screen() 