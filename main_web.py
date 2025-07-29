#!/usr/bin/env python3
"""
Disney Wish Oracle - Web Server Entry Point
A magical gift-revealing game for Rafa's 30th birthday Disney trip!
Now served as a web application with webhook support for remote gift reveals!
"""

import os
import sys
import logging
import signal
import threading
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_logic import GameLogic
from webhook_server import webhook_server

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DisneyWishOracleWebServer:
    """Main web application controller with webhook integration."""
    
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.game_logic = None
        self.server_running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def initialize_game_logic(self):
        """Initialize the game logic."""
        try:
            self.game_logic = GameLogic()
            logger.info("Game logic initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize game logic: {e}")
            return False
    
    def setup_webhook_integration(self):
        """Set up webhook server integration."""
        try:
            # Connect game logic to webhook server
            webhook_server.set_game_logic(self.game_logic)
            logger.info("Webhook integration setup complete")
            return True
        except Exception as e:
            logger.error(f"Failed to setup webhook integration: {e}")
            return False
    
    def start_server(self):
        """Start the Flask web server."""
        if not self.initialize_game_logic():
            logger.error("Failed to initialize game logic, cannot start server")
            return False
        
        if not self.setup_webhook_integration():
            logger.error("Failed to setup webhook integration")
            return False
        
        try:
            logger.info("Starting Rafa's Wishes Web Server...")
            logger.info(f"🌐 Server will be available at: http://{self.host}:{self.port}")
            if self.host == '0.0.0.0':
                logger.info(f"🔗 Local access: http://localhost:{self.port}")
            logger.info("🎯 Available endpoints:")
            logger.info("  • GET  / - Main web interface")
            logger.info("  • GET  /health - Health check")
            logger.info("  • GET  /status - Game status")
            logger.info("  • POST /reveal_present - Reveal specific gift (webhook)")
            logger.info("  • POST /reveal_random - Reveal random gift (webhook)")
            logger.info("  • POST /api/* - Web UI API endpoints")
            logger.info("")
            logger.info("✨ Disney magic is ready! Access the web interface in your browser ✨")
            logger.info("🎂 Perfect for Rafa's 30th birthday celebration! 🎂")
            logger.info("")
            logger.info("Press Ctrl+C to stop the server")
            
            self.server_running = True
            
            # Start the Flask server (this blocks)
            webhook_server.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                threaded=True,
                use_reloader=False  # Disable reloader to avoid duplicate processes
            )
            
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            return False
        finally:
            self.server_running = False
    
    def shutdown(self):
        """Clean shutdown of the server."""
        logger.info("Shutting down Rafa's Wishes Web Server...")
        
        try:
            # Save game progress
            if self.game_logic:
                self.game_logic.save_progress()
                logger.info("Game progress saved")
        except Exception as e:
            logger.warning(f"Error saving game progress: {e}")
        
        try:
            # Stop webhook server
            webhook_server.stop_server()
            logger.info("Webhook server stopped")
        except Exception as e:
            logger.warning(f"Error stopping webhook server: {e}")
        
        logger.info("Shutdown complete. Thank you for using Disney Wish Oracle! ✨")

def print_startup_banner():
    """Print a magical startup banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        ✨ RAFA'S WISHES WEB SERVER ✨                        ║
║                                                                              ║
║                    🎂 Rafa's Magical 30th Birthday Adventure 🎂              ║
║                                                                              ║
║                           Fort Wilderness Edition                           ║
║                                                                              ║
║  🌟 Now available as a web application!                                     ║
║  🎡 Spin the wheel from any device                                          ║
║  🌐 Remote webhook support for surprise reveals                             ║
║  🎁 30 magical gifts await discovery                                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def validate_environment():
    """Validate that required files and directories exist."""
    required_paths = [
        'data/characters.json',
        'data/gifts.json',
        'templates/base.html',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js',
        'static/js/wheel.js'
    ]
    
    missing_paths = []
    for path in required_paths:
        if not os.path.exists(path):
            missing_paths.append(path)
    
    if missing_paths:
        logger.error("Missing required files:")
        for path in missing_paths:
            logger.error(f"  - {path}")
        return False
    
    logger.info("Environment validation passed ✅")
    return True

def main():
    """Main entry point for the Disney Wish Oracle Web Server."""
    print_startup_banner()
    
    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed. Please ensure all required files are present.")
        sys.exit(1)
    
    # Get host and port from environment variables or use defaults
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    
    # Create and start the server
    server = DisneyWishOracleWebServer(host=host, port=port)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        server.shutdown()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        server.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    main() 