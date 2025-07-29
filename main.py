#!/usr/bin/env python3
"""
Disney Wish Oracle - Main Entry Point
A magical gift-revealing game for Rafa's 30th birthday Disney trip!
Now with webhook support for remote gift reveals!
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys
import threading
import logging

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui_components import DisneyWishOracleApp
from game_logic import GameLogic
from webhook_server import webhook_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DisneyWishOracleWithWebhooks:
    """Main application controller with webhook integration."""
    
    def __init__(self):
        self.root = None
        self.app = None
        self.game_logic = None
        self.webhook_check_interval = 100  # Check for webhooks every 100ms
        
    def setup_webhook_integration(self):
        """Set up webhook server integration."""
        try:
            # Connect game logic to webhook server
            webhook_server.set_game_logic(self.game_logic)
            
            # Start webhook server
            webhook_server.start_server()
            
            # Start checking for webhook requests
            self.check_webhook_requests()
            
            logger.info("Webhook integration setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup webhook integration: {e}")
            messagebox.showwarning(
                "Webhook Warning", 
                f"Failed to start webhook server: {e}\n\nThe app will still work normally without webhook support."
            )
    
    def check_webhook_requests(self):
        """Check for pending webhook requests and process them."""
        try:
            if webhook_server.has_pending_reveals():
                reveals = webhook_server.get_pending_reveals()
                for reveal_request in reveals:
                    self.process_webhook_reveal(reveal_request)
        
        except Exception as e:
            logger.error(f"Error checking webhook requests: {e}")
        
        # Schedule next check
        if self.root:
            self.root.after(self.webhook_check_interval, self.check_webhook_requests)
    
    def process_webhook_reveal(self, reveal_request):
        """Process a webhook reveal request in the main thread."""
        try:
            present_id = reveal_request['present_id']
            source = reveal_request.get('source', 'webhook')
            remote_ip = reveal_request.get('remote_ip', 'unknown')
            
            logger.info(f"Processing webhook reveal for gift #{present_id} from {remote_ip}")
            
            # Get the gift
            gift = self.game_logic.get_gift_by_id(present_id)
            if not gift:
                logger.error(f"Gift #{present_id} not found")
                return
            
            if gift.revealed:
                logger.warning(f"Gift #{present_id} already revealed, ignoring webhook")
                return
            
            # Find matching character
            character = self.game_logic.find_best_character_match(gift)
            
            # Set current gift and character in the UI
            if self.app:
                self.app.current_gift = gift
                self.app.current_character = character
                
                # Show a webhook notification popup
                self.show_webhook_notification(present_id, source, remote_ip)
                
                # Trigger the reveal process
                self.app.generate_and_show_message()
            
        except Exception as e:
            logger.error(f"Error processing webhook reveal: {e}")
    
    def show_webhook_notification(self, present_id, source, remote_ip):
        """Show a notification about the webhook trigger."""
        try:
            # Create a custom notification window
            notification = tk.Toplevel(self.root)
            notification.title("🌐 Remote Reveal Triggered!")
            notification.geometry("500x300")
            notification.configure(bg="#0f1729")
            notification.resizable(False, False)
            
            # Center the notification
            notification.transient(self.root)
            notification.grab_set()
            
            # Notification content
            title_label = tk.Label(
                notification,
                text="🌐 REMOTE REVEAL TRIGGERED! 🌐",
                font=("Arial", 18, "bold"),
                bg="#0f1729",
                fg="#FFD700"
            )
            title_label.pack(pady=20)
            
            message_label = tk.Label(
                notification,
                text=f"🎁 Gift #{present_id} has been remotely triggered!\n\n"
                     f"📡 Source: {source}\n"
                     f"🌍 From: {remote_ip}\n\n"
                     f"✨ Get ready for the magical reveal! ✨",
                font=("Arial", 12),
                bg="#0f1729",
                fg="#FFFFFF",
                justify=tk.CENTER
            )
            message_label.pack(pady=20)
            
            # Continue button
            continue_btn = tk.Button(
                notification,
                text="🎉 Continue to Reveal! 🎉",
                font=("Arial", 14, "bold"),
                bg="#FF1493",
                fg="#FFFFFF",
                command=notification.destroy,
                width=20,
                height=2
            )
            continue_btn.pack(pady=20)
            
            # Auto-close after 5 seconds
            notification.after(5000, notification.destroy)
            
        except Exception as e:
            logger.error(f"Error showing webhook notification: {e}")
    
    def run(self):
        """Run the Disney Wish Oracle application with webhook support."""
        try:
            # Initialize the game logic
            self.game_logic = GameLogic()
            
            # Create and configure the GUI application
            self.root = tk.Tk()
            self.app = DisneyWishOracleApp(self.root, self.game_logic)
            
            # Set up webhook integration
            self.setup_webhook_integration()
            
            # Center the window on screen
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
            # Add webhook info to window title
            self.root.title(self.root.title() + " 🌐 [Webhook Server Active]")
            
            # Show startup message with webhook info
            self.show_startup_message()
            
            # Start the application
            logger.info("Starting Disney Wish Oracle with webhook support")
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Failed to start Disney Wish Oracle: {e}")
            messagebox.showerror("Error", f"Failed to start Disney Wish Oracle: {str(e)}")
            sys.exit(1)
        finally:
            # Clean up webhook server
            try:
                webhook_server.stop_server()
            except:
                pass
    
    def show_startup_message(self):
        """Show startup message with webhook information."""
        try:
            webhook_info = tk.Toplevel(self.root)
            webhook_info.title("🌐 Webhook Server Active")
            webhook_info.geometry("600x400")
            webhook_info.configure(bg="#1e3a8a")
            webhook_info.resizable(False, False)
            
            # Center the window
            webhook_info.transient(self.root)
            
            # Content
            title_label = tk.Label(
                webhook_info,
                text="🚀 Disney Wish Oracle Ready! 🚀",
                font=("Arial", 20, "bold"),
                bg="#1e3a8a",
                fg="#FFD700"
            )
            title_label.pack(pady=20)
            
            info_text = """🌐 Webhook Server is ACTIVE! 🌐

🎯 Remote Control Endpoints:
• POST /reveal_present - Reveal specific gift
• POST /reveal_random - Reveal random gift  
• GET /status - Check game status
• GET / - Health check

🔗 Server URL: http://localhost:5000

📡 Example Usage:
curl -X POST http://localhost:5000/reveal_present \\
  -H "Content-Type: application/json" \\
  -d '{"present_id": 1}'

✨ Now you can trigger gift reveals remotely! ✨
Perfect for surprise reveals during the Disney trip!"""
            
            info_label = tk.Label(
                webhook_info,
                text=info_text,
                font=("Arial", 11),
                bg="#1e3a8a",
                fg="#FFFFFF",
                justify=tk.LEFT
            )
            info_label.pack(pady=20, padx=30)
            
            # Close button
            close_btn = tk.Button(
                webhook_info,
                text="🎉 Got it! Let's Start! 🎉",
                font=("Arial", 14, "bold"),
                bg="#32CD32",
                fg="#FFFFFF",
                command=webhook_info.destroy,
                width=25,
                height=2
            )
            close_btn.pack(pady=20)
            
            # Auto-close after 10 seconds
            webhook_info.after(10000, webhook_info.destroy)
            
        except Exception as e:
            logger.error(f"Error showing startup message: {e}")

def main():
    """Main entry point for the Disney Wish Oracle application."""
    app = DisneyWishOracleWithWebhooks()
    app.run()

if __name__ == "__main__":
    main() 