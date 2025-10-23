# Audio Extension Guide

Complete guide to extending the IR Sentiment Analyzer with audio transcription capabilities for earnings calls.

## Overview

This extension adds the ability to:
- Upload audio files (MP3, WAV, M4A, etc.)
- Automatically transcribe speech to text using Whisper
- Detect and label different speakers
- Analyze transcribed content with Ollama
- Track audio-specific metadata

## Architecture

```
Audio File → Transcription → Text Analysis → Results
     ↓            ↓              ↓            ↓
  Upload      Whisper        Ollama      Database
```

## Installation

### Step 1: Install Audio Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install Whisper for transcription
pip install openai-whisper

# Install audio processing libraries
pip install pydub

# Optional: OpenAI API for cloud transcription
pip install openai
```

### Step 2: Install FFmpeg

FFmpeg is required for audio format conversion.

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH

**Verify installation:**
```bash
ffmpeg -version
```

### Step 3: Add Audio Processing Module

Copy `backend/audio_processor.py` to your backend directory.

### Step 4: Update Backend API

Add the audio endpoints from `backend/main_audio.py` to your `backend/main.py`:

```python
# Add these imports at the top
from audio_processor import (
    transcribe_audio_file,
    validate_audio_file,
    get_audio_duration,
    get_transcription_presets,
    WHISPER_AVAILABLE
)

# Add the endpoints (copy from main_audio.py):
# - /api/audio/status
# - /api/audio/transcribe
# - /api/documents/audio
```

### Step 5: Update Frontend

Add the audio upload page to your Streamlit app:

**Option A: Integrate into existing app.py**
```python
# In your page selection
elif page == "Upload Audio":
    from pages_audio import render_audio_upload_page
    render_audio_upload_page()
```

**Option B: Create separate page file**
```bash
mkdir -p frontend/pages
cp pages_audio.py frontend/pages/audio_upload.py
```

Streamlit will automatically detect and add it to the sidebar.

### Step 6: Update Requirements

Add to `requirements.txt`:
```
openai-whisper==20231117
pydub==0.25.1
```

Optional for API transcription:
```
openai==1.3.0
```

## Usage

### Basic Audio Upload

1. Start the application
2. Navigate to "Upload Audio" page
3. Enter document title
4. Select transcription quality preset
5. Choose analysis model
6. Upload audio file
7. Wait for transcription and analysis (5-10 minutes for 30-minute call)
8. View results in "Document Analysis" page

### Transcription Presets

| Preset | Model | Speed | Accuracy | RAM | Best For |
|--------|-------|-------|----------|-----|----------|
| **Fast** | tiny | ⚡⚡⚡ | ⭐⭐ | 1GB | Quick tests |
| **Balanced** | base | ⚡⚡ | ⭐⭐⭐ | 1GB | Most use cases |
| **Accurate** | small | ⚡ | ⭐⭐⭐⭐ | 2GB | Important calls |
| **High Quality** | medium | 🐌 | ⭐⭐⭐⭐⭐ | 5GB | Critical documents |
| **API** | whisper-1 | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 0GB | Cloud option |

### Processing Time Estimates

| Audio Length | Transcription | Analysis | Total |
|--------------|---------------|----------|-------|
| 10 minutes | 1-3 min | 1-2 min | 2-5 min |
| 30 minutes | 3-9 min | 2-3 min | 5-12 min |
| 60 minutes | 6-18 min | 3-4 min | 9-22 min |

*Times vary based on hardware and model size*

## API Endpoints

### Check Audio Status

```bash
GET /api/audio/status
```

**Response:**
```json
{
  "whisper_local_available": true,
  "presets": {
    "fast": {
      "backend": "whisper-local",
      "model_size": "tiny",
      "description": "Fastest, lower accuracy"
    },
    ...
  }
}
```

### Transcribe Audio Only

```bash
POST /api/audio/transcribe
Content-Type: multipart/form-data

file: <audio_file>
language: "en"
preset: "balanced"
detect_speakers: true
```

**Response:**
```json
{
  "success": true,
  "text": "Full transcript...",
  "formatted_text": "Speaker 1: ...\nSpeaker 2: ...",
  "language": "en",
  "duration": 1234.5,
  "segments": 45,
  "backend": "whisper-local",
  "model": "base"
}
```

### Upload Audio Document

```bash
POST /api/documents/audio
Content-Type: multipart/form-data

file: <audio_file>
title: "Q4 2024 Earnings Call"
document_type: "earnings_call"
analysis_model: "llama3.2"
transcription_preset: "balanced"
language: "en"
detect_speakers: true
```

**Response:**
```json
{
  "success": true,
  "document_id": 123,
  "transcription": {
    "duration": 1234.5,
    "language": "en",
    "segments": 45,
    "backend": "whisper-local"
  },
  "analysis": {
    "sentiment_score": 75,
    "confidence_score": 68,
    "clarity_score": 72
  }
}
```

## Python API

### Transcribe Audio File

```python
from audio_processor import transcribe_audio_file

result = transcribe_audio_file(
    audio_path="earnings_call.mp3",
    backend="whisper-local",  # or "whisper-api"
    language="en",
    model_size="base",
    detect_speakers=True
)

print(result["text"])  # Full transcript
print(result["formatted_text"])  # With speaker labels
print(f"Duration: {result['duration']/60:.1f} minutes")
```

### Convert Audio Format

```python
from audio_processor import convert_audio_format

wav_path = convert_audio_format(
    input_path="recording.m4a",
    target_format="wav"
)
```

### Validate Audio File

```python
from audio_processor import validate_audio_file

is_valid, error = validate_audio_file("audio.mp3", max_size_mb=100)
if not is_valid:
    print(f"Invalid: {error}")
```

### Split Long Audio

```python
from audio_processor import split_long_audio

chunks = split_long_audio(
    audio_path="long_call.mp3",
    chunk_duration_minutes=10
)

for chunk_path in chunks:
    result = transcribe_audio_file(chunk_path)
    print(result["text"])
```

## Advanced Features

### Speaker Diarization

The basic speaker detection uses pause-based heuristics. For better results, integrate pyannote.audio:

```bash
pip install pyannote.audio
```

```python
from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
diarization = pipeline("audio.wav")

for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"{speaker}: {turn.start:.1f}s - {turn.end:.1f}s")
```

### Custom Whisper Models

Use fine-tuned or custom Whisper models:

```python
import whisper

# Load custom model
model = whisper.load_model("path/to/custom/model.pt")

result = model.transcribe("audio.mp3")
```

### GPU Acceleration

Whisper automatically uses GPU if available. To verify:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

### Batch Processing

Process multiple audio files:

```python
import os
from audio_processor import transcribe_audio_file

audio_files = [
    "q1_earnings.mp3",
    "q2_earnings.mp3",
    "q3_earnings.mp3",
    "q4_earnings.mp3"
]

for audio_file in audio_files:
    print(f"Processing {audio_file}...")
    result = transcribe_audio_file(audio_file)
    
    # Save transcript
    transcript_path = audio_file.replace(".mp3", ".txt")
    with open(transcript_path, "w") as f:
        f.write(result["formatted_text"])
```

## Optimization

### Speed Optimization

1. **Use smaller models**: `tiny` or `base` for faster transcription
2. **Use GPU**: Automatic if CUDA available
3. **Reduce audio quality**: Convert to lower bitrate
4. **Split long files**: Process chunks in parallel

```python
from concurrent.futures import ThreadPoolExecutor
from audio_processor import split_long_audio, transcribe_audio_file

chunks = split_long_audio("long_call.mp3", chunk_duration_minutes=10)

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(transcribe_audio_file, chunks)
    
full_transcript = "\n\n".join([r["text"] for r in results])
```

### Quality Optimization

1. **Use larger models**: `small`, `medium`, or `large`
2. **Provide language hint**: Improves accuracy
3. **Clean audio**: Remove noise, normalize volume
4. **Use API**: OpenAI Whisper API for best quality

### Memory Optimization

1. **Process in chunks**: For very long audio
2. **Clear cache**: Delete temporary files
3. **Use smaller models**: Reduce RAM usage

```python
import gc
import torch

# After processing
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()
```

## Troubleshooting

### Whisper Not Found

**Error:** `ModuleNotFoundError: No module named 'whisper'`

**Solution:**
```bash
pip install openai-whisper
```

### FFmpeg Not Found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solution:** Install FFmpeg (see Installation section)

### Out of Memory

**Error:** `RuntimeError: CUDA out of memory` or system freezing

**Solutions:**
1. Use smaller model: `tiny` or `base`
2. Close other applications
3. Process shorter audio segments
4. Use CPU instead of GPU

### Slow Transcription

**Issue:** Transcription takes too long

**Solutions:**
1. Use smaller model (tiny, base)
2. Enable GPU acceleration
3. Use OpenAI API instead
4. Reduce audio quality/length

### Poor Accuracy

**Issue:** Transcription has many errors

**Solutions:**
1. Use larger model (small, medium, large)
2. Specify correct language
3. Improve audio quality
4. Use OpenAI API
5. Fine-tune Whisper on domain-specific data

### Speaker Detection Not Working

**Issue:** All text attributed to one speaker

**Solutions:**
1. Ensure `detect_speakers=True`
2. Audio must have clear pauses between speakers
3. Consider using pyannote.audio for better diarization
4. Manually edit speaker labels in transcript

## Cost Comparison

### Local Whisper (Recommended)

| Item | Cost |
|------|------|
| Software | Free |
| Hardware | One-time investment |
| Per-transcription | $0 |
| **Total** | **$0 recurring** |

**Hardware requirements:**
- CPU only: Works but slow
- GPU (NVIDIA): 10-50x faster
- Recommended: RTX 3060 or better

### OpenAI Whisper API

| Item | Cost |
|------|------|
| Per minute | $0.006 |
| 30-min call | $0.18 |
| 100 calls/month | $18 |
| **Total** | **$18-50/month** |

**Advantages:**
- No hardware needed
- Faster than CPU-only
- Highest accuracy
- No setup required

## Best Practices

### Audio Preparation

1. **Format**: Convert to MP3 or WAV
2. **Quality**: Use at least 16kHz sample rate
3. **Size**: Keep under 100 MB (split if larger)
4. **Noise**: Remove background noise if possible

### Model Selection

1. **Development**: Use `tiny` or `base` for speed
2. **Testing**: Use `small` for quality checks
3. **Production**: Use `medium` or API for final transcripts
4. **Critical**: Use `large` or API for investor-facing documents

### Workflow

1. **Upload audio** with appropriate preset
2. **Review transcript** for accuracy
3. **Edit if needed** (manual corrections)
4. **Analyze** with Ollama
5. **Review analysis** and suggestions
6. **Compare** with previous calls

### Data Management

1. **Store audio files** separately from transcripts
2. **Keep transcripts** as text files for backup
3. **Tag documents** with metadata (date, quarter, speakers)
4. **Archive** old recordings to save space

## Integration Examples

### Automated Pipeline

```python
import os
from audio_processor import transcribe_audio_file
from analysis_engine import analyze_document_content

def process_earnings_call(audio_path, quarter, year):
    """Complete pipeline for earnings call processing"""
    
    # Transcribe
    print("Transcribing...")
    transcript = transcribe_audio_file(
        audio_path,
        backend="whisper-local",
        model_size="base",
        detect_speakers=True
    )
    
    # Save transcript
    transcript_path = f"transcripts/{year}_Q{quarter}.txt"
    with open(transcript_path, "w") as f:
        f.write(transcript["formatted_text"])
    
    # Analyze
    print("Analyzing...")
    analysis = analyze_document_content(
        transcript["formatted_text"],
        model="mistral"
    )
    
    # Save results
    results = {
        "quarter": quarter,
        "year": year,
        "duration": transcript["duration"],
        "sentiment_score": analysis["sentiment_score"],
        "confidence_score": analysis["confidence_score"],
        "clarity_score": analysis["clarity_score"]
    }
    
    return results

# Process all quarterly calls
for quarter in [1, 2, 3, 4]:
    audio_file = f"earnings/2024_Q{quarter}.mp3"
    if os.path.exists(audio_file):
        results = process_earnings_call(audio_file, quarter, 2024)
        print(f"Q{quarter}: Sentiment {results['sentiment_score']}/100")
```

### Web Hook Integration

```python
from fastapi import FastAPI, BackgroundTasks

@app.post("/webhook/audio-uploaded")
async def handle_audio_upload(
    url: str,
    background_tasks: BackgroundTasks
):
    """Process audio uploaded to external service"""
    
    # Download audio
    audio_path = download_audio(url)
    
    # Process in background
    background_tasks.add_task(
        process_and_analyze_audio,
        audio_path
    )
    
    return {"status": "processing"}
```

## FAQ

**Q: How long does transcription take?**
A: Typically 10-30% of audio duration. A 30-minute call takes 3-9 minutes.

**Q: Can I use this offline?**
A: Yes! Local Whisper works completely offline after installation.

**Q: What's the maximum audio length?**
A: No hard limit, but split files >1 hour for better performance.

**Q: How accurate is the transcription?**
A: 90-95% accuracy for clear audio with the `base` model. Higher with larger models.

**Q: Can it identify individual speakers?**
A: Basic speaker detection is included. For better results, use pyannote.audio.

**Q: Does it work with multiple languages?**
A: Yes! Whisper supports 90+ languages. Specify with `language` parameter.

**Q: Can I edit transcripts before analysis?**
A: Yes. Save transcript to file, edit manually, then upload as text document.

**Q: How much does it cost?**
A: Local Whisper is free. OpenAI API costs $0.006/minute (~$0.18 for 30-min call).

## Resources

### Documentation
- Whisper: https://github.com/openai/whisper
- OpenAI API: https://platform.openai.com/docs/guides/speech-to-text
- pyannote.audio: https://github.com/pyannote/pyannote-audio
- FFmpeg: https://ffmpeg.org/documentation.html

### Models
- Whisper models: https://github.com/openai/whisper#available-models-and-languages
- Custom models: https://huggingface.co/models?other=whisper

### Tools
- Audio editing: Audacity (free)
- Noise reduction: Adobe Audition, RX
- Format conversion: FFmpeg, VLC

---

**Ready to analyze earnings calls from audio!** 🎙️📊

For questions or issues, see the troubleshooting section or check the main README.md.

