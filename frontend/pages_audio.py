"""
Add this page to your Streamlit app for audio upload
Save as: frontend/pages/audio_upload.py or integrate into app.py
"""

import streamlit as st
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def render_audio_upload_page():
    """Render the audio upload page"""
    
    st.markdown('<div class="main-header">Upload Audio</div>', unsafe_allow_html=True)
    st.markdown("Upload earnings call recordings for automatic transcription and analysis")
    
    # Check audio transcription status
    try:
        response = requests.get(f"{API_BASE_URL}/api/audio/status")
        if response.status_code == 200:
            audio_status = response.json()
            whisper_available = audio_status.get("whisper_local_available", False)
            presets = audio_status.get("presets", {})
        else:
            whisper_available = False
            presets = {}
    except:
        st.error("Unable to connect to backend API")
        whisper_available = False
        presets = {}
    
    if not whisper_available:
        st.warning("⚠️ Audio transcription not available. Install Whisper to enable this feature.")
        st.info("Run: `pip install openai-whisper` and restart the backend")
        
        with st.expander("📖 Installation Instructions"):
            st.markdown("""
            ### Install Whisper for Audio Transcription
            
            **Option 1: Local Whisper (Recommended)**
            ```bash
            pip install openai-whisper
            ```
            
            **Option 2: OpenAI API**
            ```bash
            pip install openai
            export OPENAI_API_KEY="your-key-here"
            ```
            
            **Also install FFmpeg for audio processing:**
            - macOS: `brew install ffmpeg`
            - Linux: `apt install ffmpeg`
            - Windows: Download from ffmpeg.org
            
            After installation, restart the backend server.
            """)
        return
    
    # Audio upload form
    st.success("✓ Audio transcription available")
    
    with st.form("audio_upload_form"):
        title = st.text_input("Document Title", placeholder="Q4 2024 Earnings Call")
        
        document_type = st.selectbox(
            "Document Type",
            ["earnings_call", "press_release", "corporate_release", "other"],
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Transcription Settings")
            
            # Transcription preset
            preset_options = list(presets.keys()) if presets else ["balanced"]
            preset = st.selectbox(
                "Transcription Quality",
                preset_options,
                help="Choose transcription quality vs speed tradeoff"
            )
            
            if presets and preset in presets:
                st.caption(f"ℹ️ {presets[preset].get('description', '')}")
            
            language = st.selectbox(
                "Audio Language",
                ["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"],
                format_func=lambda x: {
                    "en": "English",
                    "es": "Spanish",
                    "fr": "French",
                    "de": "German",
                    "it": "Italian",
                    "pt": "Portuguese",
                    "zh": "Chinese",
                    "ja": "Japanese",
                    "ko": "Korean"
                }.get(x, x)
            )
            
            detect_speakers = st.checkbox(
                "Detect Speakers",
                value=True,
                help="Attempt to identify different speakers in the audio"
            )
        
        with col2:
            st.subheader("Analysis Settings")
            
            # Get available Ollama models
            try:
                response = requests.get(f"{API_BASE_URL}/api/ollama/models")
                if response.status_code == 200:
                    models_data = response.json()
                    installed_models = models_data.get("installed", [])
                else:
                    installed_models = []
            except:
                installed_models = []
            
            if not installed_models:
                st.warning("No Ollama models available")
                analysis_model = "llama3.2"
            else:
                analysis_model = st.selectbox(
                    "Analysis Model",
                    installed_models,
                    help="Select Ollama model for sentiment analysis"
                )
        
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'wav', 'm4a', 'ogg', 'flac', 'webm', 'mp4'],
            help="Supported formats: MP3, WAV, M4A, OGG, FLAC, WebM, MP4"
        )
        
        # File size warning
        if uploaded_file:
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.info(f"File size: {file_size_mb:.1f} MB")
            
            if file_size_mb > 100:
                st.error("⚠️ File too large. Maximum size: 100 MB")
            
            # Estimate processing time
            estimated_minutes = file_size_mb * 0.5  # Rough estimate
            st.caption(f"⏱️ Estimated processing time: {estimated_minutes:.0f}-{estimated_minutes*2:.0f} minutes")
        
        submit = st.form_submit_button("Upload and Analyze", use_container_width=True)
        
        if submit:
            if not title:
                st.error("Please enter a document title")
            elif not uploaded_file:
                st.error("Please select an audio file")
            elif not analysis_model:
                st.error("Please select an analysis model")
            else:
                # Show progress
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                try:
                    progress_text.text("Uploading audio file...")
                    progress_bar.progress(10)
                    
                    files = {"file": uploaded_file}
                    data = {
                        "title": title,
                        "document_type": document_type,
                        "analysis_model": analysis_model,
                        "transcription_preset": preset,
                        "language": language,
                        "detect_speakers": str(detect_speakers).lower()
                    }
                    
                    progress_text.text("Transcribing audio... This may take several minutes.")
                    progress_bar.progress(30)
                    
                    response = requests.post(
                        f"{API_BASE_URL}/api/documents/audio",
                        files=files,
                        data=data,
                        timeout=1800  # 30 minute timeout for long audio
                    )
                    
                    progress_bar.progress(90)
                    
                    if response.status_code == 200:
                        result = response.json()
                        progress_bar.progress(100)
                        progress_text.empty()
                        
                        st.success("✅ Audio transcribed and analyzed successfully!")
                        st.balloons()
                        
                        # Show results summary
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Transcription")
                            trans = result.get("transcription", {})
                            st.metric("Duration", f"{trans.get('duration', 0)/60:.1f} min")
                            st.metric("Language", trans.get('language', 'Unknown'))
                            st.metric("Segments", trans.get('segments', 0))
                            st.caption(f"Backend: {trans.get('backend', 'Unknown')}")
                        
                        with col2:
                            st.subheader("Analysis")
                            analysis = result.get("analysis", {})
                            st.metric("Sentiment", f"{analysis.get('sentiment_score', 0)}/100")
                            st.metric("Confidence", f"{analysis.get('confidence_score', 0)}/100")
                            st.metric("Clarity", f"{analysis.get('clarity_score', 0)}/100")
                        
                        st.info(f"Document ID: {result.get('document_id')}")
                        st.info("View full analysis in the 'Document Analysis' page")
                    
                    else:
                        error_detail = response.json().get('detail', 'Unknown error')
                        st.error(f"Processing failed: {error_detail}")
                        progress_text.empty()
                        progress_bar.empty()
                
                except requests.exceptions.Timeout:
                    st.error("Processing timed out. The audio file may be too long. Try a shorter file or split it into segments.")
                    progress_text.empty()
                    progress_bar.empty()
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    progress_text.empty()
                    progress_bar.empty()
    
    # Information section
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Supported Formats")
        st.markdown("""
        - **MP3** - Most common format
        - **WAV** - Uncompressed audio
        - **M4A** - Apple audio format
        - **OGG** - Open format
        - **FLAC** - Lossless compression
        - **WebM** - Web format
        - **MP4** - Video with audio
        """)
    
    with col2:
        st.subheader("⚙️ Transcription Presets")
        
        if presets:
            for preset_name, preset_info in presets.items():
                st.markdown(f"**{preset_name.title()}**: {preset_info.get('description', '')}")
        else:
            st.markdown("""
            - **Fast**: Quick transcription, lower accuracy
            - **Balanced**: Good speed and accuracy
            - **Accurate**: Better accuracy, slower
            - **High Quality**: Best accuracy, requires GPU
            - **API**: OpenAI Whisper API (requires key)
            """)
    
    st.markdown("---")
    
    with st.expander("💡 Tips for Best Results"):
        st.markdown("""
        ### Audio Quality
        - Use clear, high-quality recordings
        - Minimize background noise
        - Ensure speakers are audible
        
        ### File Preparation
        - Convert to MP3 or WAV for best compatibility
        - Split very long recordings (>1 hour) into segments
        - Keep file size under 100 MB
        
        ### Transcription Settings
        - Select correct language for better accuracy
        - Use "Balanced" preset for most cases
        - Enable speaker detection for multi-speaker calls
        
        ### Processing Time
        - Transcription takes ~10-30% of audio duration
        - Analysis adds 1-3 minutes
        - Total: 5-10 minutes for a 30-minute call
        """)


# Integration instructions:
# 
# Option 1: Add to existing app.py
# Add this to your page selection:
#   elif page == "Upload Audio":
#       render_audio_upload_page()
#
# Option 2: Create separate page file
# Save as: frontend/pages/audio_upload.py
# Streamlit will automatically add it to the sidebar

