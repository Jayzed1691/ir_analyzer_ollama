"""
FastAPI Backend for IR Sentiment Analyzer with Ollama Integration
Provides REST API endpoints for document analysis using local LLM models
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import os
from pathlib import Path

from database import (
    init_db, get_db,
    create_document, get_document, get_all_documents, update_document_status,
    create_analysis, get_analysis_by_document_id,
    create_section, get_sections_by_analysis_id,
    create_comparison, get_comparison, get_all_comparisons, delete_comparison,
    create_metrics, get_metrics_history, get_metrics_by_type
)
from analysis_engine import (
    analyze_document_content, analyze_sections_content,
    get_available_models, check_ollama_status, test_model,
    get_model_recommendations
)
from document_processor import extract_text_from_file

app = FastAPI(
    title="IR Sentiment Analyzer API (Ollama)",
    description="API for analyzing investor relations documents using local Ollama models",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class DocumentCreate(BaseModel):
    title: str
    document_type: str = Field(..., pattern="^(press_release|earnings_call|corporate_release|other)$")
    model: Optional[str] = "llama3.2"

class DocumentResponse(BaseModel):
    id: int
    title: str
    document_type: str
    file_path: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

class AnalysisResponse(BaseModel):
    id: int
    document_id: int
    overall_sentiment: str
    sentiment_score: int
    confidence_score: int
    clarity_score: int
    readability_score: int
    specificity_score: int
    key_themes: List[str]
    emotional_tone: Dict[str, int]
    linguistic_metrics: Dict[str, float]
    created_at: datetime

class SectionResponse(BaseModel):
    id: int
    analysis_id: int
    section_title: str
    section_type: Optional[str]
    speaker: Optional[str]
    original_text: str
    sentiment_score: int
    confidence_score: int
    clarity_score: int
    readability_score: int
    specificity_score: int
    issues: List[str]
    suggested_revision: str
    revision_rationale: str
    order: int

class ComparisonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    document_ids: List[int]

class ComparisonResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    document_ids: List[int]
    created_at: datetime

class MetricsResponse(BaseModel):
    id: int
    document_id: int
    document_type: str
    sentiment_score: int
    confidence_score: int
    clarity_score: int
    readability_score: int
    specificity_score: int
    recorded_at: datetime

class ModelTestRequest(BaseModel):
    model: str


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    # Create data directory if it doesn't exist
    Path("data/uploads").mkdir(parents=True, exist_ok=True)
    
    # Check Ollama status
    status = check_ollama_status()
    if status["available"]:
        print(f"✓ Ollama is running with {status['model_count']} models available")
        print(f"  Models: {', '.join(status['models'][:5])}")
    else:
        print(f"⚠ Ollama not available: {status.get('error', 'Unknown error')}")
        print("  Please ensure Ollama is installed and running: https://ollama.ai")


# Health check
@app.get("/health")
async def health_check():
    ollama_status = check_ollama_status()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ollama": ollama_status
    }


# Ollama-specific endpoints
@app.get("/api/ollama/status")
async def get_ollama_status():
    """Get Ollama status and available models"""
    return check_ollama_status()


@app.get("/api/ollama/models")
async def list_models():
    """List all available Ollama models"""
    models = get_available_models()
    recommendations = get_model_recommendations()
    
    return {
        "installed": models,
        "recommended": recommendations,
        "count": len(models)
    }


@app.post("/api/ollama/test-model")
async def test_ollama_model(request: ModelTestRequest):
    """Test if a specific model is working"""
    result = test_model(request.model)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Model test failed"))
    return result


# Document endpoints
@app.post("/api/documents", response_model=DocumentResponse)
async def upload_document(
    title: str = Form(...),
    document_type: str = Form(...),
    model: str = Form(default="llama3.2"),
    file: UploadFile = File(...)
):
    """Upload a document for analysis with specified Ollama model"""
    
    # Validate document type
    valid_types = ["press_release", "earnings_call", "corporate_release", "other"]
    if document_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid document type")
    
    # Validate file type
    allowed_extensions = ['.pdf', '.txt', '.doc', '.docx']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Check Ollama status
    ollama_status = check_ollama_status()
    if not ollama_status["available"]:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama not available: {ollama_status.get('error', 'Unknown error')}"
        )
    
    # Verify model exists
    available_models = get_available_models()
    if model not in available_models:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model}' not found. Available models: {', '.join(available_models)}"
        )
    
    # Save file
    file_path = f"data/uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create document record
    db = get_db()
    doc_id = create_document(db, title, document_type, file_path)
    
    # Extract text and analyze asynchronously
    try:
        # Extract text
        text_content = extract_text_from_file(file_path)
        
        # Update status to processing
        update_document_status(db, doc_id, "processing")
        
        # Perform analysis with specified model
        analysis_result = analyze_document_content(text_content, model=model)
        
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
        
        # Analyze sections with specified model
        sections_result = analyze_sections_content(text_content, model=model)
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
        
    except Exception as e:
        update_document_status(db, doc_id, "failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    # Return document
    doc = get_document(db, doc_id)
    return doc


@app.get("/api/documents", response_model=List[DocumentResponse])
async def list_documents():
    """List all documents"""
    db = get_db()
    return get_all_documents(db)


@app.get("/api/documents/{document_id}", response_model=DocumentResponse)
async def get_document_by_id(document_id: int):
    """Get a specific document"""
    db = get_db()
    doc = get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@app.get("/api/documents/{document_id}/analysis")
async def get_document_analysis(document_id: int):
    """Get analysis for a document"""
    db = get_db()
    
    # Get document
    doc = get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get analysis
    analysis = get_analysis_by_document_id(db, document_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get sections
    sections = get_sections_by_analysis_id(db, analysis["id"])
    
    return {
        "analysis": analysis,
        "sections": sections
    }


# Comparison endpoints
@app.post("/api/comparisons", response_model=ComparisonResponse)
async def create_document_comparison(comparison: ComparisonCreate):
    """Create a new document comparison"""
    if len(comparison.document_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 documents required for comparison")
    
    db = get_db()
    
    # Verify all documents exist
    for doc_id in comparison.document_ids:
        doc = get_document(db, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    
    comp_id = create_comparison(
        db,
        title=comparison.title,
        description=comparison.description,
        document_ids=comparison.document_ids
    )
    
    comp = get_comparison(db, comp_id)
    return comp


@app.get("/api/comparisons", response_model=List[ComparisonResponse])
async def list_comparisons():
    """List all comparisons"""
    db = get_db()
    return get_all_comparisons(db)


@app.get("/api/comparisons/{comparison_id}")
async def get_comparison_detail(comparison_id: int):
    """Get comparison with full document and analysis data"""
    db = get_db()
    
    comp = get_comparison(db, comparison_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    # Get documents and their analyses
    documents = []
    for doc_id in comp["document_ids"]:
        doc = get_document(db, doc_id)
        if doc:
            analysis = get_analysis_by_document_id(db, doc_id)
            documents.append({
                "document": doc,
                "analysis": analysis
            })
    
    return {
        "comparison": comp,
        "documents": documents
    }


@app.delete("/api/comparisons/{comparison_id}")
async def delete_document_comparison(comparison_id: int):
    """Delete a comparison"""
    db = get_db()
    success = delete_comparison(db, comparison_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return {"success": True}


# Metrics endpoints
@app.get("/api/metrics/history", response_model=List[MetricsResponse])
async def get_metrics_history_endpoint(limit: int = 50):
    """Get historical metrics"""
    db = get_db()
    return get_metrics_history(db, limit)


@app.get("/api/metrics/by-type/{document_type}", response_model=List[MetricsResponse])
async def get_metrics_by_type_endpoint(document_type: str):
    """Get metrics filtered by document type"""
    db = get_db()
    return get_metrics_by_type(db, document_type)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

