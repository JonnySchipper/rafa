"""
Disney Wish Oracle - Web Server
Flask server for web UI and remote gift reveal triggers via HTTP POST requests.
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
import logging
import threading
import queue
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any

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
    return gift_id in SPECIAL_GIFT_IDS

class WebhookServer:
    """Flask webhook server for remote gift reveals."""
    
    def __init__(self, port: int = 5000, host: str = '0.0.0.0'):
        # Set up Flask app with template and static folders
        template_folder = os.path.join(os.path.dirname(__file__), 'templates')
        static_folder = os.path.join(os.path.dirname(__file__), 'static')
        
        self.app = Flask(__name__, 
                        template_folder=template_folder, 
                        static_folder=static_folder)
        self.port = port
        self.host = host
        self.server_thread: Optional[threading.Thread] = None
        self.reveal_queue = queue.Queue()
        self.game_logic = None
        self.running = False
        
        # Configure Flask logging to be less verbose
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        
        # Set up routes
        self.setup_routes()
    
    def setup_routes(self):
        """Set up Flask routes for the web server."""
        
        @self.app.route('/', methods=['GET'])
        def intro():
            """Intro screen with start button and video."""
            cache_bust = str(int(time.time()))
            return render_template('intro.html', cache_bust=cache_bust)
        
        @self.app.route('/main', methods=['GET'])
        def main_app():
            """Main gift selection interface."""
            if not self.game_logic:
                return jsonify({'error': 'Game logic not initialized'}), 500
            
            # Get available gifts for display
            available_gifts = self.game_logic.get_available_gifts()
            revealed_gifts = self.game_logic.get_revealed_gifts()
            all_gifts = self.game_logic.gifts  # Full ordered list for position calculation
            total_gifts = len(self.game_logic.gifts)
            
            # Create summary data that the template expects
            summary = {
                'revealed_gifts': len(revealed_gifts),
                'remaining_gifts': len(available_gifts),
                'total_gifts': total_gifts,
                'completion_percentage': (len(revealed_gifts) / total_gifts * 100) if total_gifts > 0 else 0,
                'is_complete': len(available_gifts) == 0
            }
            
            # Get current session data
            session_data = {
                'total_revealed': self.game_logic.session.total_revealed,
                'mode': self.game_logic.session.mode
            }
            
            # Add special gift information to the template context
            def is_special_gift_for_template(gift_id):
                SPECIAL_GIFT_IDS = {28, 24, 19}
                return gift_id in SPECIAL_GIFT_IDS
            
            cache_bust = str(int(time.time()))
            return render_template('index.html',
                                 summary=summary,
                                 available_gifts=available_gifts,
                                 revealed_gifts=revealed_gifts,
                                 all_gifts=all_gifts,
                                 total_gifts=total_gifts,
                                 session_data=session_data,
                                 cache_bust=cache_bust,
                                 is_special_gift=is_special_gift_for_template)
        
        @self.app.route('/gift_reveal', methods=['GET'])
        def gift_reveal():
            """Gift reveal page."""
            cache_bust = str(int(time.time()))
            return render_template('gift_reveal.html', cache_bust=cache_bust)
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'active',
                'service': 'Rafa\'s Wishes Web Server',
                'version': '3.0',
                'endpoints': {
                    'web_ui': 'GET /',
                    'reveal_present': 'POST /reveal_present',
                    'status': 'GET /status',
                    'health': 'GET /health'
                }
            })
        
        @self.app.route('/status', methods=['GET'])
        def status():
            """Get current game status."""
            if not self.game_logic:
                return jsonify({'error': 'Game logic not initialized'}), 500
            
            try:
                summary = self.game_logic.get_game_summary()
                available_gifts = self.game_logic.get_available_gifts()
                
                return jsonify({
                    'total_gifts': summary['total_gifts'],
                    'revealed_gifts': summary['revealed_gifts'],
                    'remaining_gifts': summary['remaining_gifts'],
                    'completion_percentage': summary['completion_percentage'],
                    'is_complete': summary['is_complete'],
                    'available_gift_ids': [gift.id for gift in available_gifts]
                })
            except Exception as e:
                logger.error(f"Error getting game status: {e}")
                return jsonify({'error': 'Failed to get game status'}), 500
        
        @self.app.route('/reveal_present', methods=['POST'])
        def reveal_present():
            """Handle gift reveal webhook requests."""
            try:
                # Validate request
                if not request.is_json:
                    return jsonify({'error': 'Request must be JSON'}), 400
                
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'Invalid JSON data'}), 400
                
                # Extract present_id
                present_id = data.get('present_id')
                if present_id is None:
                    return jsonify({'error': 'Missing present_id field'}), 400
                
                try:
                    present_id = int(present_id)
                except (ValueError, TypeError):
                    return jsonify({'error': 'present_id must be an integer'}), 400
                
                # Validate present_id range
                if present_id < 1 or present_id > 30:
                    return jsonify({'error': 'present_id must be between 1 and 30'}), 400
                
                # Check if game logic is available
                if not self.game_logic:
                    return jsonify({'error': 'Game logic not initialized'}), 500
                
                # Check if gift exists and is available
                gift = self.game_logic.get_gift_by_id(present_id)
                if not gift:
                    return jsonify({'error': f'Gift {present_id} not found'}), 404
                
                if gift.revealed:
                    return jsonify({
                        'error': f'Gift {present_id} has already been revealed',
                        'revealed_at': gift.revealed_at,
                        'revealed_by': gift.revealed_by
                    }), 409
                
                # Reveal the gift immediately for all gifts
                logger.info(f"Webhook reveal for gift #{present_id} from {request.remote_addr}")
                
                # Find matching character
                character = self.game_logic.find_best_character_match(gift)
                
                # Reveal the gift directly
                success = self.game_logic.reveal_gift(gift, character)
                
                if success:
                    reveal_type = 'special_gift' if is_special_gift(present_id, self.game_logic.gifts if self.game_logic else None) else 'regular_gift'
                    
                    return jsonify({
                        'success': True,
                        'message': f'Gift {present_id} revealed successfully!',
                        'present_id': present_id,
                        'status': 'revealed',
                        'revealed_by': character.name,
                        'reveal_type': reveal_type,
                        'is_special_gift': is_special_gift(present_id, self.game_logic.gifts if self.game_logic else None),
                        'gift_description': gift.description
                    })
                else:
                    return jsonify({'error': 'Failed to reveal gift'}), 500
                
            except Exception as e:
                logger.error(f"Error processing reveal request: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/reveal_random', methods=['POST'])
        def reveal_random():
            """Reveal the next available special gift (5, 10, 15, 20, 25, 30)."""
            try:
                if not self.game_logic:
                    return jsonify({'error': 'Game logic not initialized'}), 500
                
                available_gifts = self.game_logic.get_available_gifts()
                if not available_gifts:
                    return jsonify({'error': 'No gifts available to reveal'}), 404
                
                # Find the next unrevealed special gift
                special_gift_ids = [28, 24, 19]
                next_special_gift = None
                
                for special_id in special_gift_ids:
                    gift = self.game_logic.get_gift_by_id(special_id)
                    if gift and not gift.revealed:
                        next_special_gift = gift
                        break
                
                # If no special gifts available, fall back to next available gift
                if not next_special_gift:
                    next_special_gift = self.game_logic.select_next_gift()
                    
                if not next_special_gift:
                    return jsonify({'error': 'No gifts available to reveal'}), 404
                
                # Reveal the gift immediately instead of queuing
                character = self.game_logic.find_best_character_match(next_special_gift)
                success = self.game_logic.reveal_gift(next_special_gift, character)
                
                if success:
                    logger.info(f"Special gift #{next_special_gift.id} revealed via webhook from {request.remote_addr}")
                    
                    return jsonify({
                        'success': True,
                        'message': f'Special gift {next_special_gift.id} revealed successfully!',
                        'present_id': next_special_gift.id,
                        'status': 'revealed',
                        'revealed_by': character.name,
                        'is_special_gift': is_special_gift(next_special_gift.id, self.game_logic.gifts if self.game_logic else None),
                        'gift_description': next_special_gift.description
                    })
                else:
                    return jsonify({'error': 'Failed to reveal gift'}), 500
                
            except Exception as e:
                logger.error(f"Error processing random reveal request: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # API endpoints for the web UI
        @self.app.route('/api/game_status', methods=['GET'])
        def get_game_status():
            """Get current game status for web UI."""
            if not self.game_logic:
                return jsonify({'error': 'Game logic not initialized'}), 500
            
            try:
                summary = self.game_logic.get_game_summary()
                available_gifts = self.game_logic.get_available_gifts()
                all_gifts = self.game_logic.gifts  # Full ordered list
                
                # Convert available gifts to dictionaries
                available_gifts_data = []
                for gift in available_gifts:
                    gift_data = {
                        'id': gift.id,
                        'description': gift.description,
                        'themes': gift.themes,
                        'image_path': gift.image_path,
                        'revealed': gift.revealed,
                        'revealed_at': gift.revealed_at,
                        'revealed_by': gift.revealed_by
                    }
                    available_gifts_data.append(gift_data)
                
                # Convert all gifts to dictionaries
                all_gifts_data = []
                for gift in all_gifts:
                    gift_data = {
                        'id': gift.id,
                        'description': gift.description,
                        'themes': gift.themes,
                        'image_path': gift.image_path,
                        'revealed': gift.revealed,
                        'revealed_at': gift.revealed_at,
                        'revealed_by': gift.revealed_by
                    }
                    all_gifts_data.append(gift_data)
                
                return jsonify({
                    'success': True,
                    'summary': summary,
                    'available_gifts': available_gifts_data,
                    'all_gifts': all_gifts_data
                })
            except Exception as e:
                logger.error(f"Error getting game status: {e}")
                return jsonify({'error': 'Failed to get game status'}), 500
        
        @self.app.route('/api/spin_wheel', methods=['POST'])
        def spin_wheel_api():
            """Handle wheel spin from web UI."""
            if not self.game_logic:
                return jsonify({'error': 'Game logic not initialized'}), 500
            
            try:
                data = request.get_json()
                if not data or 'gift_id' not in data:
                    return jsonify({'error': 'Missing gift_id'}), 400
                
                gift_id = data['gift_id']
                gift = self.game_logic.get_gift_by_id(gift_id)
                
                if not gift:
                    return jsonify({'error': f'Gift {gift_id} not found'}), 404
                
                if gift.revealed:
                    return jsonify({'error': f'Gift {gift_id} already revealed'}), 409
                
                # Find matching character
                character = self.game_logic.find_best_character_match(gift)
                
                # Generate magical message
                from api_integration import grok_client
                try:
                    character_dict = {
                        'name': character.name,
                        'personality': character.personality,
                        'voice_style': character.voice_style
                    }
                    
                    gift_dict = {
                        'id': gift.id,
                        'description': "a magical birthday surprise",
                        'themes': gift.themes
                    }
                    
                    message = grok_client.generate_gift_reveal(
                        character_dict, 
                        gift_dict, 
                        ["birthday magic", "surprise", "wonder", "Disney dreams"]
                    )
                except Exception as e:
                    logger.warning(f"Failed to generate AI message: {e}")
                    message = f"🎁 {character.name} has chosen a special magical surprise for you! The spirits have selected Gift #{gift.id}! Open it to discover the wonder within! Happy 30th Birthday, Rafa! ✨🎂"
                
                # Prepare response data
                character_data = {
                    'name': character.name,
                    'personality': character.personality,
                    'voice_style': character.voice_style,
                    'image_path': character.image_path,
                    'image_url': f"/static/images/{os.path.basename(character.image_path)}" if character.image_path and os.path.exists(character.image_path) else None
                }
                
                gift_data = {
                    'id': gift.id,
                    'description': gift.description,
                    'themes': gift.themes,
                    'image_path': gift.image_path,
                    'image_url': f"/static/images/{os.path.basename(gift.image_path)}" if gift.image_path and os.path.exists(gift.image_path) else None
                }
                
                return jsonify({
                    'success': True,
                    'gift': gift_data,
                    'character': character_data,
                    'message': message
                })
                
            except Exception as e:
                logger.error(f"Error in spin_wheel_api: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/accept_gift', methods=['POST'])
        def accept_gift_api():
            """Accept a gift reveal from web UI."""
            if not self.game_logic:
                return jsonify({'error': 'Game logic not initialized'}), 500
            
            try:
                data = request.get_json()
                if not data or 'gift_id' not in data or 'character_name' not in data:
                    return jsonify({'error': 'Missing gift_id or character_name'}), 400
                
                gift_id = data['gift_id']
                character_name = data['character_name']
                
                gift = self.game_logic.get_gift_by_id(gift_id)
                if not gift:
                    return jsonify({'error': f'Gift {gift_id} not found'}), 404
                
                character = self.game_logic.find_character_by_name(character_name)
                if not character:
                    return jsonify({'error': f'Character {character_name} not found'}), 404
                
                # Reveal the gift
                success = self.game_logic.reveal_gift(gift, character)
                
                if success:
                    return jsonify({'success': True, 'message': 'Gift revealed successfully'})
                else:
                    return jsonify({'error': 'Failed to reveal gift'}), 500
                    
            except Exception as e:
                logger.error(f"Error in accept_gift_api: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/save_settings', methods=['POST'])
        def save_settings_api():
            """Save game settings from web UI."""
            if not self.game_logic:
                return jsonify({'error': 'Game logic not initialized'}), 500
            
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No settings data provided'}), 400
                
                if 'mode' in data:
                    self.game_logic.session.mode = data['mode']
                    self.game_logic.save_progress()
                
                return jsonify({'success': True, 'message': 'Settings saved successfully'})
                
            except Exception as e:
                logger.error(f"Error saving settings: {e}")
                return jsonify({'error': 'Failed to save settings'}), 500
        
        @self.app.route('/api/trigger_call', methods=['POST'])
        def trigger_call_api():
            """Trigger VAPI call with specific Disney assistant."""
            try:
                logger.info("VAPI Disney character call trigger endpoint hit")
                
                # Get request data for gift-specific calls
                data = request.get_json() or {}
                gift_id = data.get('gift_id')
                phone_number = data.get('phone_number', '+1234567890')  # Placeholder
                custom_message = data.get('message', f"Happy 30th Birthday Rafa! Disney magic is revealing gift #{gift_id}!")
                
                # VAPI Assistant ID for Disney character calls
                assistant_id = 'b4f5f908-8c08-4c28-b4f7-37a9a43f2833'
                
                logger.info(f"Triggering VAPI call for gift #{gift_id} with assistant {assistant_id}")
                
                try:
                    # Try to use existing VAPI integration if available
                    from api_integration import vapi_client
                    
                    # Make the API call (assistant ID and phone number are pre-configured in the client)
                    result = vapi_client.create_call(
                        present_id=gift_id,
                        custom_message=custom_message
                    )
                    
                    # Save progress to persist agent cycling state
                    if self.game_logic:
                        self.game_logic.save_progress()
                        logger.info("Progress saved after agent cycling")
                    
                    return jsonify(result)
                    
                except ImportError:
                    # Fallback: Return a simulated successful response
                    logger.warning("VAPI client not available, returning simulated response")
                    result = {
                        'success': True,
                        'call_id': f'vapi_call_{int(time.time())}',
                        'assistant_id': assistant_id,
                        'gift_id': gift_id,
                        'phone_number': phone_number,
                        'message': 'VAPI Disney character call initiated successfully!',
                        'status': 'simulated'
                    }
                    return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error triggering VAPI call: {e}")
                return jsonify({
                    'success': False,
                    'message': 'Failed to trigger Disney character call',
                    'error': str(e)
                })
        
        @self.app.route('/api/reveal_gift', methods=['POST'])
        def reveal_gift_api():
            """Mark a gift as revealed."""
            if not self.game_logic:
                return jsonify({'error': 'Game logic not initialized'}), 500
            
            try:
                data = request.get_json()
                gift_id = data.get('gift_id')
                
                if not gift_id:
                    return jsonify({'error': 'Gift ID is required'}), 400
                
                # Find the gift
                gift = self.game_logic.get_gift_by_id(gift_id)
                if not gift:
                    return jsonify({'error': f'Gift {gift_id} not found'}), 404
                
                if gift.revealed:
                    return jsonify({'error': f'Gift {gift_id} is already revealed'}), 400
                
                # Mark gift as revealed
                gift.revealed = True
                gift.revealed_at = datetime.now().isoformat()
                gift.revealed_by = 'web_interface'
                
                # Update session
                self.game_logic.session.total_revealed += 1
                self.game_logic.session.last_played = datetime.now().isoformat()
                
                # Save progress
                self.game_logic.save_progress()
                
                logger.info(f"Gift {gift_id} marked as revealed via web interface")
                
                return jsonify({
                    'success': True,
                    'message': f'Gift {gift_id} has been revealed!',
                    'gift': {
                        'id': gift.id,
                        'description': gift.description,
                        'revealed': gift.revealed,
                        'revealed_at': gift.revealed_at
                    }
                })
                
            except Exception as e:
                logger.error(f"Error revealing gift: {e}")
                return jsonify({'error': 'Failed to reveal gift'}), 500
        
        @self.app.route('/api/recent_reveals', methods=['GET'])
        def get_recent_reveals():
            """Get recently revealed gifts to notify the web UI of webhook reveals."""
            if not self.game_logic:
                return jsonify({'error': 'Game logic not initialized'}), 500
            
            try:
                # Get all revealed gifts and sort by revealed time
                all_gifts = self.game_logic.gifts
                recent_reveals = []
                
                # Get reveals from the last 10 seconds (shorter window to avoid duplicates)
                from datetime import datetime, timedelta
                cutoff_time = datetime.now() - timedelta(seconds=10)
                
                for gift in all_gifts:
                    if gift.revealed and gift.revealed_at:
                        try:
                            revealed_time = datetime.fromisoformat(gift.revealed_at.replace('Z', '+00:00').replace('+00:00', ''))
                            if revealed_time > cutoff_time:
                                recent_reveals.append({
                                    'id': gift.id,
                                    'description': gift.description,
                                    'revealed_at': gift.revealed_at,
                                    'revealed_by': getattr(gift, 'revealed_by', 'unknown'),
                                    'is_special_gift': is_special_gift(gift.id, self.game_logic.gifts if self.game_logic else None)
                                })
                        except:
                            # Skip if time parsing fails
                            continue
                
                return jsonify({
                    'success': True,
                    'recent_reveals': recent_reveals,
                    'count': len(recent_reveals)
                })
                
            except Exception as e:
                logger.error(f"Error getting recent reveals: {e}")
                return jsonify({'error': 'Failed to get recent reveals'}), 500
        
        @self.app.route('/api/reset_game', methods=['POST'])
        def reset_game_api():
            """Reset the game from web UI."""
            if not self.game_logic:
                return jsonify({'error': 'Game logic not initialized'}), 500
            
            try:
                success = self.game_logic.reset_game()
                
                if success:
                    return jsonify({'success': True, 'message': 'Game reset successfully'})
                else:
                    return jsonify({'error': 'Failed to reset game'}), 500
                    
            except Exception as e:
                logger.error(f"Error resetting game: {e}")
                return jsonify({'error': 'Failed to reset game'}), 500
        
        # Serve asset files (videos and images)
        @self.app.route('/static/assets/<filename>')
        def serve_asset(filename):
            """Serve asset files including videos and images."""
            assets_path = os.path.join(os.path.dirname(__file__), 'assets')
            if os.path.exists(os.path.join(assets_path, filename)):
                return send_from_directory(assets_path, filename)
            return "Asset not found", 404
        
        # Serve gift and character images
        @self.app.route('/static/images/<filename>')
        def serve_image(filename):
            """Serve gift and character images."""
            assets_path = os.path.join(os.path.dirname(__file__), 'assets', 'images')
            full_path = os.path.join(assets_path, filename)
            
            logger.info(f"🔍 Serving image request: {filename}")
            logger.info(f"📁 Looking in: {assets_path}")
            logger.info(f"📄 Full path: {full_path}")
            logger.info(f"✅ File exists: {os.path.exists(full_path)}")
            
            if os.path.exists(full_path):
                logger.info(f"✅ Serving file: {filename}")
                return send_from_directory(assets_path, filename)
            else:
                logger.warning(f"❌ File not found: {filename}")
                return f"File not found: {filename}", 404
    
    def set_game_logic(self, game_logic):
        """Set the game logic instance for webhook operations."""
        self.game_logic = game_logic
        logger.info("Game logic connected to webhook server")
    
    def start_server(self):
        """Start the Flask server in a separate thread."""
        if self.running:
            logger.warning("Webhook server is already running")
            return
        
        def run_server():
            try:
                logger.info(f"Starting Disney Wish Oracle webhook server on {self.host}:{self.port}")
                self.app.run(host=self.host, port=self.port, debug=False, threaded=True)
            except Exception as e:
                logger.error(f"Failed to start webhook server: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True
        
        logger.info(f"Webhook server thread started - accessible at http://{self.host}:{self.port}")
        logger.info("Available endpoints:")
        logger.info("  GET  / - Health check")
        logger.info("  GET  /status - Game status")
        logger.info("  POST /reveal_present - Reveal specific gift")
        logger.info("  POST /reveal_random - Reveal random gift")
    
    def stop_server(self):
        """Stop the Flask server."""
        if not self.running:
            return
        
        # Note: Flask development server doesn't have a clean shutdown method
        # In production, you'd use a proper WSGI server like Gunicorn
        self.running = False
        logger.info("Webhook server stopped")
    
    def get_pending_reveals(self) -> list:
        """Get all pending reveal requests from the queue."""
        reveals = []
        while not self.reveal_queue.empty():
            try:
                reveal = self.reveal_queue.get_nowait()
                reveals.append(reveal)
            except queue.Empty:
                break
        return reveals
    
    def has_pending_reveals(self) -> bool:
        """Check if there are pending reveal requests."""
        return not self.reveal_queue.empty()

# Global webhook server instance
webhook_server = WebhookServer() 