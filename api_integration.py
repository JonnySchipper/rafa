"""
Disney Wish Oracle - Grok API Integration
Handles all interactions with xAI's Grok API for dynamic content generation.
"""

import os
import json
import time
import requests
from typing import Dict, Optional, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrokAPIClient:
    """Client for interacting with xAI's Grok API."""
    
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY')
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }
        self.fallback_messages = self._load_fallback_messages()
        
    def _load_fallback_messages(self) -> Dict:
        """Load fallback messages for when API is unavailable."""
        return {
            "riddle": [
                "🎁 The magic reveals itself! Open gift #{gift_id}: {gift_description}! Happy 30th Birthday, Rafa! ✨",
                "🌟 A mystical gift awaits! Time to unwrap #{gift_id}: {gift_description}! Make a wish! 🎂",
                "✨ The oracle has spoken! Your next treasure is gift #{gift_id}: {gift_description}! 🎉"
            ],
            "trivia": [
                "Quick Disney question: What's Mickey Mouse's girlfriend's name? (Answer: Minnie Mouse!)",
                "Disney trivia: Which princess has the longest hair? (Answer: Rapunzel!)",
                "Fun fact: Which Disney character loves warm hugs? (Answer: Olaf!)"
            ],
            "celebration": [
                "🎉 Amazing job, Rafa! You've revealed another magical gift! The adventure continues... ✨",
                "🌟 The Disney magic is strong with you! Another gift discovered on your special day! 🎂",
                "✨ Wonderful! The oracle is pleased with your birthday wishes coming true! 🎁"
            ]
        }
    
    def is_api_available(self) -> bool:
        """Check if the Grok API is available and configured."""
        return bool(self.api_key)
    
    def generate_gift_reveal(self, character: Dict, gift: Dict, interests: Optional[List[str]] = None) -> str:
        """Generate a personalized gift reveal message from a Disney character."""
        if interests is None:
            interests = ["relaxation", "Disney", "Japan"]
            
        prompt = self._create_reveal_prompt(character, gift, interests)
        
        try:
            if not self.is_api_available():
                logger.warning("Grok API key not available, using fallback message")
                return self._get_fallback_message("riddle", gift)
                
            response = self._make_api_call(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating gift reveal: {e}")
            return self._get_fallback_message("riddle", gift)
    
    def generate_trivia_question(self, character: Dict) -> Dict[str, str]:
        """Generate a Disney trivia question from a character."""
        prompt = f"""As {character['name']}, create a fun, easy Disney trivia question about yourself or your movie. 
        Format your response as JSON with 'question', 'answer', and 'fun_fact' fields.
        Keep it simple and appropriate for all ages.
        Example: {{"question": "What's my favorite food?", "answer": "Beignets", "fun_fact": "I learned to cook from my father!"}}"""
        
        try:
            if not self.is_api_available():
                return self._get_fallback_trivia()
                
            response = self._make_api_call(prompt)
            trivia_data = json.loads(response)
            return trivia_data
            
        except Exception as e:
            logger.error(f"Error generating trivia: {e}")
            return self._get_fallback_trivia()
    
    def generate_day_recap(self, revealed_gifts: List[Dict], day: int) -> str:
        """Generate a recap of the day's revealed gifts."""
        gift_descriptions = [f"Gift #{g['id']}: {g['description']}" for g in revealed_gifts]
        gifts_text = ", ".join(gift_descriptions)
        
        prompt = f"""Create a magical, poetic recap of Rafa's Day {day} birthday gifts at Disney Fort Wilderness.
        Gifts revealed today: {gifts_text}
        
        Write a warm, celebratory paragraph (50-80 words) weaving these gifts into a cohesive story about Rafa's magical 30th birthday adventure.
        Include Disney magic and birthday wishes. Be joyful and personal."""
        
        try:
            if not self.is_api_available():
                return f"🎉 What a magical Day {day}, Rafa! You've discovered {len(revealed_gifts)} wonderful gifts on your Disney adventure. Each one brings more joy to your special 30th birthday celebration at Fort Wilderness! ✨🎂"
                
            response = self._make_api_call(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating day recap: {e}")
            return f"🎉 Day {day} has been magical, Rafa! {len(revealed_gifts)} amazing gifts revealed! Happy 30th! ✨"
    
    def _create_reveal_prompt(self, character: Dict, gift: Dict, interests: List[str]) -> str:
        """Create a prompt for gift reveal generation."""
        interests_text = ", ".join(interests)
        
        return f"""You are {character['name']}, a Disney character. {character['personality']}
        
        Create a fun, magical 50-70 word message revealing Rafa's birthday gift #{gift['id']}: {gift['description']}.
        
        Style guidelines:
        - Use {character['voice_style']} tone
        - Include birthday wishes for Rafa's 30th
        - Reference the gift themes: {', '.join(gift['themes'])}
        - Tie to Rafa's interests: {interests_text}
        - End with excitement about the gift
        - Use emojis sparingly but effectively
        - Stay in character as {character['name']}
        
        Make it feel personal and magical, like the character is really speaking to Rafa at Disney Fort Wilderness!"""
    
    def _make_api_call(self, prompt: str) -> str:
        """Make a call to the Grok API."""
        data = {
            "messages": [
                {"role": "system", "content": "You are a helpful, creative Disney character oracle."},
                {"role": "user", "content": prompt}
            ],
            "model": "grok-beta",
            "temperature": 0.8,
            "max_tokens": 200
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"API call failed: {response.status_code} - {response.text}")
    
    def _get_fallback_message(self, message_type: str, gift: Dict) -> str:
        """Get a fallback message when API is unavailable."""
        import random
        messages = self.fallback_messages.get(message_type, self.fallback_messages["riddle"])
        message = random.choice(messages)
        return message.format(gift_id=gift['id'], gift_description=gift['description'])
    
    def _get_fallback_trivia(self) -> Dict[str, str]:
        """Get fallback trivia when API is unavailable."""
        import random
        trivia_options = [
            {
                "question": "What's Mickey Mouse's girlfriend's name?",
                "answer": "Minnie Mouse",
                "fun_fact": "Mickey and Minnie have been together since 1928!"
            },
            {
                "question": "Which Disney princess has the longest hair?",
                "answer": "Rapunzel",
                "fun_fact": "Rapunzel's hair is 70 feet long when let down!"
            },
            {
                "question": "What does Baymax say when he's activated?",
                "answer": "Hello, I am Baymax",
                "fun_fact": "Baymax is a healthcare companion robot!"
            }
        ]
        return random.choice(trivia_options)

# Create a global instance
grok_client = GrokAPIClient()

class VapiClient:
    """Client for making outbound phone calls via Vapi API with cycling support."""
    
    def __init__(self):
        self.api_key = "02f5e3fa-6bd0-44a0-8d71-5aa4d2a69ebf"  # Provided API key
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Multiple agent/phone configurations for cycling
        self.agent_configs = [
            {
                "name": "Agent 1",
                "assistant_id": "b4f5f908-8c08-4c28-b4f7-37a9a43f2833",
                "phone_number_id": "958dd8c2-00f9-4b28-a0ae-e2de7fa64254",
                "phone_number": "Current Phone"  # Original phone number
            },
            {
                "name": "Agent 2", 
                "assistant_id": "faa5e904-9d4c-4472-a58c-434c1ff34ee7",
                "phone_number_id": "2fafd93d-48c2-4b34-b365-ae9884310767",  # +1 (448) 228 6708
                "phone_number": "+1 (448) 228 6708"
            }
        ]
        
        # Rafa's phone number (destination/TO number) - always the same
        self.rafa_phone = "+18633320003"
        
        # Current agent index for cycling (will be loaded from progress)
        self.current_agent_index = 0
        
    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """Check if a string is a valid UUID format."""
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        return bool(uuid_pattern.match(uuid_string))
        
    def get_next_agent_config(self) -> Dict:
        """Get the next agent configuration for cycling with validation."""
        config = self.agent_configs[self.current_agent_index]
        
        # Validate the phone number ID is a proper UUID
        if not self._is_valid_uuid(config["phone_number_id"]):
            logger.warning(f"Invalid phone number ID for {config['name']}: {config['phone_number_id']}")
            logger.warning("Falling back to Agent 1 configuration")
            config = self.agent_configs[0]  # Fallback to first agent
            
        # Cycle to next agent for next call
        self.current_agent_index = (self.current_agent_index + 1) % len(self.agent_configs)
        return config
        
    def set_agent_index(self, index: int) -> None:
        """Set the current agent index (used when loading from saved progress)."""
        self.current_agent_index = index % len(self.agent_configs)
        
    def get_current_agent_index(self) -> int:
        """Get the current agent index."""
        return self.current_agent_index
    
    def create_call(self, present_id: Optional[int] = None, custom_message: Optional[str] = None) -> Dict:
        """
        Create an outbound call using Vapi API with agent cycling for special presents.
        
        Args:
            present_id: Optional gift ID to include in metadata
            custom_message: Optional custom message for the call
            
        Returns:
            Dict with call response data including call_id if successful
        """

        try:
            # Get next agent configuration for cycling
            agent_config = self.get_next_agent_config()
            
            logger.info(f"Using agent configuration: {agent_config['name']} with phone {agent_config['phone_number']}")
            
            # Check if assistant ID is properly configured
            if not agent_config["assistant_id"]:
                return {
                    "success": False,
                    "error": "Assistant ID not configured",
                    "message": "Assistant ID is missing"
                }
            
            # Check if phone number is properly configured
            if not self.rafa_phone:
                return {
                    "success": False,
                    "error": "Phone number not configured", 
                    "message": "Phone number is missing"
                }
            
            # Prepare call payload with correct format
            call_data = {
                "assistantId": agent_config["assistant_id"],
                "phoneNumberId": agent_config["phone_number_id"],
                "customer": {
                    "number": self.rafa_phone
                },
                "metadata": {
                    "source": "disney_wish_oracle",
                    "birthday_call": True,
                    "timestamp": time.time(),
                    "agent_config": agent_config["name"],
                    "calling_from": agent_config["phone_number"]
                }
            }
            
            # Add present-specific metadata if provided
            if present_id:
                call_data["metadata"]["present_id"] = present_id
                call_data["metadata"]["gift_reveal"] = True
                call_data["metadata"]["is_special_gift"] = present_id % 5 == 0 if present_id else False
                
            if custom_message:
                call_data["metadata"]["custom_message"] = custom_message
            
            logger.info(f"Initiating Vapi call from {agent_config['phone_number']} to {self.rafa_phone} with metadata: {call_data['metadata']}")
            
            # Make the API call
            response = requests.post(
                f"{self.base_url}/call",
                headers=self.headers,
                json=call_data,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 201:  # Created
                call_id = response_data.get('id')
                logger.info(f"Vapi call created successfully. Call ID: {call_id}")
                return {
                    "success": True,
                    "call_id": call_id,
                    "status": "call_initiated",
                    "message": f"Birthday call initiated! Call ID: {call_id}",
                    "response": response_data
                }
            else:
                error_msg = response_data.get('message', f'HTTP {response.status_code}')
                logger.error(f"Vapi call failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                    "message": f"Failed to initiate call: {error_msg}"
                }
                
        except requests.exceptions.Timeout:
            error_msg = "Request timeout - Vapi API didn't respond in time"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "message": "Call initiation timed out. Please try again."
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(f"Vapi API network error: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "message": "Network error occurred. Please check your connection."
            }
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Vapi call unexpected error: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "message": "An unexpected error occurred. Please try again."
            }

# Create a global instance
vapi_client = VapiClient() 