# Quick Start Guide - Ollama Edition

Get the IR Sentiment Analyzer running with Ollama in 10 minutes!

## Prerequisites

- Python 3.9+ installed
- 8GB+ RAM (16GB recommended)
- 10GB+ free disk space

## Step 1: Install Ollama (5 minutes)

### macOS/Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
Download and run installer from [ollama.ai](https://ollama.ai)

### Verify Installation
```bash
ollama --version
```

## Step 2: Start Ollama

```bash
ollama serve
```

Leave this terminal window open.

## Step 3: Install a Model (2-5 minutes)

Open a **new terminal** and run:

```bash
# Recommended: Fast and efficient (2GB download)
ollama pull llama3.2

# Alternative: Higher quality (4GB download)
ollama pull mistral
```

Wait for download to complete.

## Step 4: Set Up the Application (2 minutes)

```bash
# Extract the project
tar -xzf ir-analyzer-ollama.tar.gz
cd ir-analyzer-ollama

# Run the startup script
./start_app.sh  # macOS/Linux
# OR
start_app.bat   # Windows
```

The script will:
- Create a virtual environment
- Install Python dependencies
- Start the backend API
- Start the frontend UI

## Step 5: Access the Application

Open your browser and go to:

**http://localhost:8501**

You should see the IR Sentiment Analyzer interface with a green "Ollama Running" status.

## First Analysis

### 1. Upload a Document

1. Click **"Upload Document"** in the sidebar
2. Enter a title (e.g., "Test Document")
3. Select document type
4. **Choose model**: Select "llama3.2" from dropdown
5. Upload your file (PDF, TXT, DOC, or DOCX)
6. Click **"Upload and Analyze"**

### 2. Wait for Analysis

- Analysis takes 1-3 minutes
- Progress shown in UI
- You'll see a success message when complete

### 3. View Results

1. Go to **"Document Analysis"** in sidebar
2. Select your document
3. Explore the tabs:
   - **Overview**: Summary and key themes
   - **Sections**: Detailed analysis with AI suggestions
   - **Emotional Tone**: Tone distribution chart
   - **Linguistic Metrics**: Advanced metrics

## Troubleshooting

### "Ollama Not Available"

**Solution**: Make sure Ollama is running
```bash
ollama serve
```

### "No Models Available"

**Solution**: Install a model
```bash
ollama pull llama3.2
```

### "Unable to connect to backend API"

**Solution**: Wait 10 seconds for backend to start, then refresh the page.

### Analysis Takes Too Long

**Solution**: Use a smaller model or shorter document
```bash
# If using gemma2, switch to llama3.2
ollama pull llama3.2
```

## Manual Startup

If the startup script doesn't work:

**Terminal 1 - Start Ollama:**
```bash
ollama serve
```

**Terminal 2 - Start Backend:**
```bash
cd ir-analyzer-ollama
source venv/bin/activate  # or venv\Scripts\activate on Windows
cd backend
python main.py
```

**Terminal 3 - Start Frontend:**
```bash
cd ir-analyzer-ollama
source venv/bin/activate  # or venv\Scripts\activate on Windows
cd frontend
streamlit run app.py
```

## Model Recommendations

| Model | Speed | Quality | RAM | Best For |
|-------|-------|---------|-----|----------|
| **llama3.2** | ⚡⚡⚡ | ⭐⭐⭐ | 8GB | Quick analysis, testing |
| **mistral** | ⚡⚡ | ⭐⭐⭐⭐ | 12GB | Production use |
| **llama3.1** | ⚡⚡ | ⭐⭐⭐⭐ | 12GB | Detailed analysis |
| **gemma2** | ⚡ | ⭐⭐⭐⭐⭐ | 16GB | Maximum quality |

## Next Steps

1. **Read the full README.md** for detailed documentation
2. **Check docs/OLLAMA_GUIDE.md** for Ollama setup and optimization
3. **Explore Model Management** page to test and manage models
4. **Try document comparisons** to track improvements over time

## Getting Help

- Check the **README.md** troubleshooting section
- Review **docs/OLLAMA_GUIDE.md** for Ollama-specific issues
- Verify Ollama is running: `curl http://localhost:11434`
- Test your model: `ollama run llama3.2 "test"`

## Key Features to Explore

✅ **Multiple Models** - Switch between models for different needs
✅ **Section Analysis** - Get detailed suggestions for each section
✅ **Document Comparison** - Compare multiple documents side-by-side
✅ **Metrics Tracking** - Track improvements over time
✅ **Model Management** - Test and manage your installed models

## Privacy & Cost

✅ **100% Private** - All analysis happens on your machine
✅ **No API Keys** - No external services required
✅ **Offline Capable** - Works without internet after setup
✅ **Zero Cost** - Free to use (hardware only)

---

**Ready to analyze your IR documents privately and locally!** 📊🔒

For questions or issues, see the troubleshooting sections in README.md or OLLAMA_GUIDE.md.

