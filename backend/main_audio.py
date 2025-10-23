"""
Extended FastAPI Backend with Audio Transcription Support
Add these endpoints to your main.py file
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import Optional
import os
from pathlib import Path
from datetime import datetime

from audio_processor import (
    transcribe_audio_file,
    validate_audio_file,
    get_audio_duration,
    get_transcription_presets,
    WHISPER_AVAILABLE
)


# Add these endpoints to your existing FastAPI app

@app.get("/api/audio/status")
async def get_audio_status():
    """Check audio transcription availability"""
    return {
        "whisper_local_available": WHISPER_AVAILABLE,
        "presets": get_transcription_presets()
    }


@app.post("/api/audio/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form(default="en"),
    preset: str = Form(default="balanced"),
    detect_speakers: bool = Form(default=True)
):
    """
    Transcribe audio file to text
    
    This is a standalone endpoint for testing transcription
    """
    # Validate file type
    allowed_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm', '.mp4']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save file
    file_path = f"data/uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Get preset settings
        presets = get_transcription_presets()
        preset_config = presets.get(preset, presets["balanced"])
        
        # Transcribe
        result = transcribe_audio_file(
            audio_path=file_path,
            backend=preset_config["backend"],
            language=language,
            model_size=preset_config["model_size"],
            detect_speakers=detect_speakers
        )
        
        return {
            "success": True,
            "text": result["text"],
            "formatted_text": result.get("formatted_text", result["text"]),
            "language": result["language"],
            "duration": result["duration"],
            "segments": len(result.get("segments", [])),
            "backend": result["backend"],
            "model": result["model"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Optionally clean up audio file
        # os.remove(file_path)
        pass


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
    """
    Upload audio file, transcribe, and analyze
    
    This combines transcription + analysis in one endpoint
    """
    from database import (
        get_db, create_document, update_document_status,
        create_analysis, create_section, create_metrics
    )
    from analysis_engine import analyze_document_content, analyze_sections_content
    
    # Validate document type
    valid_types = ["press_release", "earnings_call", "corporate_release", "other"]
    if document_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid document type")
    
    # Validate file type
    allowed_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm', '.mp4']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Audio file type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save file
    file_path = f"data/uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create document record
    db = get_db()
    doc_id = create_document(db, title, document_type, file_path)
    
    try:
        # Update status to transcribing
        update_document_status(db, doc_id, "transcribing")
        
        # Get preset settings
        presets = get_transcription_presets()
        preset_config = presets.get(transcription_preset, presets["balanced"])
        
        # Transcribe audio
        transcription_result = transcribe_audio_file(
            audio_path=file_path,
            backend=preset_config["backend"],
            language=language,
            model_size=preset_config["model_size"],
            detect_speakers=detect_speakers
        )
        
        text_content = transcription_result.get("formatted_text", transcription_result["text"])
        
        # Save transcript to file
        transcript_path = file_path + ".transcript.txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        
        # Update status to analyzing
        update_document_status(db, doc_id, "analyzing")
        
        # Perform sentiment analysis
        analysis_result = analyze_document_content(text_content, model=analysis_model)
        
        # Save analysis
        analysis_id = create_analysis(
            db,
            document_id=doc_id,
            overall_sentiment=analysis_result["overall_sentiment"],
            sentiment_score=analysis_result["sentiment_score"],
            confidence_score=analysis_result["confidence_score"],
            clarity_score=analysis_result["clarity_score"],
            readability_score=analysis_result["readability_score"],
            specificity_score=analysis_result["specificity_score"],
            key_themes=analysis_result["key_themes"],
            emotional_tone=analysis_result["emotional_tone"],
            linguistic_metrics=analysis_result["linguistic_metrics"]
        )
        
        # Analyze sections
        sections_result = analyze_sections_content(text_content, model=analysis_model)
        for idx, section in enumerate(sections_result):
            create_section(
                db,
                analysis_id=analysis_id,
                section_title=section["section_title"],
                section_type=section.get("section_type"),
                speaker=section.get("speaker"),
                original_text=section["original_text"],
                sentiment_score=section["sentiment_score"],
                confidence_score=section["confidence_score"],
                clarity_score=section["clarity_score"],
                readability_score=section["readability_score"],
                specificity_score=section["specificity_score"],
                issues=section["issues"],
                suggested_revision=section["suggested_revision"],
                revision_rationale=section["revision_rationale"],
                order=idx
            )
        
        # Create metrics history
        create_metrics(
            db,
            document_id=doc_id,
            analysis_id=analysis_id,
            document_type=document_type,
            sentiment_score=analysis_result["sentiment_score"],
            confidence_score=analysis_result["confidence_score"],
            clarity_score=analysis_result["clarity_score"],
            readability_score=analysis_result["readability_score"],
            specificity_score=analysis_result["specificity_score"]
        )
        
        # Update status to completed
        update_document_status(db, doc_id, "completed")
        
        return {
            "success": True,
            "document_id": doc_id,
            "transcription": {
                "duration": transcription_result["duration"],
                "language": transcription_result["language"],
                "segments": len(transcription_result.get("segments", [])),
                "backend": transcription_result["backend"]
            },
            "analysis": {
                "sentiment_score": analysis_result["sentiment_score"],
                "confidence_score": analysis_result["confidence_score"],
                "clarity_score": analysis_result["clarity_score"]
            }
        }
    
    except Exception as e:
        update_document_status(db, doc_id, "failed")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# Instructions for integrating into main.py:
# 1. Copy audio_processor.py to backend/
# 2. Add these endpoints to main.py
# 3. Install dependencies: pip install openai-whisper pydub
# 4. For audio format conversion, also install ffmpeg:
#    - macOS: brew install ffmpeg
#    - Linux: apt install ffmpeg
#    - Windows: Download from ffmpeg.org

