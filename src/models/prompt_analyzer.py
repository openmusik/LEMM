"""
Prompt Analyzer for extracting musical attributes from text
"""
from typing import Dict, Any
import re
from loguru import logger


class PromptAnalyzer:
    """Analyzes user prompts to extract musical attributes"""
    
    def __init__(self):
        """Initialize prompt analyzer"""
        self.genres = [
            'pop', 'rock', 'jazz', 'classical', 'electronic', 'hip-hop', 'rap',
            'country', 'blues', 'metal', 'folk', 'r&b', 'soul', 'funk', 'disco',
            'reggae', 'punk', 'indie', 'alternative', 'edm', 'house', 'techno',
            'ambient', 'lo-fi', 'trap', 'drill'
        ]
        
        self.moods = [
            'happy', 'sad', 'energetic', 'calm', 'aggressive', 'melancholic',
            'upbeat', 'dark', 'bright', 'mysterious', 'romantic', 'epic',
            'chill', 'intense', 'relaxing', 'dramatic', 'playful', 'serious'
        ]
        
        self.instruments = {
            'guitar': ['guitar', 'guitars'],
            'piano': ['piano', 'keyboard', 'keys'],
            'drums': ['drums', 'percussion'],
            'bass': ['bass'],
            'synth': ['synth', 'synthesizer', 'synths'],
            'violin': ['violin', 'strings'],
            'saxophone': ['sax', 'saxophone'],
            'trumpet': ['trumpet'],
            'vocal': ['vocal', 'vocals', 'voice', 'singing']
        }
    
    def analyze(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze prompt to extract musical attributes
        
        Args:
            prompt: User's text prompt
            
        Returns:
            Dictionary containing analyzed attributes
        """
        prompt_lower = prompt.lower()
        
        # Extract genre
        genre = self._extract_genre(prompt_lower)
        
        # Extract mood
        mood = self._extract_mood(prompt_lower)
        
        # Extract instruments
        instruments = self._extract_instruments(prompt_lower)
        
        # Extract tempo (BPM)
        tempo = self._extract_tempo(prompt_lower)
        
        # Extract key
        key = self._extract_key(prompt_lower)
        
        # Determine style
        style = self._determine_style(prompt_lower, genre)
        
        analysis = {
            'genre': genre,
            'style': style,
            'mood': mood,
            'tempo': tempo,
            'key': key,
            'instruments': instruments,
            'raw_prompt': prompt
        }
        
        logger.info(f"Prompt analysis complete: {analysis}")
        return analysis
    
    def _extract_genre(self, prompt: str) -> str:
        """Extract genre from prompt"""
        for genre in self.genres:
            if genre in prompt:
                return genre.title()
        return "Pop"  # Default
    
    def _extract_mood(self, prompt: str) -> str:
        """Extract mood from prompt"""
        for mood in self.moods:
            if mood in prompt:
                return mood.title()
        return "Neutral"  # Default
    
    def _extract_instruments(self, prompt: str) -> list:
        """Extract instruments from prompt"""
        found_instruments = []
        for instrument, keywords in self.instruments.items():
            for keyword in keywords:
                if keyword in prompt:
                    if instrument not in found_instruments:
                        found_instruments.append(instrument)
                    break
        
        if not found_instruments:
            return ["guitar", "drums", "bass"]  # Default band setup
        
        return found_instruments
    
    def _extract_tempo(self, prompt: str) -> int:
        """Extract tempo (BPM) from prompt"""
        # Look for explicit BPM mention
        bpm_match = re.search(r'(\d+)\s*bpm', prompt)
        if bpm_match:
            return int(bpm_match.group(1))
        
        # Infer from descriptors
        if any(word in prompt for word in ['fast', 'upbeat', 'energetic', 'quick']):
            return 140
        elif any(word in prompt for word in ['slow', 'calm', 'relaxing', 'chill']):
            return 80
        else:
            return 120  # Default medium tempo
    
    def _extract_key(self, prompt: str) -> str:
        """Extract musical key from prompt"""
        # Look for explicit key mention (e.g., "in C major", "A minor")
        key_pattern = r'\b([A-G]#?b?)\s*(major|minor)\b'
        key_match = re.search(key_pattern, prompt, re.IGNORECASE)
        
        if key_match:
            return f"{key_match.group(1)} {key_match.group(2).title()}"
        
        return "C Major"  # Default
    
    def _determine_style(self, prompt: str, genre: str) -> str:
        """Determine musical style based on prompt and genre"""
        if 'acoustic' in prompt:
            return "Acoustic"
        elif 'electronic' in prompt or 'edm' in prompt:
            return "Electronic"
        elif 'classical' in prompt or 'orchestral' in prompt:
            return "Classical/Orchestral"
        elif 'vintage' in prompt or 'retro' in prompt:
            return "Vintage/Retro"
        else:
            return f"Modern {genre}"
