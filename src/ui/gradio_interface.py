"""
Gradio UI for LEMM - Let Everyone Make Music
"""
import gradio as gr
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from loguru import logger

from src.__version__ import __version__
from src.models.prompt_analyzer import PromptAnalyzer
from src.models.lyrics_generator import LyricsGenerator
from src.models.music_generator import MusicGenerator
from src.audio.processor import AudioProcessor
from src.audio.mixer import AudioMixer
from src.utils.file_manager import FileManager


class LEMMInterface:
    """Main interface class for LEMM"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LEMM interface
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.prompt_analyzer = PromptAnalyzer()
        self.lyrics_generator = LyricsGenerator(config)
        self.music_generator = MusicGenerator(config)
        self.audio_processor = AudioProcessor(config)
        self.audio_mixer = AudioMixer(config)
        self.file_manager = FileManager(config)
        
        logger.info("LEMM Interface initialized")
    
    def analyze_prompt(self, prompt: str) -> str:
        """
        Analyze user prompt for musical attributes
        
        Args:
            prompt: User's text prompt
            
        Returns:
            Formatted analysis results
        """
        try:
            analysis = self.prompt_analyzer.analyze(prompt)
            return self._format_analysis(analysis)
        except Exception as e:
            logger.error(f"Error analyzing prompt: {e}")
            return f"Error: {str(e)}"
    
    def generate_lyrics(self, prompt: str, analysis: str) -> str:
        """
        Generate lyrics based on prompt
        
        Args:
            prompt: User's text prompt
            analysis: Analyzed prompt attributes
            
        Returns:
            Generated lyrics
        """
        try:
            lyrics = self.lyrics_generator.generate(prompt, analysis)
            return lyrics
        except Exception as e:
            logger.error(f"Error generating lyrics: {e}")
            return f"Error generating lyrics: {str(e)}"
    
    def generate_song(
        self,
        prompt: str,
        lyrics: str,
        num_clips: int,
        use_lora: bool,
        lora_path: Optional[str],
        temperature: float,
        progress=gr.Progress()
    ) -> Tuple[str, str]:
        """
        Generate complete song
        
        Args:
            prompt: User's text prompt
            lyrics: Lyrics (can be empty for instrumental)
            num_clips: Number of 32-second clips to generate
            use_lora: Whether to use LoRA weights
            lora_path: Path to LoRA weights
            temperature: Generation temperature
            progress: Gradio progress tracker
            
        Returns:
            Tuple of (audio_path, generation_info)
        """
        try:
            progress(0, desc="Analyzing prompt...")
            analysis = self.prompt_analyzer.analyze(prompt)
            
            # Generate clips
            clips = []
            for i in range(num_clips):
                progress((i + 1) / (num_clips + 2), desc=f"Generating clip {i+1}/{num_clips}...")
                
                clip = self.music_generator.generate_clip(
                    prompt=prompt,
                    lyrics=lyrics,
                    clip_index=i,
                    analysis=analysis,
                    previous_clip=clips[-1] if clips else None,
                    use_lora=use_lora,
                    lora_path=lora_path,
                    temperature=temperature
                )
                clips.append(clip)
            
            progress((num_clips + 1) / (num_clips + 2), desc="Processing and mixing...")
            
            # Process each clip (stem separation + enhancement)
            processed_clips = []
            for i, clip in enumerate(clips):
                processed = self.audio_processor.process_clip(clip, has_vocals=bool(lyrics))
                processed_clips.append(processed)
            
            progress((num_clips + 1.5) / (num_clips + 2), desc="Chaining clips...")
            
            # Mix and chain clips
            final_audio = self.audio_mixer.chain_clips(processed_clips)
            
            # Save final output
            output_path = self.file_manager.save_output(final_audio)
            
            progress(1.0, desc="Complete!")
            
            info = self._generate_info(analysis, num_clips, output_path)
            
            return output_path, info
            
        except Exception as e:
            logger.error(f"Error generating song: {e}")
            logger.exception("Full traceback:")
            return "", f"Error: {str(e)}"
    
    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results for display"""
        return f"""**Musical Analysis:**
- Genre: {analysis.get('genre', 'Unknown')}
- Style: {analysis.get('style', 'Unknown')}
- Tempo: {analysis.get('tempo', 'Unknown')} BPM
- Key: {analysis.get('key', 'Unknown')}
- Mood: {analysis.get('mood', 'Unknown')}
- Instruments: {', '.join(analysis.get('instruments', []))}
"""
    
    def _generate_info(self, analysis: Dict[str, Any], num_clips: int, output_path: str) -> str:
        """Generate generation info"""
        duration = num_clips * 32
        return f"""**Generation Complete!**

**Song Details:**
- Duration: {duration} seconds ({duration // 60}:{duration % 60:02d})
- Clips: {num_clips}
- Genre: {analysis.get('genre', 'Unknown')}
- Style: {analysis.get('style', 'Unknown')}

**Output:** `{output_path}`
"""


def create_interface(config: Dict[str, Any]) -> gr.Blocks:
    """
    Create Gradio interface for LEMM
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Gradio Blocks interface
    """
    lemm = LEMMInterface(config)
    
    with gr.Blocks(title="LEMM - Let Everyone Make Music", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("""
        # 🎵 LEMM - Let Everyone Make Music
        ### AI-Powered Music Generation
        
        Create complete songs from text prompts with advanced AI models.
        """)
        
        with gr.Tab("Generate Music"):
            with gr.Row():
                with gr.Column(scale=1):
                    prompt_input = gr.Textbox(
                        label="Prompt",
                        placeholder="Describe your song: genre, style, mood, instruments...\nExample: 'An upbeat pop song with electric guitars and synths, energetic and fun'",
                        lines=3
                    )
                    
                    with gr.Row():
                        analyze_btn = gr.Button("🔍 Analyze Prompt", size="sm")
                        auto_lyrics_btn = gr.Button("📝 Auto-Generate Lyrics", size="sm")
                    
                    analysis_output = gr.Markdown(label="Analysis")
                    
                    lyrics_input = gr.Textbox(
                        label="Lyrics (optional - leave empty for instrumental)",
                        placeholder="Enter or generate lyrics here...",
                        lines=8
                    )
                    
                    with gr.Accordion("⚙️ Settings", open=False):
                        num_clips = gr.Slider(
                            minimum=1,
                            maximum=config.get("generation", {}).get("max_clips", 10),
                            value=config.get("generation", {}).get("default_clips", 3),
                            step=1,
                            label="Number of Clips (32 seconds each)"
                        )
                        
                        temperature = gr.Slider(
                            minimum=0.1,
                            maximum=2.0,
                            value=config.get("generation", {}).get("temperature", 1.0),
                            step=0.1,
                            label="Temperature (creativity)"
                        )
                        
                        use_lora = gr.Checkbox(
                            label="Use LoRA Model",
                            value=False
                        )
                        
                        lora_path = gr.Textbox(
                            label="LoRA Model Path",
                            placeholder="Path to LoRA weights...",
                            visible=False
                        )
                    
                    generate_btn = gr.Button("🎵 Generate Song", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    info_output = gr.Markdown(label="Generation Info")
                    audio_output = gr.Audio(label="Generated Song", type="filepath")
                    
                    with gr.Row():
                        download_wav = gr.Button("⬇️ Download WAV")
                        download_mp3 = gr.Button("⬇️ Download MP3")
        
        with gr.Tab("Training (LoRA)"):
            gr.Markdown("""
            ### LoRA Training
            Fine-tune the model on your own music to create custom styles.
            """)
            
            with gr.Row():
                with gr.Column():
                    training_data = gr.File(
                        label="Training Audio Files",
                        file_count="multiple",
                        file_types=["audio"]
                    )
                    
                    training_steps = gr.Slider(
                        minimum=100,
                        maximum=10000,
                        value=1000,
                        step=100,
                        label="Training Steps"
                    )
                    
                    learning_rate = gr.Number(
                        value=1e-4,
                        label="Learning Rate"
                    )
                    
                    train_btn = gr.Button("🚀 Start Training", variant="primary")
                
                with gr.Column():
                    training_output = gr.Textbox(
                        label="Training Log",
                        lines=20,
                        interactive=False
                    )
        
        with gr.Tab("About"):
            gr.Markdown("""
            ### About LEMM
            
            **LEMM (Let Everyone Make Music)** is an advanced AI-powered music generation system that combines multiple state-of-the-art models:
            
            - 🎼 **ACE-Step**: High-quality music generation
            - 📝 **SongComposer**: Intelligent lyrics generation
            - 🎛️ **MusicControlNet**: Seamless clip conditioning
            - 🎚️ **Demucs**: Professional stem separation
            - 🎤 **so-vits-svc**: Vocal enhancement
            - 🎸 **Pedalboard**: Audio effects processing
            
            #### How It Works:
            1. Describe your song in natural language
            2. Optionally generate or provide lyrics
            3. Choose number of clips (each is 32 seconds)
            4. Let AI generate, enhance, and mix your song
            
            #### Technical Details:
            - Each clip: 2s lead-in + 28s main + 2s lead-out
            - Clips are seamlessly chained with crossfading
            - Stems are separated and individually enhanced
            - LoRA training for custom styles
            
            **Version:** """ + __version__ + """
            """)
        
        # Event handlers
        analyze_btn.click(
            fn=lemm.analyze_prompt,
            inputs=[prompt_input],
            outputs=[analysis_output]
        )
        
        auto_lyrics_btn.click(
            fn=lemm.generate_lyrics,
            inputs=[prompt_input, analysis_output],
            outputs=[lyrics_input]
        )
        
        use_lora.change(
            fn=lambda x: gr.update(visible=x),
            inputs=[use_lora],
            outputs=[lora_path]
        )
        
        generate_btn.click(
            fn=lemm.generate_song,
            inputs=[
                prompt_input,
                lyrics_input,
                num_clips,
                use_lora,
                lora_path,
                temperature
            ],
            outputs=[audio_output, info_output]
        )
    
    return interface
