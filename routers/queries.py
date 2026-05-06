from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import re
import json
import os
from datetime import datetime
from utils.embedding import DocumentProcessor
from utils.language_model import LanguageModel
from utils.database import get_document, save_chat_message, get_chat_history as db_get_chat_history, clear_chat_history as db_clear_chat_history

router = APIRouter()

language_model = LanguageModel()

class QueryRequest(BaseModel):
    question: str = Field(..., description="Question about the document")
    max_tokens: int = Field(1000, description="Maximum response tokens")
    top_k: int = Field(4, description="Number of similar chunks to retrieve")
    save_to_history: bool = Field(True, description="Whether to save this interaction to chat history")

class QueryResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    chunks_used: Optional[int] = None
    has_table: bool = False
    table_data: Optional[List[Dict[str, Any]]] = None
    table_title: Optional[str] = None
    referenced_pages: Optional[List[int]] = None
    timestamp: str

class ChatHistoryEntry(BaseModel):
    role: str
    content: str
    timestamp: str
    has_table: Optional[bool] = False
    table_data: Optional[List[Dict[str, Any]]] = None
    table_title: Optional[str] = None
    referenced_pages: Optional[List[int]] = None

class ChatHistoryResponse(BaseModel):
    document_id: str
    history: List[ChatHistoryEntry]


def parse_markdown_table(markdown_text):
    """Parse markdown tables into structured data."""
    try:
        table_lines = markdown_text.strip().split('\n')
        header = [h.strip() for h in table_lines[0].strip('|').split('|')]
        rows = []
        for line in table_lines[2:]:
            row = [cell.strip() for cell in line.strip('|').split('|')]
            if len(row) == len(header):
                rows.append(dict(zip(header, row)))
        return rows if rows else None
    except Exception as e:
        return None

def is_schedule_request(message):
    schedule_keywords = [
        'schedule', 'table', 'tabular', 'fixture', 'equipment',
        'door schedule', 'window schedule', 'finish schedule', 'hardware schedule'
    ]
    return any(keyword in message.lower() for keyword in schedule_keywords)

def get_document_processor(document_id: str):
    doc_info = get_document(document_id)
    if not doc_info:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc_info["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Document status: {doc_info['status']}")

    json_path = doc_info.get("structured_json_path")
    if not json_path or not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Structured document data missing")

    try:
        return DocumentProcessor(json_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document loading error: {e}")

@router.post("/{document_id}/query", response_model=QueryResponse)
async def query_document(
    query: QueryRequest,
    document_id: str = Path(..., description="Document ID"),
):
    """
    Unified endpoint for querying documents and managing chat history.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save user question to history if requested
    if query.save_to_history:
        user_msg = {
            "role": "user", 
            "content": query.question, 
            "timestamp": timestamp,
            "has_table": False
        }
        save_chat_message(document_id, user_msg)
    
    # Process the query
    doc_processor = get_document_processor(document_id)
    similar_docs = doc_processor.search_similar_documents(query.question, k=query.top_k)

    answer_data = language_model.search_and_answer(
        query.question,
        similar_docs,
        max_tokens=query.max_tokens
    )

    # Extract referenced pages from metadata
    referenced_pages = list(set(
        int(doc.metadata.get("page_number", 0))
        for doc in similar_docs
        if "page_number" in doc.metadata
    ))

    has_table = is_schedule_request(query.question) and "|" in answer_data["answer"]
    table_data = parse_markdown_table(answer_data["answer"]) if has_table else None
    table_title = None

    if has_table:
        match = re.search(r"#+\s*(.*?(schedule|table))", answer_data["answer"], re.I)
        table_title = match.group(1).strip() if match else "Extracted Table"

    # Create response
    response = QueryResponse(
        document_id=document_id,
        question=query.question,
        answer=answer_data["answer"],
        input_tokens=answer_data.get("input_tokens"),
        output_tokens=answer_data.get("output_tokens"),
        chunks_used=len(similar_docs),
        has_table=has_table,
        table_data=table_data,
        table_title=table_title,
        referenced_pages=referenced_pages or None,
        timestamp=timestamp
    )
    
    # Save assistant response to history if requested
    if query.save_to_history:
        assistant_msg = {
            "role": "assistant",
            "content": answer_data["answer"],
            "timestamp": timestamp,
            "has_table": has_table,
            "table_data": table_data,
            "table_title": table_title,
            "referenced_pages": referenced_pages or None
        }
        save_chat_message(document_id, assistant_msg)

    return response

@router.get("/{document_id}/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(document_id: str = Path(..., description="Document ID")):
    """Get the complete chat history for a document"""
    if not get_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
        
    history = db_get_chat_history(document_id)
    return ChatHistoryResponse(document_id=document_id, history=history)

@router.delete("/{document_id}/chat/history")
async def clear_chat_history(document_id: str = Path(..., description="Document ID")):
    """Clear the chat history for a document"""
    if not get_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
        
    db_clear_chat_history(document_id)
    return {"message": "Chat history cleared successfully"}
