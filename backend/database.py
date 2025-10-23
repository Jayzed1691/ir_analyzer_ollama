"""
Database module using SQLite for local storage
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

DB_PATH = "data/ir_analyzer.db"


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with schema"""
    Path("data").mkdir(exist_ok=True)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            document_type TEXT NOT NULL,
            file_path TEXT,
            status TEXT DEFAULT 'uploading',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Analyses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            overall_sentiment TEXT,
            sentiment_score INTEGER,
            confidence_score INTEGER,
            clarity_score INTEGER,
            readability_score INTEGER,
            specificity_score INTEGER,
            key_themes TEXT,
            emotional_tone TEXT,
            linguistic_metrics TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    """)
    
    # Sections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER NOT NULL,
            section_title TEXT NOT NULL,
            section_type TEXT,
            speaker TEXT,
            original_text TEXT NOT NULL,
            sentiment_score INTEGER,
            confidence_score INTEGER,
            clarity_score INTEGER,
            readability_score INTEGER,
            specificity_score INTEGER,
            issues TEXT,
            suggested_revision TEXT,
            revision_rationale TEXT,
            section_order INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        )
    """)
    
    # Comparisons table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            document_ids TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Metrics history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            analysis_id INTEGER NOT NULL,
            document_type TEXT NOT NULL,
            sentiment_score INTEGER,
            confidence_score INTEGER,
            clarity_score INTEGER,
            readability_score INTEGER,
            specificity_score INTEGER,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id),
            FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        )
    """)
    
    conn.commit()
    conn.close()


# Document operations
def create_document(conn, title: str, document_type: str, file_path: str) -> int:
    """Create a new document"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (title, document_type, file_path, status) VALUES (?, ?, ?, ?)",
        (title, document_type, file_path, "uploading")
    )
    conn.commit()
    return cursor.lastrowid


def get_document(conn, document_id: int) -> Optional[Dict]:
    """Get document by ID"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_all_documents(conn) -> List[Dict]:
    """Get all documents"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY created_at DESC")
    return [dict(row) for row in cursor.fetchall()]


def update_document_status(conn, document_id: int, status: str):
    """Update document status"""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE documents SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, document_id)
    )
    conn.commit()


# Analysis operations
def create_analysis(
    conn,
    document_id: int,
    overall_sentiment: str,
    sentiment_score: int,
    confidence_score: int,
    clarity_score: int,
    readability_score: int,
    specificity_score: int,
    key_themes: List[str],
    emotional_tone: Dict[str, int],
    linguistic_metrics: Dict[str, float]
) -> int:
    """Create analysis record"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analyses (
            document_id, overall_sentiment, sentiment_score, confidence_score,
            clarity_score, readability_score, specificity_score,
            key_themes, emotional_tone, linguistic_metrics
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        document_id, overall_sentiment, sentiment_score, confidence_score,
        clarity_score, readability_score, specificity_score,
        json.dumps(key_themes), json.dumps(emotional_tone), json.dumps(linguistic_metrics)
    ))
    conn.commit()
    return cursor.lastrowid


def get_analysis_by_document_id(conn, document_id: int) -> Optional[Dict]:
    """Get analysis for a document"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE document_id = ?", (document_id,))
    row = cursor.fetchone()
    if not row:
        return None
    
    analysis = dict(row)
    # Parse JSON fields
    analysis["key_themes"] = json.loads(analysis["key_themes"])
    analysis["emotional_tone"] = json.loads(analysis["emotional_tone"])
    analysis["linguistic_metrics"] = json.loads(analysis["linguistic_metrics"])
    return analysis


# Section operations
def create_section(
    conn,
    analysis_id: int,
    section_title: str,
    section_type: Optional[str],
    speaker: Optional[str],
    original_text: str,
    sentiment_score: int,
    confidence_score: int,
    clarity_score: int,
    readability_score: int,
    specificity_score: int,
    issues: List[str],
    suggested_revision: str,
    revision_rationale: str,
    order: int
) -> int:
    """Create section record"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sections (
            analysis_id, section_title, section_type, speaker, original_text,
            sentiment_score, confidence_score, clarity_score, readability_score,
            specificity_score, issues, suggested_revision, revision_rationale, section_order
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        analysis_id, section_title, section_type, speaker, original_text,
        sentiment_score, confidence_score, clarity_score, readability_score,
        specificity_score, json.dumps(issues), suggested_revision, revision_rationale, order
    ))
    conn.commit()
    return cursor.lastrowid


def get_sections_by_analysis_id(conn, analysis_id: int) -> List[Dict]:
    """Get all sections for an analysis"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM sections WHERE analysis_id = ? ORDER BY section_order",
        (analysis_id,)
    )
    sections = []
    for row in cursor.fetchall():
        section = dict(row)
        section["issues"] = json.loads(section["issues"])
        sections.append(section)
    return sections


# Comparison operations
def create_comparison(
    conn,
    title: str,
    description: Optional[str],
    document_ids: List[int]
) -> int:
    """Create comparison record"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comparisons (title, description, document_ids) VALUES (?, ?, ?)",
        (title, description, json.dumps(document_ids))
    )
    conn.commit()
    return cursor.lastrowid


def get_comparison(conn, comparison_id: int) -> Optional[Dict]:
    """Get comparison by ID"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comparisons WHERE id = ?", (comparison_id,))
    row = cursor.fetchone()
    if not row:
        return None
    
    comp = dict(row)
    comp["document_ids"] = json.loads(comp["document_ids"])
    return comp


def get_all_comparisons(conn) -> List[Dict]:
    """Get all comparisons"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comparisons ORDER BY created_at DESC")
    comparisons = []
    for row in cursor.fetchall():
        comp = dict(row)
        comp["document_ids"] = json.loads(comp["document_ids"])
        comparisons.append(comp)
    return comparisons


def delete_comparison(conn, comparison_id: int) -> bool:
    """Delete comparison"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM comparisons WHERE id = ?", (comparison_id,))
    conn.commit()
    return cursor.rowcount > 0


# Metrics operations
def create_metrics(
    conn,
    document_id: int,
    analysis_id: int,
    document_type: str,
    sentiment_score: int,
    confidence_score: int,
    clarity_score: int,
    readability_score: int,
    specificity_score: int
) -> int:
    """Create metrics history record"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO metrics_history (
            document_id, analysis_id, document_type,
            sentiment_score, confidence_score, clarity_score,
            readability_score, specificity_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        document_id, analysis_id, document_type,
        sentiment_score, confidence_score, clarity_score,
        readability_score, specificity_score
    ))
    conn.commit()
    return cursor.lastrowid


def get_metrics_history(conn, limit: int = 50) -> List[Dict]:
    """Get metrics history"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM metrics_history ORDER BY recorded_at DESC LIMIT ?",
        (limit,)
    )
    return [dict(row) for row in cursor.fetchall()]


def get_metrics_by_type(conn, document_type: str) -> List[Dict]:
    """Get metrics filtered by document type"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM metrics_history WHERE document_type = ? ORDER BY recorded_at DESC",
        (document_type,)
    )
    return [dict(row) for row in cursor.fetchall()]

