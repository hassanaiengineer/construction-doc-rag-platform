import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DB_PATH = "document_rag.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create documents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        document_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        status TEXT NOT NULL,
        progress INTEGER DEFAULT 0,
        message TEXT,
        file_path TEXT,
        structured_json_path TEXT,
        text_path TEXT,
        embeddings_path TEXT,
        pages INTEGER,
        chunks INTEGER,
        created_at INTEGER NOT NULL
    )
    ''')
    
    # Create chat history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        has_table BOOLEAN DEFAULT 0,
        table_data TEXT,
        table_title TEXT,
        referenced_pages TEXT,
        FOREIGN KEY (document_id) REFERENCES documents (document_id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

def save_document(doc_info: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO documents 
    (document_id, filename, original_filename, status, progress, message, 
     file_path, structured_json_path, text_path, embeddings_path, 
     pages, chunks, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        doc_info.get("document_id"),
        doc_info.get("filename"),
        doc_info.get("original_filename"),
        doc_info.get("status"),
        doc_info.get("progress", 0),
        doc_info.get("message"),
        doc_info.get("file_path"),
        doc_info.get("structured_json_path"),
        doc_info.get("text_path"),
        doc_info.get("embeddings_path"),
        doc_info.get("pages"),
        doc_info.get("chunks"),
        doc_info.get("created_at")
    ))
    
    conn.commit()
    conn.close()

def get_document(document_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM documents WHERE document_id = ?', (document_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_all_documents() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM documents ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def delete_document_db(document_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cascade delete is enabled, so this will also delete chat history
    cursor.execute('DELETE FROM documents WHERE document_id = ?', (document_id,))
    
    conn.commit()
    conn.close()

def update_document_status(document_id: str, updates: Dict[str, Any]):
    doc = get_document(document_id)
    if not doc:
        return
    
    doc.update(updates)
    save_document(doc)

def save_chat_message(document_id: str, message: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    table_data_str = json.dumps(message.get("table_data")) if message.get("table_data") else None
    ref_pages_str = json.dumps(message.get("referenced_pages")) if message.get("referenced_pages") else None
    
    cursor.execute('''
    INSERT INTO chat_history 
    (document_id, role, content, timestamp, has_table, table_data, table_title, referenced_pages)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        document_id,
        message.get("role"),
        message.get("content"),
        message.get("timestamp"),
        1 if message.get("has_table") else 0,
        table_data_str,
        message.get("table_title"),
        ref_pages_str
    ))
    
    conn.commit()
    conn.close()

def get_chat_history(document_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM chat_history WHERE document_id = ? ORDER BY id ASC', (document_id,))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        msg = dict(row)
        msg["has_table"] = bool(msg["has_table"])
        if msg["table_data"]:
            msg["table_data"] = json.loads(msg["table_data"])
        if msg["referenced_pages"]:
            msg["referenced_pages"] = json.loads(msg["referenced_pages"])
        history.append(msg)
        
    return history

def clear_chat_history(document_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_history WHERE document_id = ?', (document_id,))
    conn.commit()
    conn.close()
