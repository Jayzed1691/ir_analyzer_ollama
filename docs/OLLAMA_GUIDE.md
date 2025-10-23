# Ollama Setup and Usage Guide

Complete guide to setting up and using Ollama with the IR Sentiment Analyzer.

## What is Ollama?

Ollama is a local LLM (Large Language Model) runtime that allows you to run AI models on your own computer. It provides:

- **Privacy**: All processing happens locally
- **No API costs**: Free to use after installation
- **Offline capability**: Works without internet
- **Multiple models**: Choose from various open-source models
- **Easy management**: Simple CLI for model installation

## Installation

### macOS

```bash
# Using the install script
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from ollama.ai
```

### Linux

```bash
# Using the install script
curl -fsSL https://ollama.ai/install.sh | sh

# Or install manually
# Ubuntu/Debian
sudo apt install ollama

# Fedora
sudo dnf install ollama
```

### Windows

1. Download installer from [ollama.ai](https://ollama.ai)
2. Run the installer
3. Ollama will start automatically

### Docker

```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

## Starting Ollama

### macOS/Linux

```bash
# Start Ollama server
ollama serve

# Or run as background service
# macOS
brew services start ollama

# Linux (systemd)
sudo systemctl start ollama
sudo systemctl enable ollama  # Start on boot
```

### Windows

Ollama starts automatically after installation. Check system tray for icon.

### Verify Installation

```bash
# Check if Ollama is running
curl http://localhost:11434

# Should return: "Ollama is running"
```

## Installing Models

### Recommended Models for IR Analysis

#### llama3.2 (3B) - Fast & Efficient
```bash
ollama pull llama3.2
```
- **Size**: ~2GB
- **RAM**: 8GB minimum
- **Speed**: Fast (~1 minute per document)
- **Quality**: Good
- **Best for**: Quick analysis, testing, lower-end systems

#### mistral (7B) - Balanced
```bash
ollama pull mistral
```
- **Size**: ~4GB
- **RAM**: 12GB recommended
- **Speed**: Medium (~2 minutes per document)
- **Quality**: Excellent
- **Best for**: Production use, balanced performance

#### llama3.1 (8B) - High Quality
```bash
ollama pull llama3.1
```
- **Size**: ~4.7GB
- **RAM**: 12GB recommended
- **Speed**: Medium (~2-3 minutes per document)
- **Quality**: Excellent
- **Best for**: Detailed analysis, important documents

#### gemma2 (9B) - Maximum Quality
```bash
ollama pull gemma2
```
- **Size**: ~5.4GB
- **RAM**: 16GB recommended
- **Speed**: Slower (~3-4 minutes per document)
- **Quality**: Superior
- **Best for**: Critical investor-facing documents

### Model Management Commands

```bash
# List installed models
ollama list

# Remove a model
ollama rm llama3.2

# Update a model
ollama pull llama3.2

# Show model information
ollama show llama3.2

# Run a model interactively
ollama run llama3.2
```

## Testing Models

### Quick Test

```bash
# Test if model works
ollama run llama3.2 "What is investor relations?"

# Test JSON output (used by our app)
ollama run llama3.2 "Respond with JSON: {\"status\": \"ok\"}"
```

### Performance Test

```bash
# Time a simple query
time ollama run llama3.2 "Analyze this text: The company reported strong earnings."
```

### In-App Testing

Use the "Model Management" page in the application to test models directly.

## Configuration

### Change Ollama Port

```bash
# Set custom port
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

### Increase Context Window

```bash
# Allow longer documents
export OLLAMA_NUM_CTX=8192
ollama serve
```

### GPU Acceleration

Ollama automatically uses GPU if available. To verify:

```bash
# Check GPU usage while running
nvidia-smi  # NVIDIA GPUs
```

### Memory Allocation

```bash
# Limit memory usage (in GB)
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
```

## Troubleshooting

### Ollama Won't Start

**Issue**: `ollama serve` fails

**Solutions**:
```bash
# Check if already running
ps aux | grep ollama

# Kill existing process
pkill ollama

# Check port availability
lsof -i :11434

# Try different port
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

### Model Download Fails

**Issue**: `ollama pull` times out or fails

**Solutions**:
```bash
# Check internet connection
ping ollama.ai

# Try again (resume download)
ollama pull llama3.2

# Use different network
# Download on different network, then copy models
```

### Out of Memory

**Issue**: System freezes or "out of memory" errors

**Solutions**:
1. Use smaller model (llama3.2 instead of gemma2)
2. Close other applications
3. Increase swap space (Linux)
4. Upgrade RAM

### Slow Performance

**Issue**: Analysis takes >5 minutes

**Solutions**:
1. Use smaller model
2. Reduce document length
3. Enable GPU acceleration
4. Close background applications
5. Use SSD for model storage

### Model Not Found

**Issue**: "Model not found" error

**Solutions**:
```bash
# List installed models
ollama list

# Install missing model
ollama pull llama3.2

# Verify installation
ollama run llama3.2 "test"
```

## Performance Optimization

### System Requirements by Model

| Model | Min RAM | Recommended RAM | Min Disk | GPU |
|-------|---------|----------------|----------|-----|
| llama3.2 | 8GB | 12GB | 5GB | Optional |
| mistral | 12GB | 16GB | 8GB | Recommended |
| llama3.1 | 12GB | 16GB | 10GB | Recommended |
| gemma2 | 16GB | 24GB | 12GB | Recommended |

### Speed Optimization

1. **Use GPU**: Automatic if available
2. **Use SSD**: Store models on fast storage
3. **Close Apps**: Free up RAM
4. **Smaller Models**: Use llama3.2 for speed
5. **Batch Processing**: Process multiple documents sequentially

### Quality Optimization

1. **Larger Models**: Use mistral or gemma2
2. **Longer Context**: Increase OLLAMA_NUM_CTX
3. **Better Prompts**: Customize in analysis_engine.py
4. **Clean Documents**: Well-formatted input = better output

## Advanced Usage

### Custom Models

You can use any Ollama-compatible model:

```bash
# Browse models at ollama.ai/library
ollama pull codellama  # For technical documents
ollama pull llama2     # Alternative option
```

### Model Quantization

Ollama uses optimized quantized models by default. For even smaller models:

```bash
# Some models have multiple quantization levels
ollama pull llama3.2:q4_0  # More compressed
ollama pull llama3.2:q8_0  # Higher quality
```

### Running Multiple Models

```bash
# Keep multiple models loaded (requires more RAM)
export OLLAMA_MAX_LOADED_MODELS=2
ollama serve
```

### API Access

Ollama provides a REST API:

```bash
# Generate completion
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Analyze this earnings call",
  "stream": false
}'

# Chat completion
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [
    {"role": "user", "content": "Hello"}
  ]
}'
```

## Integration with IR Analyzer

### How It Works

1. **Upload**: User uploads document via Streamlit UI
2. **Extract**: Backend extracts text from document
3. **Analyze**: Backend sends text to Ollama with analysis prompt
4. **Parse**: Backend parses JSON response from Ollama
5. **Store**: Results saved to SQLite database
6. **Display**: Frontend shows analysis to user

### Model Selection Flow

1. User selects model from dropdown
2. Frontend sends model name with upload request
3. Backend validates model exists
4. Backend uses specified model for analysis
5. Model name not stored (can re-analyze with different model)

### Customizing Prompts

Edit `backend/analysis_engine.py`:

```python
def analyze_document_content(text: str, model: str = "llama3.2"):
    prompt = f"""Your custom prompt here...
    
    Document:
    {text}
    
    Provide analysis in JSON format...
    """
    
    response = call_ollama(model, prompt, system_prompt, temperature=0.3)
    return json.loads(response)
```

## Best Practices

### Model Selection Strategy

1. **Development**: Use llama3.2 for fast iteration
2. **Testing**: Use mistral for quality checks
3. **Production**: Use llama3.1 or gemma2 for final analysis
4. **Batch**: Use llama3.2 for processing many documents

### Resource Management

1. **Monitor RAM**: Keep 4GB free for OS
2. **Monitor Disk**: Keep 20% free space
3. **Monitor CPU**: Don't run at 100% for extended periods
4. **Monitor Temp**: Ensure adequate cooling

### Maintenance

1. **Update Models**: `ollama pull <model>` periodically
2. **Clean Cache**: Remove unused models
3. **Monitor Logs**: Check for errors
4. **Backup Data**: Export important analyses

## Comparison: Ollama vs Cloud APIs

| Aspect | Ollama | OpenAI/Cloud |
|--------|--------|--------------|
| **Privacy** | 100% local | Data sent to cloud |
| **Cost** | Free (hardware) | Per-use fees |
| **Speed** | 1-3 min | 30-60 sec |
| **Quality** | Good-Excellent | Excellent |
| **Internet** | Not required | Required |
| **Setup** | Install + models | API key only |
| **Customization** | Full control | Limited |
| **Scaling** | Hardware limited | Nearly unlimited |

## Resources

### Official Documentation
- Ollama Website: https://ollama.ai
- Ollama GitHub: https://github.com/ollama/ollama
- Model Library: https://ollama.ai/library

### Community
- Ollama Discord: https://discord.gg/ollama
- GitHub Issues: https://github.com/ollama/ollama/issues
- Reddit: r/ollama

### Model Information
- Llama Models: https://ai.meta.com/llama/
- Mistral AI: https://mistral.ai/
- Gemma: https://ai.google.dev/gemma

## FAQ

**Q: How much disk space do I need?**
A: 5-10GB per model. Start with 20GB free space.

**Q: Can I run Ollama on a laptop?**
A: Yes! llama3.2 works well on modern laptops with 8GB+ RAM.

**Q: Do I need a GPU?**
A: No, but it significantly speeds up analysis. CPU-only works fine.

**Q: Can I use multiple models simultaneously?**
A: Yes, but each model uses RAM. Keep OLLAMA_MAX_LOADED_MODELS=1 for lower RAM systems.

**Q: How do I update Ollama?**
A: Reinstall from ollama.ai or use your package manager.

**Q: Can I use Ollama on a server?**
A: Yes! Set OLLAMA_HOST=0.0.0.0:11434 to allow network access.

**Q: Are models updated automatically?**
A: No. Run `ollama pull <model>` to update manually.

**Q: Can I create custom models?**
A: Yes! See Ollama documentation on creating Modelfiles.

---

**Need help?** Check the troubleshooting section or visit ollama.ai/docs

