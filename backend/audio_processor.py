"""
Audio transcription module for earnings calls
Supports multiple transcription backends: Whisper (local), OpenAI Whisper API
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

# Try importing optional dependencies
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class AudioTranscriber:
    """Handle audio transcription with multiple backends"""
    
    def __init__(self, backend: str = "whisper-local"):
        """
        Initialize transcriber
        
        Args:
            backend: "whisper-local", "whisper-api", or "auto"
        """
        self.backend = backend
        
        if backend == "whisper-local" and not WHISPER_AVAILABLE:
            raise ImportError("Whisper not installed. Run: pip install openai-whisper")
        
        if backend == "whisper-api" and not OPENAI_AVAILABLE:
            raise ImportError("OpenAI not installed. Run: pip install openai")
        
        if backend == "auto":
            if WHISPER_AVAILABLE:
                self.backend = "whisper-local"
            elif OPENAI_AVAILABLE:
                self.backend = "whisper-api"
            else:
                raise ImportError("No transcription backend available")
    
    def transcribe(
        self,
        audio_path: str,
        language: str = "en",
        model_size: str = "base"
    ) -> Dict:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., "en")
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            
        Returns:
            Dictionary with transcription results
        """
        if self.backend == "whisper-local":
            return self._transcribe_local(audio_path, language, model_size)
        elif self.backend == "whisper-api":
            return self._transcribe_api(audio_path, language)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
    
    def _transcribe_local(
        self,
        audio_path: str,
        language: str,
        model_size: str
    ) -> Dict:
        """Transcribe using local Whisper model"""
        print(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        
        print(f"Transcribing audio: {audio_path}")
        result = model.transcribe(
            audio_path,
            language=language,
            verbose=False
        )
        
        # Format result
        return {
            "text": result["text"],
            "language": result.get("language", language),
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"],
                    "speaker": None  # Whisper doesn't do speaker diarization
                }
                for seg in result.get("segments", [])
            ],
            "backend": "whisper-local",
            "model": model_size
        }
    
    def _transcribe_api(
        self,
        audio_path: str,
        language: str
    ) -> Dict:
        """Transcribe using OpenAI Whisper API"""
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        print(f"Transcribing audio via OpenAI API: {audio_path}")
        
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json"
            )
        
        # Format result
        return {
            "text": transcript.text,
            "language": transcript.language,
            "segments": [
                {
                    "start": seg.get("start", 0),
                    "end": seg.get("end", 0),
                    "text": seg.get("text", ""),
                    "speaker": None
                }
                for seg in getattr(transcript, "segments", [])
            ],
            "backend": "whisper-api",
            "model": "whisper-1"
        }


def detect_speakers_simple(segments: List[Dict]) -> List[Dict]:
    """
    Simple speaker detection based on pauses
    This is a basic heuristic - for better results, use pyannote.audio
    
    Args:
        segments: List of transcription segments
        
    Returns:
        Segments with speaker labels
    """
    if not segments:
        return segments
    
    speaker_id = 1
    last_end = 0
    
    for segment in segments:
        # If there's a long pause (>2 seconds), assume speaker change
        if segment["start"] - last_end > 2.0:
            speaker_id += 1
        
        segment["speaker"] = f"Speaker {speaker_id}"
        last_end = segment["end"]
    
    return segments


def format_transcript_with_speakers(segments: List[Dict]) -> str:
    """
    Format transcript with speaker labels and timestamps
    
    Args:
        segments: List of segments with speaker info
        
    Returns:
        Formatted transcript text
    """
    lines = []
    current_speaker = None
    current_text = []
    
    for segment in segments:
        speaker = segment.get("speaker", "Unknown")
        
        if speaker != current_speaker:
            # New speaker - output previous speaker's text
            if current_speaker and current_text:
                lines.append(f"\n{current_speaker}:")
                lines.append(" ".join(current_text))
            
            current_speaker = speaker
            current_text = [segment["text"].strip()]
        else:
            current_text.append(segment["text"].strip())
    
    # Output last speaker's text
    if current_speaker and current_text:
        lines.append(f"\n{current_speaker}:")
        lines.append(" ".join(current_text))
    
    return "\n".join(lines)


def convert_audio_format(
    input_path: str,
    output_path: Optional[str] = None,
    target_format: str = "wav"
) -> str:
    """
    Convert audio to a format suitable for transcription
    
    Args:
        input_path: Path to input audio file
        output_path: Path to output file (optional)
        target_format: Target format (wav, mp3, etc.)
        
    Returns:
        Path to converted file
    """
    if not PYDUB_AVAILABLE:
        raise ImportError("pydub not installed. Run: pip install pydub")
    
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.with_suffix(f".{target_format}"))
    
    print(f"Converting {input_path} to {target_format}")
    
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format=target_format)
    
    return output_path


def get_audio_duration(audio_path: str) -> float:
    """
    Get audio file duration in seconds
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Duration in seconds
    """
    if PYDUB_AVAILABLE:
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0  # Convert ms to seconds
    else:
        # Fallback: use ffprobe if available
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                capture_output=True,
                text=True
            )
            return float(result.stdout.strip())
        except:
            return 0.0


def validate_audio_file(audio_path: str, max_size_mb: int = 100) -> Tuple[bool, str]:
    """
    Validate audio file for transcription
    
    Args:
        audio_path: Path to audio file
        max_size_mb: Maximum file size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file exists
    if not os.path.exists(audio_path):
        return False, "File not found"
    
    # Check file size
    file_size = os.path.getsize(audio_path) / (1024 * 1024)  # MB
    if file_size > max_size_mb:
        return False, f"File too large: {file_size:.1f}MB (max {max_size_mb}MB)"
    
    # Check file extension
    valid_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm', '.mp4']
    ext = Path(audio_path).suffix.lower()
    if ext not in valid_extensions:
        return False, f"Unsupported format: {ext}"
    
    return True, ""


def split_long_audio(
    audio_path: str,
    chunk_duration_minutes: int = 10
) -> List[str]:
    """
    Split long audio file into chunks for processing
    
    Args:
        audio_path: Path to audio file
        chunk_duration_minutes: Duration of each chunk in minutes
        
    Returns:
        List of paths to audio chunks
    """
    if not PYDUB_AVAILABLE:
        raise ImportError("pydub not installed. Run: pip install pydub")
    
    audio = AudioSegment.from_file(audio_path)
    chunk_duration_ms = chunk_duration_minutes * 60 * 1000
    
    chunks = []
    input_file = Path(audio_path)
    
    for i, start_ms in enumerate(range(0, len(audio), chunk_duration_ms)):
        chunk = audio[start_ms:start_ms + chunk_duration_ms]
        chunk_path = str(input_file.parent / f"{input_file.stem}_chunk{i}{input_file.suffix}")
        chunk.export(chunk_path, format=input_file.suffix[1:])
        chunks.append(chunk_path)
    
    return chunks


def transcribe_audio_file(
    audio_path: str,
    backend: str = "auto",
    language: str = "en",
    model_size: str = "base",
    detect_speakers: bool = True
) -> Dict:
    """
    High-level function to transcribe audio file
    
    Args:
        audio_path: Path to audio file
        backend: Transcription backend
        language: Language code
        model_size: Whisper model size (for local)
        detect_speakers: Whether to detect speakers
        
    Returns:
        Transcription result with formatted text
    """
    # Validate file
    is_valid, error = validate_audio_file(audio_path)
    if not is_valid:
        raise ValueError(f"Invalid audio file: {error}")
    
    # Get duration
    duration = get_audio_duration(audio_path)
    print(f"Audio duration: {duration/60:.1f} minutes")
    
    # Transcribe
    transcriber = AudioTranscriber(backend=backend)
    result = transcriber.transcribe(audio_path, language, model_size)
    
    # Detect speakers if requested
    if detect_speakers and result["segments"]:
        result["segments"] = detect_speakers_simple(result["segments"])
        result["formatted_text"] = format_transcript_with_speakers(result["segments"])
    else:
        result["formatted_text"] = result["text"]
    
    result["duration"] = duration
    
    return result


# Recommended settings for different use cases
TRANSCRIPTION_PRESETS = {
    "fast": {
        "backend": "whisper-local",
        "model_size": "tiny",
        "description": "Fastest, lower accuracy"
    },
    "balanced": {
        "backend": "whisper-local",
        "model_size": "base",
        "description": "Good balance of speed and accuracy"
    },
    "accurate": {
        "backend": "whisper-local",
        "model_size": "small",
        "description": "Better accuracy, slower"
    },
    "high_quality": {
        "backend": "whisper-local",
        "model_size": "medium",
        "description": "High accuracy, requires GPU"
    },
    "api": {
        "backend": "whisper-api",
        "model_size": "whisper-1",
        "description": "OpenAI API (requires API key)"
    }
}


def get_transcription_presets() -> Dict:
    """Get available transcription presets"""
    return TRANSCRIPTION_PRESETS

