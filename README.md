# IR Sentiment Analyzer - Ollama Edition

A **completely local** Python-based solution for analyzing investor relations documents using **Ollama** for AI-powered sentiment and linguistic analysis. No API keys required, fully offline-capable, and completely private.

## 🌟 Key Features

### 🔒 Complete Privacy
- **100% Local Processing** - All analysis runs on your machine
- **No Cloud APIs** - No data sent to external services
- **No API Keys** - No subscriptions or usage fees
- **Offline Capable** - Works without internet (after setup)

### 🤖 Flexible Model Selection
- **Multiple Model Support** - Choose from various Ollama models
- **In-App Model Selection** - Select model for each analysis
- **Model Testing** - Verify models before use
- **Recommended Models** - Curated list for IR analysis

### 📊 Comprehensive Analysis
- **5-Dimensional Scoring** - Sentiment, Confidence, Clarity, Readability, Specificity
- **Section-by-Section Review** - Detailed analysis with AI suggestions
- **Document Comparison** - Side-by-side metrics
- **Historical Tracking** - Trend analysis over time

## Prerequisites

### Required
- **Python 3.9+**
- **Ollama** - Local LLM runtime ([Install from ollama.ai](https://ollama.ai))
- **At least one Ollama model** (recommended: llama3.2, mistral, or llama3.1)

### System Requirements
- **RAM**: 8GB minimum (16GB recommended for larger models)
- **Disk Space**: 5-20GB per model
- **OS**: Windows, macOS, or Linux

## Installation

### Step 1: Install Ollama

Visit [ollama.ai](https://ollama.ai) and follow installation instructions for your OS.

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download and run the installer from ollama.ai

### Step 2: Start Ollama

```bash
ollama serve
```

Leave this running in a terminal window.

### Step 3: Install a Model

Choose and install at least one model:

```bash
# Recommended for speed (3B parameters)
ollama pull llama3.2

# Recommended for quality (7-8B parameters)
ollama pull mistral
ollama pull llama3.1

# For high-end systems (9B+ parameters)
ollama pull gemma2
```

**Model Comparison:**
| Model | Size | RAM Needed | Speed | Quality | Best For |
|-------|------|------------|-------|---------|----------|
| llama3.2 | 3B | 8GB | Fast | Good | Quick analysis |
| mistral | 7B | 12GB | Medium | Excellent | Balanced |
| llama3.1 | 8B | 12GB | Medium | Excellent | Detailed analysis |
| gemma2 | 9B | 16GB | Slower | Superior | Maximum quality |

### Step 4: Set Up the Application

```bash
# Extract the project
tar -xzf ir-analyzer-ollama.tar.gz
cd ir-analyzer-ollama

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start

**Option 1: Use the startup script**

```bash
# macOS/Linux
./start_app.sh

# Windows
start_app.bat
```

**Option 2: Manual startup**

Terminal 1 - Backend:
```bash
cd backend
python main.py
```

Terminal 2 - Frontend:
```bash
cd frontend
streamlit run app.py
```

### Access the Application

Open your browser and navigate to:
- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Using the Application

#### 1. Upload a Document

1. Click "Upload Document" in the sidebar
2. Enter document title and select type
3. **Choose your model** from the dropdown
4. Upload your file (PDF, TXT, DOC, DOCX)
5. Click "Upload and Analyze"
6. Wait 1-3 minutes for analysis to complete

#### 2. View Analysis

1. Go to "Document Analysis"
2. Select your document
3. Explore the tabs:
   - **Overview**: Summary and key themes
   - **Sections**: Detailed section-by-section analysis with AI suggestions
   - **Emotional Tone**: Tone distribution chart
   - **Linguistic Metrics**: Advanced metrics

#### 3. Compare Documents

1. Go to "Comparisons"
2. Create a new comparison
3. Select 2+ documents
4. View side-by-side metrics and radar charts

#### 4. Track Trends

1. Go to "Metrics & Trends"
2. View historical performance
3. Track improvements over time
4. Filter by document type

#### 5. Manage Models

1. Go to "Model Management"
2. View installed models
3. Test model functionality
4. See installation instructions for recommended models

## Model Selection Guide

### For Quick Analysis
- **llama3.2** (3B) - Fast, good quality, low RAM
- Best for: Quick reviews, testing, lower-end systems

### For Balanced Performance
- **mistral** (7B) - Excellent quality, reasonable speed
- **llama3.1** (8B) - High quality, good for detailed analysis
- Best for: Most use cases, production analysis

### For Maximum Quality
- **gemma2** (9B) - Superior analysis, slower
- Best for: Critical documents, when quality is paramount

### Switching Models

You can use different models for different documents:
- Use **llama3.2** for quick initial reviews
- Use **mistral** or **llama3.1** for final versions
- Use **gemma2** for investor-facing documents

## Project Structure

```
ir-analyzer-ollama/
├── backend/
│   ├── main.py                 # FastAPI application with Ollama integration
│   ├── database.py             # SQLite database operations
│   ├── analysis_engine.py      # Ollama-based analysis engine
│   └── document_processor.py   # Text extraction utilities
│
├── frontend/
│   └── app.py                  # Streamlit UI with model selection
│
├── data/
│   ├── uploads/                # Uploaded documents
│   └── ir_analyzer.db          # SQLite database
│
├── docs/
│   ├── API.md                  # API documentation
│   └── OLLAMA_GUIDE.md         # Ollama setup and usage guide
│
├── requirements.txt            # Python dependencies
├── start_app.sh               # Startup script (Unix)
├── start_app.bat              # Startup script (Windows)
└── README.md                  # This file
```

## Configuration

### Environment Variables

Create a `.env` file (optional):

```bash
# Backend API URL (for frontend)
API_BASE_URL=http://localhost:8000

# Ollama API URL (if running on different host)
OLLAMA_API_URL=http://localhost:11434/api
```

### Ollama Configuration

Ollama runs on `localhost:11434` by default. To change:

```bash
# Set custom host/port
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

## Troubleshooting

### Ollama Not Available

**Error:** "Ollama is not running"

**Solutions:**
1. Start Ollama: `ollama serve`
2. Check if running: `curl http://localhost:11434`
3. Restart Ollama service

### No Models Available

**Error:** "No models installed"

**Solutions:**
1. Install a model: `ollama pull llama3.2`
2. List installed models: `ollama list`
3. Verify model works: `ollama run llama3.2 "test"`

### Analysis Takes Too Long

**Issue:** Analysis timing out or taking >5 minutes

**Solutions:**
1. Use a smaller model (llama3.2 instead of gemma2)
2. Reduce document length
3. Increase RAM allocation
4. Close other applications

### Out of Memory

**Error:** "Out of memory" or system freezing

**Solutions:**
1. Use a smaller model
2. Close other applications
3. Increase system RAM
4. Process shorter documents

### Model Test Fails

**Error:** "Model test failed"

**Solutions:**
1. Verify model is installed: `ollama list`
2. Try running model directly: `ollama run <model> "test"`
3. Reinstall model: `ollama pull <model>`
4. Check Ollama logs

### Backend Won't Start

**Error:** "Address already in use"

**Solutions:**
1. Kill process on port 8000: `lsof -ti:8000 | xargs kill`
2. Change port in `backend/main.py`
3. Restart your computer

### Frontend Won't Connect

**Error:** "Unable to connect to backend API"

**Solutions:**
1. Ensure backend is running
2. Check backend URL in frontend
3. Verify no firewall blocking localhost
4. Try accessing http://localhost:8000/health

## Performance Tips

### Speed Optimization
1. Use **llama3.2** for fastest analysis
2. Keep documents under 5,000 words
3. Close unnecessary applications
4. Use SSD for model storage

### Quality Optimization
1. Use **mistral** or **llama3.1** for best balance
2. Use **gemma2** for critical documents
3. Provide clear, well-formatted documents
4. Review and refine prompts in `analysis_engine.py`

### System Optimization
1. Allocate sufficient RAM to Ollama
2. Use GPU acceleration if available (see Ollama docs)
3. Keep models on fast storage (SSD)
4. Monitor system resources during analysis

## Comparison: Ollama vs OpenAI

| Feature | Ollama | OpenAI |
|---------|--------|--------|
| **Privacy** | 100% local | Cloud-based |
| **Cost** | Free (hardware only) | $0.01-0.05 per document |
| **Internet** | Not required | Required |
| **Setup** | Install Ollama + models | API key only |
| **Speed** | 1-3 minutes | 30-60 seconds |
| **Quality** | Good to excellent | Excellent |
| **Customization** | Full control | Limited |
| **Best For** | Privacy, offline, no costs | Speed, convenience |

## Advanced Usage

### Custom Models

You can use any Ollama-compatible model:

```bash
# Install custom model
ollama pull <model-name>

# Use in application
# Select from dropdown in Upload page
```

### API Integration

The FastAPI backend provides REST endpoints for integration:

```python
import requests

# Upload and analyze
files = {"file": open("document.pdf", "rb")}
data = {"title": "Q4 Earnings", "document_type": "earnings_call", "model": "llama3.2"}
response = requests.post("http://localhost:8000/api/documents", files=files, data=data)
```

See `docs/API.md` for full API documentation.

### Batch Processing

Process multiple documents:

```python
import os
import requests

documents = [
    ("Q1 Earnings", "earnings_call", "q1.pdf"),
    ("Q2 Earnings", "earnings_call", "q2.pdf"),
]

for title, doc_type, filename in documents:
    with open(filename, "rb") as f:
        files = {"file": f}
        data = {"title": title, "document_type": doc_type, "model": "mistral"}
        response = requests.post("http://localhost:8000/api/documents", files=files, data=data)
        print(f"Uploaded {title}: {response.status_code}")
```

## Development

### Modifying Analysis Prompts

Edit `backend/analysis_engine.py` to customize:
- Analysis criteria
- Scoring methodology
- Section detection logic
- Suggestion generation

### Adding New Models

Recommended models are defined in `analysis_engine.py`:

```python
RECOMMENDED_MODELS = [
    {
        "name": "your-model",
        "size": "7B",
        "description": "Your description",
        "recommended": True
    }
]
```

### Testing

Test the backend:
```bash
cd backend
python -m pytest tests/
```

Test Ollama connection:
```bash
curl http://localhost:11434/api/tags
```

## Deployment

### Local Network Access

Allow access from other devices on your network:

**Backend:**
```bash
# In backend/main.py, change:
uvicorn.run("main:app", host="0.0.0.0", port=8000)
```

**Frontend:**
```bash
streamlit run app.py --server.address 0.0.0.0
```

Access from other devices using your machine's IP address.

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "python backend/main.py & streamlit run frontend/app.py"]
```

**Note:** Ollama must be running on the host or in a separate container.

## Security

- **Local Only**: Designed for local use, not internet-exposed
- **No Authentication**: Single-user system
- **Data Privacy**: All data stays on your machine
- **File Validation**: Validates file types and sizes
- **SQL Injection**: Protected by parameterized queries

## Limitations

- Single-user system (no authentication)
- Slower than cloud APIs (1-3 minutes vs 30-60 seconds)
- Requires significant RAM for larger models
- SQLite database (not for high concurrency)
- No cloud storage integration

## FAQ

**Q: Do I need an API key?**
A: No! Ollama runs completely locally with no API keys required.

**Q: Can I use this offline?**
A: Yes! After installing Ollama and downloading models, it works completely offline.

**Q: How much does it cost?**
A: Free! Only cost is your hardware. No subscriptions or usage fees.

**Q: Which model should I use?**
A: Start with **llama3.2** for speed, upgrade to **mistral** for quality.

**Q: How long does analysis take?**
A: 1-3 minutes depending on document length and model size.

**Q: Can I use multiple models?**
A: Yes! Select a different model for each document upload.

**Q: Is my data private?**
A: Completely! All processing happens on your machine. Nothing is sent to the cloud.

**Q: Can I customize the analysis?**
A: Yes! Edit the prompts in `backend/analysis_engine.py`.

## Support

### Getting Help

1. Check this README and troubleshooting section
2. Review Ollama documentation: https://ollama.ai/docs
3. Check GitHub issues
4. Test with `ollama run <model> "test"`

### Reporting Issues

When reporting issues, include:
- Operating system
- Python version
- Ollama version (`ollama --version`)
- Installed models (`ollama list`)
- Error messages
- Steps to reproduce

## License

This project is proprietary software. All rights reserved.

## Acknowledgments

- Built with **FastAPI** and **Streamlit**
- Powered by **Ollama** for local LLM inference
- Document processing with **PyPDF2** and **python-docx**
- Visualizations with **Plotly**
- Inspired by the need for private, local AI analysis

## Changelog

### Version 2.0.0 (Ollama Edition)
- ✨ Ollama integration for local LLM inference
- ✨ In-app model selection
- ✨ Model management interface
- ✨ Model testing functionality
- ✨ No API keys required
- ✨ Complete offline capability
- ✨ 100% private and local processing

---

**Ready to analyze your IR documents privately and locally? Start Ollama and run the app!** 🚀

