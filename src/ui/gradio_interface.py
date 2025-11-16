"""
Gradio UI for LEMM - Let Everyone Make Music
"""
import gradio as gr
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
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
        
        # Check system capabilities
        self._check_system_compatibility()
        
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
    
    def _check_system_compatibility(self) -> None:
        """Check system compatibility and log warnings"""
        import torch
        import platform
        
        if not torch.cuda.is_available():
            logger.warning("⚠️ CUDA not available - ACE-Step music generation may fail")
            if platform.system() == "Windows":
                try:
                    import subprocess
                    result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                          capture_output=True, text=True, timeout=5)
                    if "Radeon" in result.stdout or "AMD" in result.stdout:
                        logger.warning("⚠️ AMD GPU detected - ACE-Step requires NVIDIA GPU")
                        logger.info("💡 Consider using HuggingFace Space deployment for music generation")
                except Exception:
                    pass
    
    def get_system_status(self) -> str:
        """Get system compatibility status for UI display"""
        import torch
        import platform
        
        status_lines = [f"LEMM v{__version__} - System Status"]
        
        # Check GPU availability
        if torch.cuda.is_available():
            status_lines.append(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        else:
            status_lines.append("❌ GPU: No CUDA available (CPU only)")
            
        # Check for AMD GPU
        amd_detected = False
        if platform.system() == "Windows":
            try:
                import subprocess
                result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                      capture_output=True, text=True, timeout=5)
                if "Radeon" in result.stdout or "AMD" in result.stdout:
                    amd_detected = True
                    status_lines.append("⚠️ AMD GPU detected")
            except Exception:
                pass
        
        # Model availability
        status_lines.append("\n**Available Models:**")
        
        # Check ACE-Step availability
        if self.music_generator.ace_step_available:
            if torch.cuda.is_available() and not amd_detected:
                status_lines.append("✅ ACE-Step: Ready (GPU accelerated)")
            else:
                status_lines.append("⚠️ ACE-Step: Available but may have issues on this hardware")
        else:
            status_lines.append("❌ ACE-Step: Not available")
            
        # Check MusicGen availability
        if self.music_generator.musicgen_available:
            status_lines.append("✅ MusicGen: Ready (CPU compatible)")
        else:
            status_lines.append("❌ MusicGen: Not available")
            
        # Recommended model
        selected_model = self.music_generator.selected_model
        if selected_model == "ace_step":
            status_lines.append(f"\n**Auto-Selected:** ACE-Step (for high-quality GPU generation)")
        elif selected_model == "musicgen":
            status_lines.append(f"\n**Auto-Selected:** MusicGen (for reliable CPU generation)")
        else:
            status_lines.append(f"\n**Auto-Selected:** {selected_model}")
        
        return "\n".join(status_lines)
    
    def generate_lyrics(self, prompt: str, analysis_str: str, random_seed: Optional[int] = None) -> str:
        """
        Generate lyrics based on prompt and analysis
        
        Args:
            prompt: User's text prompt
            analysis_str: Formatted analysis string
            random_seed: Random seed for variation (None = new random seed)
            
        Returns:
            Generated lyrics
        """
        try:
            # Parse analysis back to dict
            analysis_dict = self.prompt_analyzer.analyze(prompt)
            
            # Generate with optional random seed
            lyrics = self.lyrics_generator.generate(prompt, analysis_dict, random_seed)
            return lyrics
        except Exception as e:
            logger.error(f"Error generating lyrics: {e}")
            return f"Error generating lyrics: {str(e)}"
    
    def randomize_lyrics(self, prompt: str, analysis_str: Optional[str] = None) -> str:
        """
        Generate completely new random lyrics based on prompt analysis
        
        Args:
            prompt: User's text prompt
            analysis_str: Formatted analysis string (not used, re-analyzed from prompt)
            
        Returns:
            New randomized lyrics with completely different content
        """
        import random
        
        # Re-analyze the prompt to get fresh analysis
        analysis = self.prompt_analyzer.analyze(prompt)
        
        # Generate new random seed for variation
        new_seed = random.randint(0, 999999)
        logger.info(f"Randomizing lyrics with new seed: {new_seed} and fresh analysis")
        
        # Generate lyrics with new seed and analysis
        return self.lyrics_generator.generate(prompt, analysis, random_seed=new_seed)
    
    def estimate_generation_time(
        self,
        num_clips: int,
        lyrics: str,
        model_choice: str
    ) -> str:
        """
        Estimate total generation time
        
        Args:
            num_clips: Number of clips to generate
            lyrics: Lyrics (empty = instrumental)
            model_choice: Selected model
            
        Returns:
            Formatted time estimate string
        """
        import torch
        
        # Determine which model will be used
        if model_choice == "Auto (Recommended)":
            model = self.music_generator.selected_model
        elif model_choice == "ACE-Step (GPU)":
            model = "ace_step"
        else:
            model = "musicgen"
        
        # Base generation time per clip (in seconds)
        if model == "ace_step":
            # ACE-Step is fast on GPU
            if torch.cuda.is_available():
                time_per_clip = 30  # ~30s per 32s clip on GPU
            else:
                time_per_clip = 600  # ~10 minutes per clip on CPU (slow!)
        else:  # MusicGen
            # MusicGen is CPU-friendly
            if torch.cuda.is_available():
                time_per_clip = 20  # ~20s per clip on GPU
            else:
                time_per_clip = 180  # ~3 minutes per clip on CPU
        
        # Additional processing time
        stem_separation_time = 15 * num_clips  # ~15s per clip
        vocal_synthesis_time = 0
        if lyrics and lyrics.strip():
            # Estimate vocal synthesis time (rough: 0.1s per character on CPU)
            vocal_synthesis_time = len(lyrics) * 0.1
        mixing_time = 10  # Final mixing
        
        # Total estimate
        total_seconds = (
            time_per_clip * num_clips +
            stem_separation_time +
            vocal_synthesis_time +
            mixing_time
        )
        
        # Format as human-readable time
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        
        estimate_text = f"⏱️ **Estimated Time:** {minutes}m {seconds}s\n\n"
        estimate_text += f"**Breakdown:**\n"
        estimate_text += f"- Music generation: ~{int(time_per_clip * num_clips // 60)}m {int(time_per_clip * num_clips % 60)}s ({num_clips} clips × {time_per_clip}s)\n"
        estimate_text += f"- Stem separation: ~{stem_separation_time}s\n"
        if vocal_synthesis_time > 0:
            estimate_text += f"- Vocal synthesis: ~{int(vocal_synthesis_time)}s\n"
        estimate_text += f"- Mixing: ~{mixing_time}s\n\n"
        
        # Hardware info
        if torch.cuda.is_available():
            estimate_text += f"💡 Using GPU acceleration (faster)\n"
        else:
            estimate_text += f"⚠️ CPU-only mode (slower - consider using GPU)\n"
        
        return estimate_text
    
    def generate_song(
        self,
        prompt: str,
        lyrics: str,
        num_clips: int,
        model_choice: str,
        use_lora: bool,
        lora_path: Optional[str],
        temperature: float,
        inference_steps: int,
        guidance_scale: float,
        random_seed: int,
        progress=gr.Progress()
    ) -> Tuple[Optional[str], str]:
        """
        Generate complete song
        
        Args:
            prompt: User's text prompt
            lyrics: Lyrics (can be empty for instrumental)
            num_clips: Number of 32-second clips to generate
            model_choice: Selected model
            use_lora: Whether to use LoRA weights
            lora_path: Path to LoRA weights
            temperature: Generation temperature
            inference_steps: Number of inference steps (ACE-Step)
            guidance_scale: Guidance scale (ACE-Step)
            random_seed: Random seed for reproducibility (-1 for random)
            progress: Gradio progress tracker
            
        Returns:
            Tuple of (audio_path, generation_info)
        """
        try:
            progress(0, desc="Analyzing prompt...")
            analysis = self.prompt_analyzer.analyze(prompt)
            
            # Update music generator settings
            if inference_steps > 0:
                self.music_generator.num_inference_steps = inference_steps
            if guidance_scale > 0:
                self.music_generator.guidance_scale = guidance_scale
            
            # Handle model selection
            if model_choice == "Auto (Recommended)":
                # Use current auto-selected model
                logger.info(f"Using auto-selected model: {self.music_generator.selected_model}")
            elif model_choice == "ACE-Step (GPU)":
                # Force ACE-Step selection if available
                if self.music_generator.ace_step_available:
                    self.music_generator.selected_model = "ace_step"
                    self.music_generator.active_model_type = "ace_step"
                    logger.info("User forced ACE-Step model selection")
                else:
                    return None, "❌ ACE-Step not available on this system"
            elif model_choice == "MusicGen (CPU)":  
                # Force MusicGen selection if available
                if self.music_generator.musicgen_available:
                    self.music_generator.selected_model = "musicgen"
                    self.music_generator.active_model_type = "musicgen"
                    logger.info("User forced MusicGen model selection")
                else:
                    return None, "❌ MusicGen not available on this system"
            
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
                
                # Validate clip is not silent
                clip_max = np.abs(clip).max()
                clip_rms = np.sqrt(np.mean(clip**2))
                logger.info(f"Clip {i+1} generated - peak: {clip_max:.4f}, RMS: {clip_rms:.4f}")
                
                if clip_max < 1e-6:
                    error_msg = f"❌ Clip {i+1} is silent! Generation failed."
                    logger.error(error_msg)
                    return None, error_msg
                
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
            try:
                output_path = self.file_manager.save_output(final_audio)
                logger.info(f"💾 Received output path from file_manager: {output_path}")
                logger.info(f"   Type: {type(output_path)}")
                logger.info(f"   Is file: {Path(output_path).is_file() if output_path else 'N/A'}")
            except Exception as save_error:
                logger.error(f"❌ Failed to save audio: {save_error}")
                logger.exception("Save error traceback:")
                return None, f"❌ Error saving audio: {save_error}"
            
            # Verify the output path is valid
            if not output_path:
                logger.error("Output path is None or empty")
                return None, f"❌ Error: No output path returned"
            
            if not isinstance(output_path, str):
                logger.error(f"Output path is not a string: {type(output_path)}")
                return None, f"❌ Error: Invalid output path type"
            
            output_path_obj = Path(output_path)
            if not output_path_obj.exists():
                logger.error(f"Output path does not exist: {output_path}")
                return None, f"❌ Error: Output file not found"
            
            if not output_path_obj.is_file():
                logger.error(f"Output path is not a file: {output_path}")
                logger.error(f"   Is directory: {output_path_obj.is_dir()}")
                return None, f"❌ Error: Output path is not a valid file"
            
            progress(1.0, desc="Complete!")
            
            info = self._generate_info(analysis, num_clips, output_path)
            
            return output_path, info
            
        except Exception as e:
            logger.error(f"Error generating song: {e}")
            logger.exception("Full traceback:")
            
            # Return None for audio (Gradio will handle it) and error message
            error_msg = f"❌ Generation Error: {str(e)}"
            
            # Add helpful hints for common errors
            error_str = str(e).lower()
            if "musicgen" in error_str or "audiocraft" in error_str:
                error_msg += "\n\n💡 MusicGen requires audiocraft to be installed."
                error_msg += "\nInstall with: pip install audiocraft"
            elif "permission" in error_str:
                error_msg += "\n\n💡 Permission error - check file/directory permissions"
            elif "ace" in error_str or "ace-step" in error_str:
                error_msg += "\n\n💡 ACE-Step may not work on CPU/AMD systems"
                error_msg += "\nTry selecting 'MusicGen (CPU)' instead"
            
            return None, error_msg
    
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
    
    with gr.Blocks(title="LEMM - Let Everyone Make Music", theme="soft") as interface:
        
        gr.Markdown("""
        # 🎵 LEMM - Let Everyone Make Music
        ### AI-Powered Music Generation
        
        Create complete songs from text prompts with advanced AI models.
        """)
        
        # System status
        system_status = gr.Markdown(lemm.get_system_status(), elem_classes=["system-status"])
        
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
                        randomize_lyrics_btn = gr.Button("🎲 Randomize Lyrics", size="sm", variant="secondary")
                    
                    analysis_output = gr.Markdown(label="Analysis")
                    
                    lyrics_input = gr.Textbox(
                        label="Lyrics (optional - leave empty for instrumental)",
                        placeholder="Enter or generate lyrics here...",
                        lines=8
                    )
                    
                    # Model Selection - visible by default for easy testing
                    model_choice = gr.Radio(
                        choices=["Auto (Recommended)", "ACE-Step (GPU)", "MusicGen (CPU)"],
                        value="Auto (Recommended)",
                        label="🤖 AI Model",
                        info="Auto selects best model based on your hardware"
                    )
                    
                    with gr.Accordion("⚙️ Advanced Settings", open=False):
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
                        
                        # ACE-Step specific settings
                        with gr.Group(visible=True) as ace_settings:
                            gr.Markdown("**ACE-Step Settings**")
                            inference_steps = gr.Slider(
                                minimum=10,
                                maximum=50,
                                value=config.get("models", {}).get("ace_step", {}).get("num_inference_steps", 27),
                                step=1,
                                label="Inference Steps (quality vs speed)",
                                info="More steps = better quality but slower"
                            )
                            guidance_scale = gr.Slider(
                                minimum=1.0,
                                maximum=15.0,
                                value=config.get("models", {}).get("ace_step", {}).get("guidance_scale", 7.5),
                                step=0.5,
                                label="Guidance Scale (prompt adherence)",
                                info="Higher values follow prompt more closely"
                            )
                        
                        # MusicGen specific settings
                        with gr.Group(visible=False) as musicgen_settings:
                            gr.Markdown("**MusicGen Settings**")
                            musicgen_duration = gr.Slider(
                                minimum=5,
                                maximum=30,
                                value=30,
                                step=5,
                                label="Generation Duration (seconds)",
                                info="Longer = more coherent but slower"
                            )
                            musicgen_top_k = gr.Slider(
                                minimum=0,
                                maximum=250,
                                value=250,
                                step=10,
                                label="Top-K Sampling",
                                info="Lower = more focused, higher = more diverse"
                            )
                        
                        # Common settings
                        use_lora = gr.Checkbox(
                            label="Use LoRA Model",
                            value=False
                        )
                        
                        lora_path = gr.Textbox(
                            label="LoRA Model Path",
                            placeholder="Path to LoRA weights...",
                            visible=False
                        )
                        
                        random_seed = gr.Number(
                            label="Random Seed (optional, for reproducibility)",
                            value=-1,
                            precision=0,
                            info="Use -1 for random, or set a specific number for reproducible results"
                        )
                    
                    generate_btn = gr.Button("🎵 Generate Song", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    info_output = gr.Markdown(label="Generation Info")
                    time_estimate = gr.Markdown(
                        label="Time Estimate",
                        value="⏱️ Adjust settings to see estimated generation time"
                    )
                    audio_output = gr.Audio(
                        label="Generated Song",
                        type="filepath",
                        format="wav",
                        autoplay=False
                    )
                    
                    with gr.Row():
                        download_wav = gr.Button("⬇️ Download WAV")
                        download_mp3 = gr.Button("⬇️ Download MP3")
        
        with gr.Tab("Training"):
            gr.Markdown("""
            ## Model Training & Fine-Tuning
            Train custom models on your own data to create unique styles and voices.
            """)
            
            with gr.Tabs():
                # ACE-Step LoRA Training
                with gr.Tab("ACE-Step (LoRA)"):
                    gr.Markdown("""
                    ### ACE-Step LoRA Fine-Tuning
                    Fine-tune ACE-Step on your music to create custom musical styles.
                    **Use case**: Genre-specific generation, artist style emulation
                    """)
                    
                    with gr.Row():
                        with gr.Column():
                            ace_training_data = gr.File(
                                label="Training Audio Files (WAV/MP3)",
                                file_count="multiple",
                                file_types=["audio"]
                            )
                            
                            ace_training_steps = gr.Slider(
                                minimum=100,
                                maximum=10000,
                                value=1000,
                                step=100,
                                label="Training Steps"
                            )
                            
                            ace_learning_rate = gr.Number(
                                value=1e-4,
                                label="Learning Rate"
                            )
                            
                            ace_lora_rank = gr.Slider(
                                minimum=4,
                                maximum=128,
                                value=32,
                                step=4,
                                label="LoRA Rank (higher = more parameters)"
                            )
                            
                            ace_batch_size = gr.Slider(
                                minimum=1,
                                maximum=16,
                                value=4,
                                step=1,
                                label="Batch Size"
                            )
                            
                            ace_train_btn = gr.Button("🚀 Start ACE-Step Training", variant="primary")
                        
                        with gr.Column():
                            ace_training_output = gr.Textbox(
                                label="Training Log",
                                lines=20,
                                interactive=False
                            )
                
                # MusicGen Fine-Tuning
                with gr.Tab("MusicGen"):
                    gr.Markdown("""
                    ### MusicGen Fine-Tuning
                    Fine-tune MusicGen on your audio dataset for custom instrumental generation.
                    **Use case**: CPU-compatible music generation, specific genre training
                    """)
                    
                    with gr.Row():
                        with gr.Column():
                            mg_training_data = gr.File(
                                label="Training Audio Files (WAV/MP3)",
                                file_count="multiple",
                                file_types=["audio"]
                            )
                            
                            mg_training_steps = gr.Slider(
                                minimum=500,
                                maximum=20000,
                                value=5000,
                                step=500,
                                label="Training Steps"
                            )
                            
                            mg_learning_rate = gr.Number(
                                value=5e-5,
                                label="Learning Rate"
                            )
                            
                            mg_warmup_steps = gr.Slider(
                                minimum=0,
                                maximum=1000,
                                value=100,
                                step=10,
                                label="Warmup Steps"
                            )
                            
                            mg_train_btn = gr.Button("🚀 Start MusicGen Training", variant="primary")
                        
                        with gr.Column():
                            mg_training_output = gr.Textbox(
                                label="Training Log",
                                lines=20,
                                interactive=False
                            )
                
                # SongComposer/Lyrics Training
                with gr.Tab("Lyrics Model"):
                    gr.Markdown("""
                    ### SongComposer Lyrics Fine-Tuning
                    Train the lyrics generation model on your song lyrics dataset.
                    **Use case**: Genre-specific lyrics, custom writing style
                    """)
                    
                    with gr.Row():
                        with gr.Column():
                            lyrics_training_data = gr.File(
                                label="Lyrics Text Files (.txt)",
                                file_count="multiple",
                                file_types=[".txt"]
                            )
                            
                            lyrics_training_steps = gr.Slider(
                                minimum=500,
                                maximum=15000,
                                value=3000,
                                step=500,
                                label="Training Steps"
                            )
                            
                            lyrics_learning_rate = gr.Number(
                                value=2e-5,
                                label="Learning Rate"
                            )
                            
                            lyrics_genre = gr.Dropdown(
                                choices=["Pop", "Rock", "Hip-Hop", "Country", "R&B", "Electronic", "Folk", "Jazz", "Other"],
                                value="Pop",
                                label="Target Genre (optional)"
                            )
                            
                            lyrics_train_btn = gr.Button("🚀 Start Lyrics Training", variant="primary")
                        
                        with gr.Column():
                            lyrics_training_output = gr.Textbox(
                                label="Training Log",
                                lines=20,
                                interactive=False
                            )
                
                # Vocal Synthesizer Training
                with gr.Tab("Voice Clone"):
                    gr.Markdown("""
                    ### Vocal Synthesizer Voice Training
                    Train a custom voice model for vocal synthesis (used with MusicGen).
                    **Use case**: Custom singer voice, specific vocal style
                    """)
                    
                    with gr.Row():
                        with gr.Column():
                            voice_training_data = gr.File(
                                label="Voice Audio Files (WAV, clean vocals)",
                                file_count="multiple",
                                file_types=["audio"]
                            )
                            
                            voice_speaker_name = gr.Textbox(
                                label="Voice Name",
                                placeholder="e.g., 'MySinger'"
                            )
                            
                            voice_training_hours = gr.Slider(
                                minimum=0.5,
                                maximum=10,
                                value=2,
                                step=0.5,
                                label="Estimated Training Hours"
                            )
                            
                            voice_quality = gr.Radio(
                                choices=["Fast (Lower Quality)", "Balanced", "Best (Slower)"],
                                value="Balanced",
                                label="Training Quality"
                            )
                            
                            voice_train_btn = gr.Button("🚀 Start Voice Training", variant="primary")
                        
                        with gr.Column():
                            voice_training_output = gr.Textbox(
                                label="Training Log",
                                lines=20,
                                interactive=False
                            )
                            
                            voice_preview = gr.Audio(
                                label="Voice Preview",
                                type="filepath"
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
        
        randomize_lyrics_btn.click(
            fn=lemm.randomize_lyrics,
            inputs=[prompt_input, analysis_output],
            outputs=[lyrics_input]
        )
        
        use_lora.change(
            fn=lambda x: gr.update(visible=x),
            inputs=[use_lora],
            outputs=[lora_path]
        )
        
        # Toggle model-specific settings based on model choice
        def update_model_settings(model_choice):
            """Show/hide model-specific settings based on selection"""
            if model_choice == "ACE-Step (GPU)":
                return gr.update(visible=True), gr.update(visible=False)
            elif model_choice == "MusicGen (CPU)":
                return gr.update(visible=False), gr.update(visible=True)
            else:  # Auto
                # Show both with indication that auto will choose
                return gr.update(visible=True), gr.update(visible=True)
        
        model_choice.change(
            fn=update_model_settings,
            inputs=[model_choice],
            outputs=[ace_settings, musicgen_settings]
        )
        
        # Update time estimate when settings change
        def update_time_estimate(num_clips, lyrics, model_choice):
            estimate = lemm.estimate_generation_time(num_clips, lyrics, model_choice)
            return estimate  # Return string directly for HF Space compatibility
        
        # Update estimate when any relevant input changes
        for component in [num_clips, lyrics_input, model_choice]:
            component.change(
                fn=update_time_estimate,
                inputs=[num_clips, lyrics_input, model_choice],
                outputs=[time_estimate]
            )
        
        generate_btn.click(
            fn=lemm.generate_song,
            inputs=[
                prompt_input,
                lyrics_input,
                num_clips,
                model_choice,
                use_lora,
                lora_path,
                temperature,
                inference_steps,
                guidance_scale,
                random_seed
            ],
            outputs=[audio_output, info_output]
        )
    
    return interface
