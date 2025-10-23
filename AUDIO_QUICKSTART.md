# Audio Extension - Quick Start

Add audio transcription to your IR Sentiment Analyzer in 15 minutes!

## Prerequisites

- IR Sentiment Analyzer already installed and working
- Python virtual environment activated
- 5GB+ free disk space (for Whisper models)

## Step 1: Install Dependencies (5 minutes)

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install audio processing packages
pip install openai-whisper pydub
```

## Step 2: Install FFmpeg (2 minutes)

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH
4. Restart terminal

**Verify:**
```bash
ffmpeg -version
```

## Step 3: Add Audio Module (1 minute)

Copy the audio processor to your backend:

```bash
# From the audio extension files
cp audio_processor.py backend/
```

## Step 4: Update Backend API (3 minutes)

Add these lines to `backend/main.py`:

```python
# At the top with other imports
from audio_processor import (
    transcribe_audio_file,
    get_transcription_presets,
    WHISPER_AVAILABLE
)

# Add these endpoints (copy from main_audio.py):

@app.get("/api/audio/status")
async def get_audio_status():
    """Check audio transcription availability"""
    return {
        "whisper_local_available": WHISPER_AVAILABLE,
        "presets": get_transcription_presets()
    }

@app.post("/api/documents/audio")
async def upload_audio_document(
    title: str = Form(...),
    document_type: str = Form(...),
    analysis_model: str = Form(default="llama3.2"),
    transcription_preset: str = Form(default="balanced"),
    language: str = Form(default="en"),
    detect_speakers: bool = Form(default=True),
    file: UploadFile = File(...)
):
    # Copy full implementation from main_audio.py
    pass
```

See `backend/main_audio.py` for complete endpoint implementations.

## Step 5: Update Frontend (2 minutes)

Add audio upload page to `frontend/app.py`:

```python
# In your page selection (around line 50-60)
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Upload Document", "Upload Audio",  # Add this
     "Document Analysis", "Comparisons", "Metrics & Trends", "Model Management"]
)

# Add this condition (around line 100)
elif page == "Upload Audio":
    # Copy render_audio_upload_page() function from pages_audio.py
    render_audio_upload_page()
```

Or create a separate page file:
```bash
mkdir -p frontend/pages
cp pages_audio.py frontend/pages/audio_upload.py
```

## Step 6: Restart Application (1 minute)

```bash
# Stop the current application (Ctrl+C)

# Restart
./start_app.sh  # or start_app.bat on Windows
```

## Step 7: Test Audio Upload (1 minute)

1. Open http://localhost:8501
2. Click "Upload Audio" in sidebar
3. You should see "✓ Audio transcription available"
4. Upload a test audio file
5. Wait for transcription and analysis

## First Audio Analysis

### Test with Sample Audio

If you don't have an earnings call recording, create a test file:

**macOS/Linux:**
```bash
# Record 10 seconds of audio
ffmpeg -f avfoundation -i ":0" -t 10 test.wav

# Or download a sample
curl -o test.mp3 "https://example.com/sample-earnings-call.mp3"
```

**Windows:**
```bash
# Record 10 seconds
ffmpeg -f dshow -i audio="Microphone" -t 10 test.wav
```

### Upload and Analyze

1. Go to "Upload Audio" page
2. Enter title: "Test Audio"
3. Select document type: "Earnings Call"
4. Choose preset: "Balanced"
5. Select model: "llama3.2"
6. Upload your audio file
7. Click "Upload and Analyze"
8. Wait 2-5 minutes

### View Results

1. Go to "Document Analysis"
2. Select your test document
3. Review transcription and analysis

## Troubleshooting

### "Audio transcription not available"

**Check Whisper installation:**
```bash
python -c "import whisper; print('Whisper OK')"
```

**If error, reinstall:**
```bash
pip uninstall openai-whisper
pip install openai-whisper
```

### "FFmpeg not found"

**Verify installation:**
```bash
ffmpeg -version
```

**If not found:**
- macOS: `brew install ffmpeg`
- Linux: `apt install ffmpeg`
- Windows: Add to PATH and restart terminal

### "Out of memory"

**Use smaller model:**
- Change preset from "Accurate" to "Fast"
- Or edit `audio_processor.py`:
  ```python
  "fast": {
      "model_size": "tiny",  # Smallest model
  }
  ```

### Slow transcription

**Expected times:**
- 10-min audio: 1-3 minutes
- 30-min audio: 3-9 minutes
- 60-min audio: 6-18 minutes

**To speed up:**
1. Use "Fast" preset (tiny model)
2. Enable GPU (automatic if available)
3. Use OpenAI API instead

## What's Next?

### Optimize for Your Use Case

**For Speed:**
```python
# In audio_processor.py, modify presets:
"fast": {
    "backend": "whisper-local",
    "model_size": "tiny",
}
```

**For Quality:**
```python
"high_quality": {
    "backend": "whisper-local",
    "model_size": "medium",  # or "large"
}
```

**For Cloud:**
```bash
# Install OpenAI package
pip install openai

# Set API key
export OPENAI_API_KEY="your-key-here"

# Use "api" preset in UI
```

### Process Multiple Files

Create a batch script:

```python
import requests
import os

audio_files = [
    ("Q1 2024", "q1.mp3"),
    ("Q2 2024", "q2.mp3"),
    ("Q3 2024", "q3.mp3"),
    ("Q4 2024", "q4.mp3"),
]

for title, filename in audio_files:
    with open(filename, "rb") as f:
        files = {"file": f}
        data = {
            "title": title,
            "document_type": "earnings_call",
            "analysis_model": "mistral",
            "transcription_preset": "balanced"
        }
        
        response = requests.post(
            "http://localhost:8000/api/documents/audio",
            files=files,
            data=data,
            timeout=1800
        )
        
        print(f"{title}: {response.status_code}")
```

### Advanced Speaker Detection

For better speaker identification:

```bash
pip install pyannote.audio
```

Then integrate into `audio_processor.py` (see AUDIO_EXTENSION.md for details).

## File Checklist

After integration, you should have:

```
✓ backend/audio_processor.py
✓ backend/main.py (updated with audio endpoints)
✓ frontend/app.py (updated with audio page)
✓ requirements-audio.txt
✓ docs/AUDIO_EXTENSION.md
```

## Cost & Performance

### Local Whisper (Recommended)

| Metric | Value |
|--------|-------|
| Setup time | 15 minutes |
| Cost | $0 |
| Speed | 1-3 min per 10-min audio |
| Quality | Good to Excellent |
| Privacy | 100% local |

### OpenAI API (Alternative)

| Metric | Value |
|--------|-------|
| Setup time | 2 minutes |
| Cost | $0.006/minute |
| Speed | ~1 min per 10-min audio |
| Quality | Excellent |
| Privacy | Cloud-based |

## Support

### Documentation
- Full guide: `docs/AUDIO_EXTENSION.md`
- Main README: `README.md`
- Ollama guide: `docs/OLLAMA_GUIDE.md`

### Common Issues
- Whisper not found → `pip install openai-whisper`
- FFmpeg not found → Install FFmpeg and add to PATH
- Out of memory → Use smaller model (tiny or base)
- Slow → Use GPU or OpenAI API

### Testing
```bash
# Test Whisper
python -c "import whisper; print(whisper.__version__)"

# Test FFmpeg
ffmpeg -version

# Test audio processing
python -c "from audio_processor import WHISPER_AVAILABLE; print(f'Whisper: {WHISPER_AVAILABLE}')"
```

---

**You're ready to analyze earnings calls from audio!** 🎙️

Upload your first audio file and see the magic happen. For detailed documentation, see `docs/AUDIO_EXTENSION.md`.

