"""
Document text extraction utilities
Supports PDF, TXT, DOC, and DOCX files
"""

import os
from pathlib import Path
from typing import Optional

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    if not PDF_AVAILABLE:
        raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")
    
    text = []
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text.append(page.extract_text())
    
    return '\n\n'.join(text)


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx not installed. Install with: pip install python-docx")
    
    doc = Document(file_path)
    text = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)
    
    return '\n\n'.join(text)


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from various file formats
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: If file format is not supported
    """
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext in ['.txt', '.text']:
        return extract_text_from_txt(file_path)
    elif ext == '.doc':
        # For .doc files, try to read as text (limited support)
        # For full support, consider using textract or antiword
        try:
            return extract_text_from_txt(file_path)
        except:
            raise ValueError(f"Unable to extract text from {ext} file. Consider converting to .docx format.")
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def validate_file_size(file_path: str, max_size_mb: int = 10) -> bool:
    """
    Validate file size
    
    Args:
        file_path: Path to the file
        max_size_mb: Maximum file size in MB
        
    Returns:
        True if file size is acceptable
    """
    file_size = os.path.getsize(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def get_file_info(file_path: str) -> dict:
    """
    Get file metadata
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    path = Path(file_path)
    stat = path.stat()
    
    return {
        "name": path.name,
        "extension": path.suffix,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "created": stat.st_ctime,
        "modified": stat.st_mtime
    }

