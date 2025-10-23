"""
AI-powered sentiment and linguistic analysis engine using Ollama
Supports local LLM models for complete privacy and offline operation
"""

import json
import requests
from typing import Dict, List, Any, Optional

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api"


def get_available_models() -> List[str]:
    """
    Get list of available Ollama models
    
    Returns:
        List of model names
    """
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags")
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        return []
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []


def check_ollama_status() -> Dict[str, Any]:
    """
    Check if Ollama is running and available
    
    Returns:
        Dictionary with status information
    """
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags", timeout=2)
        if response.status_code == 200:
            models = [model["name"] for model in response.json().get("models", [])]
            return {
                "available": True,
                "models": models,
                "model_count": len(models)
            }
        return {"available": False, "error": "Ollama not responding"}
    except requests.exceptions.ConnectionError:
        return {"available": False, "error": "Cannot connect to Ollama. Is it running?"}
    except Exception as e:
        return {"available": False, "error": str(e)}


def call_ollama(
    model: str,
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.3,
    format: str = "json"
) -> str:
    """
    Call Ollama API with a prompt
    
    Args:
        model: Model name (e.g., "llama3.2", "mistral")
        prompt: User prompt
        system_prompt: System prompt (optional)
        temperature: Sampling temperature (0-1)
        format: Response format ("json" or "")
        
    Returns:
        Model response text
    """
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }
    
    if system_prompt:
        payload["system"] = system_prompt
    
    if format == "json":
        payload["format"] = "json"
    
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/generate",
            json=payload,
            timeout=120  # Longer timeout for local models
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    except Exception as e:
        raise Exception(f"Error calling Ollama: {str(e)}")


def analyze_document_content(
    text: str,
    model: str = "llama3.2"
) -> Dict[str, Any]:
    """
    Analyze overall document sentiment and metrics using Ollama
    
    Args:
        text: Full document text
        model: Ollama model to use
        
    Returns:
        Dictionary containing analysis results
    """
    
    system_prompt = """You are an expert in analyzing investor relations communications for sentiment, tone, and linguistic quality. 
You provide detailed analysis in valid JSON format only. Be precise and analytical."""
    
    prompt = f"""Analyze the following investor relations document and provide a comprehensive sentiment and linguistic analysis.

Document:
{text[:8000]}

Provide your analysis in the following JSON format (respond with ONLY valid JSON, no other text):
{{
    "overall_sentiment": "positive|negative|neutral|mixed",
    "sentiment_score": <0-100>,
    "confidence_score": <0-100>,
    "clarity_score": <0-100>,
    "readability_score": <0-100>,
    "specificity_score": <0-100>,
    "key_themes": ["theme1", "theme2", "theme3"],
    "emotional_tone": {{
        "positive": <0-100>,
        "negative": <0-100>,
        "neutral": <0-100>,
        "confident": <0-100>,
        "uncertain": <0-100>
    }},
    "linguistic_metrics": {{
        "avgSentenceLength": <float>,
        "complexWordRatio": <0-1>,
        "passiveVoiceRatio": <0-1>,
        "jargonDensity": <0-1>,
        "hedgingLanguage": <0-1>
    }}
}}

Scoring guidelines:
- Sentiment score: 0=very negative, 50=neutral, 100=very positive
- Confidence score: How assertive and certain the language is
- Clarity score: How easy to understand and unambiguous
- Readability score: Accessibility for general audience
- Specificity score: Use of concrete vs. vague language

Respond with ONLY the JSON object, no additional text."""
    
    try:
        response_text = call_ollama(model, prompt, system_prompt, temperature=0.3, format="json")
        
        # Parse JSON response
        result = json.loads(response_text)
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response was: {response_text[:500]}")
        # Return default values on parsing error
        return get_default_analysis()
    
    except Exception as e:
        print(f"Error in document analysis: {e}")
        return get_default_analysis()


def analyze_sections_content(
    text: str,
    model: str = "llama3.2"
) -> List[Dict[str, Any]]:
    """
    Analyze document section by section with suggestions using Ollama
    
    Args:
        text: Full document text
        model: Ollama model to use
        
    Returns:
        List of section analyses
    """
    
    system_prompt = """You are an expert editor specializing in investor relations communications. 
You provide actionable suggestions to improve clarity, confidence, and sentiment. 
You respond with valid JSON format only."""
    
    prompt = f"""Analyze the following investor relations document section by section. Break it into logical sections (e.g., Introduction, Financial Results, Outlook, Q&A) and provide detailed analysis for each.

Document:
{text[:8000]}

For each section, provide analysis in this JSON format (respond with ONLY valid JSON):
{{
    "sections": [
        {{
            "section_title": "Section name",
            "section_type": "introduction|financial_results|outlook|qa|other",
            "speaker": "Speaker name if applicable or null",
            "original_text": "First 500 chars of section text",
            "sentiment_score": <0-100>,
            "confidence_score": <0-100>,
            "clarity_score": <0-100>,
            "readability_score": <0-100>,
            "specificity_score": <0-100>,
            "issues": ["Issue 1", "Issue 2"],
            "suggested_revision": "Specific text revision suggestion",
            "revision_rationale": "Why this revision improves the text"
        }}
    ]
}}

Focus on identifying:
- Vague or hedging language that could be more specific
- Complex sentences that could be simplified
- Passive voice that could be active
- Negative framing that could be more positive
- Missing concrete data or metrics

Respond with ONLY the JSON object, no additional text."""
    
    try:
        response_text = call_ollama(model, prompt, system_prompt, temperature=0.3, format="json")
        
        # Parse JSON response
        result = json.loads(response_text)
        return result.get("sections", [])
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error in section analysis: {e}")
        print(f"Response was: {response_text[:500]}")
        return get_default_sections(text)
    
    except Exception as e:
        print(f"Error in section analysis: {e}")
        return get_default_sections(text)


def get_default_analysis() -> Dict[str, Any]:
    """Return default analysis values when analysis fails"""
    return {
        "overall_sentiment": "neutral",
        "sentiment_score": 50,
        "confidence_score": 50,
        "clarity_score": 50,
        "readability_score": 50,
        "specificity_score": 50,
        "key_themes": ["Analysis unavailable"],
        "emotional_tone": {
            "positive": 33,
            "negative": 33,
            "neutral": 34,
            "confident": 50,
            "uncertain": 50
        },
        "linguistic_metrics": {
            "avgSentenceLength": 20.0,
            "complexWordRatio": 0.3,
            "passiveVoiceRatio": 0.2,
            "jargonDensity": 0.25,
            "hedgingLanguage": 0.15
        }
    }


def get_default_sections(text: str) -> List[Dict[str, Any]]:
    """Return default section analysis when analysis fails"""
    return [{
        "section_title": "Full Document",
        "section_type": "other",
        "speaker": None,
        "original_text": text[:500],
        "sentiment_score": 50,
        "confidence_score": 50,
        "clarity_score": 50,
        "readability_score": 50,
        "specificity_score": 50,
        "issues": ["Analysis unavailable - check Ollama connection"],
        "suggested_revision": "Unable to generate suggestions. Please ensure Ollama is running and a model is available.",
        "revision_rationale": "Analysis requires a working Ollama installation with downloaded models."
    }]


def test_model(model: str) -> Dict[str, Any]:
    """
    Test if a model is working correctly
    
    Args:
        model: Model name to test
        
    Returns:
        Dictionary with test results
    """
    try:
        test_prompt = "Respond with a JSON object containing a single field 'status' with value 'ok'"
        response = call_ollama(model, test_prompt, format="json", temperature=0.1)
        
        # Try to parse as JSON
        json.loads(response)
        
        return {
            "success": True,
            "model": model,
            "message": "Model is working correctly"
        }
    
    except Exception as e:
        return {
            "success": False,
            "model": model,
            "error": str(e)
        }


# Recommended models for IR analysis
RECOMMENDED_MODELS = [
    {
        "name": "llama3.2",
        "size": "3B",
        "description": "Fast and efficient, good for quick analysis",
        "recommended": True
    },
    {
        "name": "llama3.1",
        "size": "8B",
        "description": "Balanced performance and quality",
        "recommended": True
    },
    {
        "name": "mistral",
        "size": "7B",
        "description": "Excellent for analytical tasks",
        "recommended": True
    },
    {
        "name": "phi3",
        "size": "3.8B",
        "description": "Compact and fast",
        "recommended": False
    },
    {
        "name": "gemma2",
        "size": "9B",
        "description": "High quality analysis",
        "recommended": False
    }
]


def get_model_recommendations() -> List[Dict[str, Any]]:
    """Get list of recommended models for IR analysis"""
    return RECOMMENDED_MODELS

