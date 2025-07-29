"""
Disney Wish Oracle - Game Logic
Handles the core game mechanics including randomization, progress tracking, and character matching.
"""

import json
import os
import random
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Gift:
    """Represents a birthday gift with metadata."""
    id: int
    description: str
    themes: List[str]
    image_path: str
    revealed: bool = False
    revealed_at: Optional[str] = None
    revealed_by: Optional[str] = None

@dataclass
class Character:
    """Represents a Disney character with matching capabilities."""
    name: str
    image_path: str
    personality: str
    match_keywords: List[str]
    voice_style: str

@dataclass
class GameSession:
    """Represents the current game session state."""
    total_revealed: int = 0
    last_played: Optional[str] = None
    mode: str = "random"  # "random", "sequential"

class GameLogic:
    """Main game logic controller for the Disney Wish Oracle."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.gifts: List[Gift] = []
        self.characters: List[Character] = []
        self.session: GameSession = GameSession()
        self.progress_file = os.path.join(data_dir, "progress.json")
        
        # Agent cycling state
        self.current_agent_index = 0
        
        # Load game data
        self._load_gifts()
        self._load_characters()
        self._load_progress()
        
        # Initialize VAPI client with loaded agent index
        self._init_vapi_client()
        
        # Set up randomization
        random.seed()  # Use current time for randomization
    
    def _load_gifts(self) -> None:
        """Load gifts data from JSON file."""
        try:
            gifts_file = os.path.join(self.data_dir, "gifts.json")
            with open(gifts_file, 'r', encoding='utf-8') as f:
                gifts_data = json.load(f)
                
            self.gifts = [
                Gift(
                    id=gift['id'],
                    description=gift['description'],
                    themes=gift['themes'],
                    image_path=gift['image_path']
                )
                for gift in gifts_data
            ]
            logger.info(f"Loaded {len(self.gifts)} gifts")
            
        except Exception as e:
            logger.error(f"Error loading gifts: {e}")
            self.gifts = []
    
    def _load_characters(self) -> None:
        """Load Disney characters data from JSON file."""
        try:
            characters_file = os.path.join(self.data_dir, "characters.json")
            with open(characters_file, 'r', encoding='utf-8') as f:
                characters_data = json.load(f)
                
            self.characters = [
                Character(
                    name=char['name'],
                    image_path=char['image_path'],
                    personality=char['personality'],
                    match_keywords=char['match_keywords'],
                    voice_style=char['voice_style']
                )
                for char in characters_data
            ]
            logger.info(f"Loaded {len(self.characters)} characters")
            
        except Exception as e:
            logger.error(f"Error loading characters: {e}")
            self.characters = []
    
    def _load_progress(self) -> None:
        """Load saved game progress."""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                
                # Load session data
                self.session.total_revealed = progress_data.get('total_revealed', 0)
                self.session.last_played = progress_data.get('last_played')
                self.session.mode = progress_data.get('mode', 'random')
                
                # Load agent cycling state
                self.current_agent_index = progress_data.get('current_agent_index', 0)
                
                # Load revealed gifts
                revealed_gifts = progress_data.get('revealed_gifts', [])
                for gift_data in revealed_gifts:
                    gift = self.get_gift_by_id(gift_data['id'])
                    if gift:
                        gift.revealed = True
                        gift.revealed_at = gift_data.get('revealed_at')
                        gift.revealed_by = gift_data.get('revealed_by')

                logger.info(f"Loaded progress: {self.session.total_revealed}/30 gifts revealed, agent index: {self.current_agent_index}")
                
        except Exception as e:
            logger.error(f"Error loading progress: {e}")
            # Start fresh if progress file is corrupted
            self.session = GameSession()
            self.current_agent_index = 0
    
    def save_progress(self) -> None:
        """Save current game progress to file."""
        try:
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            
            revealed_gifts = [
                {
                    'id': gift.id,
                    'revealed_at': gift.revealed_at,
                    'revealed_by': gift.revealed_by
                }
                for gift in self.gifts if gift.revealed
            ]
            
            # Get current agent index from VAPI client
            try:
                from api_integration import vapi_client
                self.current_agent_index = vapi_client.get_current_agent_index()
            except ImportError:
                pass  # Keep current value if VAPI client not available
            
            progress_data = {
                'total_revealed': self.session.total_revealed,
                'last_played': datetime.now().isoformat(),
                'mode': self.session.mode,
                'current_agent_index': self.current_agent_index,
                'revealed_gifts': revealed_gifts
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2)
                
            logger.info(f"Progress saved successfully, agent index: {self.current_agent_index}")
            
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
    
    def get_available_gifts(self) -> List[Gift]:
        """Get list of unrevealed gifts."""
        return [gift for gift in self.gifts if not gift.revealed]
    
    def get_revealed_gifts(self) -> List[Gift]:
        """Get list of revealed gifts."""
        return [gift for gift in self.gifts if gift.revealed]
    
    def get_gift_by_id(self, gift_id: int) -> Optional[Gift]:
        """Get a gift by its ID."""
        for gift in self.gifts:
            if gift.id == gift_id:
                return gift
        return None
    
    def select_next_gift(self, mode: Optional[str] = None) -> Optional[Gift]:
        """Select the next gift to reveal based on the specified mode."""
        if mode is None:
            mode = self.session.mode
            
        available_gifts = self.get_available_gifts()
        
        if not available_gifts:
            return None  # All gifts revealed!
        
        if mode == "sequential":
            # Select the lowest ID available gift
            return min(available_gifts, key=lambda g: g.id)
        else:  # "random" mode (default)
            return random.choice(available_gifts)
    
    def find_best_character_match(self, gift: Gift) -> Character:
        """Find the best character match for a gift based on themes and keywords."""
        if not self.characters:
            # Fallback character if no characters loaded
            return Character(
                name="Mickey Mouse",
                image_path="assets/mickey.png",
                personality="Cheerful Disney icon",
                match_keywords=["disney", "magic"],
                voice_style="Upbeat and magical"
            )
        
        best_character = None
        best_score = 0
        
        # Calculate match scores for each character
        for character in self.characters:
            score = self._calculate_match_score(gift, character)
            if score > best_score:
                best_score = score
                best_character = character
        
        # If no good match found (score 0), use random character
        if best_character is None or best_score == 0:
            # Check for exact name matches first
            for character in self.characters:
                for theme in gift.themes:
                    if character.name.lower() in theme.lower() or theme.lower() in character.name.lower():
                        return character
            
            # Random fallback
            best_character = random.choice(self.characters)
        
        return best_character
    
    def _calculate_match_score(self, gift: Gift, character: Character) -> int:
        """Calculate how well a character matches a gift based on themes and keywords."""
        score = 0
        
        # Check for theme matches with character keywords
        for theme in gift.themes:
            theme_lower = theme.lower()
            for keyword in character.match_keywords:
                if keyword.lower() in theme_lower or theme_lower in keyword.lower():
                    score += 2  # Theme match is worth 2 points
        
        # Check for character name in gift description or themes
        char_name_lower = character.name.lower()
        gift_desc_lower = gift.description.lower()
        
        if char_name_lower in gift_desc_lower:
            score += 5  # Exact name match in description is worth 5 points
        
        for theme in gift.themes:
            if char_name_lower in theme.lower():
                score += 3  # Name match in theme is worth 3 points
        
        return score
    
    def reveal_gift(self, gift: Gift, character: Character) -> bool:
        """Mark a gift as revealed and update progress."""
        if gift.revealed:
            return False  # Already revealed
        
        try:
            gift.revealed = True
            gift.revealed_at = datetime.now().isoformat()
            gift.revealed_by = character.name
            
            self.session.total_revealed += 1
            
            self.save_progress()
            logger.info(f"Gift #{gift.id} revealed by {character.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error revealing gift: {e}")
            return False
    
    def get_game_summary(self) -> Dict:
        """Get overall game progress summary."""
        return {
            'total_gifts': len(self.gifts),
            'revealed_gifts': self.session.total_revealed,
            'remaining_gifts': len(self.gifts) - self.session.total_revealed,
            'completion_percentage': (self.session.total_revealed / len(self.gifts)) * 100 if self.gifts else 0,
            'is_complete': self.session.total_revealed >= len(self.gifts)
        }
    
    def reset_game(self) -> bool:
        """Reset the entire game progress."""
        try:
            # Reset all gifts
            for gift in self.gifts:
                gift.revealed = False
                gift.revealed_at = None
                gift.revealed_by = None
            
            # Reset session
            self.session = GameSession()
            
            # Remove progress file
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
            
            logger.info("Game reset successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting game: {e}")
            return False
    
    def find_character_by_name(self, name: str) -> Optional[Character]:
        """Find a character by name."""
        for character in self.characters:
            if character.name.lower() == name.lower():
                return character
        return None 

    def _init_vapi_client(self) -> None:
        """Initialize VAPI client with current agent index."""
        try:
            from api_integration import vapi_client
            vapi_client.set_agent_index(self.current_agent_index)
            logger.info(f"VAPI client initialized with agent index: {self.current_agent_index}")
        except ImportError:
            logger.warning("VAPI client not available") 