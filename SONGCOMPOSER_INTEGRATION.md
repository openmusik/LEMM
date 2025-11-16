# SongComposer Integration Plan

## Current Status
The lyrics generator is currently using a **placeholder implementation** that generates thematic lyrics based on genre and mood analysis. This works for testing but should be replaced with the actual SongComposer model.

## SongComposer Repository
- **GitHub**: https://github.com/pjlab-songcomposer/songcomposer
- **Paper**: SongComposer: A Large Language Model for Lyric and Melody Composition in Song Generation

## Integration Steps

### 1. Install SongComposer
```bash
git clone https://github.com/pjlab-songcomposer/songcomposer.git
cd songcomposer
pip install -r requirements.txt
```

### 2. Download Models
SongComposer requires:
- Language model for lyrics generation
- Melody generation model (optional for LEMM since we use ACE-Step)

```bash
# Download from Hugging Face
# Check repository for specific model paths
```

### 3. Update LyricsGenerator Class

**File**: `src/models/lyrics_generator.py`

Replace the placeholder implementation with actual SongComposer integration:

```python
from songcomposer import SongComposerModel  # Import actual model

class LyricsGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_path = config.get("models", {}).get("songcomposer", {}).get("path")
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load SongComposer model"""
        try:
            logger.info(f"Loading SongComposer from {self.model_path}")
            self.model = SongComposerModel.from_pretrained(self.model_path)
            logger.info("SongComposer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load SongComposer: {e}")
            logger.warning("Falling back to placeholder lyrics generation")
            self.model = None
    
    def generate(self, prompt: str, analysis: Optional[Dict[str, Any]] = None, 
                 random_seed: Optional[int] = None) -> str:
        """Generate lyrics using SongComposer"""
        if self.model is None:
            # Fallback to placeholder
            return self._generate_placeholder_lyrics(prompt, analysis)
        
        try:
            # Build SongComposer prompt from analysis
            composer_prompt = self._build_songcomposer_prompt(prompt, analysis)
            
            # Generate lyrics
            lyrics = self.model.generate_lyrics(
                prompt=composer_prompt,
                max_length=500,
                temperature=0.8,
                top_p=0.9,
                random_seed=random_seed
            )
            
            return lyrics
            
        except Exception as e:
            logger.error(f"SongComposer generation failed: {e}")
            return self._generate_placeholder_lyrics(prompt, analysis)
    
    def _build_songcomposer_prompt(self, prompt: str, analysis: Dict[str, Any]) -> str:
        """Build prompt for SongComposer from LEMM analysis"""
        genre = analysis.get('genre', 'Pop')
        mood = analysis.get('mood', 'Neutral')
        style = analysis.get('style', 'Modern')
        
        # Format for SongComposer expectations
        composer_prompt = f"Genre: {genre}\\nMood: {mood}\\nStyle: {style}\\n\\n{prompt}"
        return composer_prompt
```

### 4. Update Configuration

**File**: `config/config.yaml`

Add SongComposer configuration:

```yaml
models:
  songcomposer:
    path: "models/songcomposer"  # Path to downloaded model
    device: "cuda"  # or "cpu"
    max_length: 500
    temperature: 0.8
    top_p: 0.9
```

### 5. Update Requirements

Add SongComposer dependencies to `requirements.txt`:

```txt
# SongComposer (when available)
# git+https://github.com/pjlab-songcomposer/songcomposer.git
# transformers>=4.30.0
# torch>=2.0.0
```

## Benefits of SongComposer Integration

1. **Coherent Lyrics**: Generates lyrics that actually make sense and follow song structure
2. **Genre-Appropriate**: Creates lyrics matching the musical style
3. **Rhyme Schemes**: Proper rhyming and meter
4. **Song Structure**: Verses, chorus, bridge, etc.
5. **Emotional Consistency**: Lyrics match the intended mood

## Fallback Behavior

The current placeholder implementation will remain as a fallback:
- If SongComposer fails to load → use placeholder
- If SongComposer generation fails → use placeholder
- This ensures LEMM continues to work even without SongComposer

## Testing Checklist

After integration:
- [ ] Test lyrics generation without errors
- [ ] Verify lyrics quality and coherence
- [ ] Check lyrics match genre/mood from analysis
- [ ] Test fallback to placeholder if SongComposer unavailable
- [ ] Verify integration works on both CPU and GPU
- [ ] Test on HuggingFace Space deployment

## Notes

- SongComposer may have specific prompt format requirements - check documentation
- May need to adapt output format to match LEMM's expected structure
- Consider memory requirements when deploying to HuggingFace Spaces
- SongComposer might generate melody info - we can ignore this since ACE-Step handles music
