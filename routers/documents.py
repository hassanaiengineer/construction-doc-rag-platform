from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import json
import time
import uuid
import shutil
from pydantic import BaseModel
from utils.ocr import OCRProcessor
from utils.embedding import DocumentProcessor
import logging

router = APIRouter()

# Initialize the OCR processor
ocr_processor = OCRProcessor()

# In-memory storage for document metadata
# In production, you might want to use a database
document_store = {}

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    pages: Optional[int] = None
    chunks: Optional[int] = None
    embeddings_path: Optional[str] = None
    created_at: float


class DocumentsListResponse(BaseModel):
    documents: List[DocumentResponse]


class ProcessingStatus(BaseModel):
    document_id: str
    status: str
    progress: float
    message: str


# Background processing task
def process_document(document_id: str, file_path: str):
    try:
        # Update status to processing
        document_store[document_id].update(
            status="processing",
            progress=10,
            message="Running OCR on document..."
        )
        
        # Check if we already have the document processed
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        json_path = os.path.join("Structured Text", f"{base_filename}.json")
        txt_path = os.path.join("Sample Text", f"{base_filename}.txt")
        
        # Process PDF with OCR only if not already processed
        if not (os.path.exists(json_path) and os.path.exists(txt_path)):
            json_path, txt_path = ocr_processor.process_pdf(file_path)
        else:
            logger.info(f"Document {base_filename} already processed, reusing existing files")
            
        document_store[document_id].update(
            progress=50,
            structured_json_path=json_path,
            text_path=txt_path,
            message="OCR completed. Creating embeddings..."
        )

        # Check if embeddings already exist
        embeddings_folder = os.path.join("Embeddings", base_filename)
        if os.path.exists(embeddings_folder):
            logger.info(f"Embeddings already exist for {base_filename}, reusing them")
            document_store[document_id].update(
                embeddings_path=embeddings_folder
            )
        else:
            # Create document embeddings
            doc_processor = DocumentProcessor(json_path)
            docs, index = doc_processor.create_faiss_index()
            document_store[document_id].update(
                embeddings_path=doc_processor.index_path
            )
        
        # Update document metadata
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            total_pages = len(json_data.keys())
        
        # Final updates
        document_store[document_id].update(
            pages=total_pages,
            chunks=len(docs) if 'docs' in locals() else None,  # Use docs if available
            status="completed",
            progress=100,
            message="Document processed successfully"
        )
        
        logger.info(f"Document {document_id} processed successfully with {total_pages} pages.")
        
    except Exception as e:
        # Handle any errors and update the status to failed
        logger.error(f"Error processing document {document_id}: {str(e)}")
        document_store[document_id].update(
            status="failed",
            message=f"Error processing document: {str(e)}"
        )


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a PDF document for processing"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate a unique document ID
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time())
    document_id = f"{timestamp}_{unique_id}"
    
    # Create uploads directory if it doesn't exist
    os.makedirs("Uploads", exist_ok=True)
    
    # Normalize filename to avoid duplicates
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join("Uploads", safe_filename)
    
    # Save uploaded file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Check if this file has been uploaded before
    existing_document = None
    for doc_id, info in document_store.items():
        if info.get("original_filename") == file.filename:
            existing_document = doc_id
            break
    
    if existing_document:
        logger.info(f"Document {file.filename} was previously uploaded as {existing_document}")
    
    # Store document metadata
    document_store[document_id] = {
        "document_id": document_id,
        "filename": file.filename,  # Store original filename for display
        "original_filename": file.filename,  # Keep original filename for duplicate detection
        "status": "pending",
        "progress": 0,
        "message": "Document uploaded, waiting for processing",
        "file_path": file_path,
        "created_at": timestamp
    }

    # Log background task start
    logger.info(f"Background task started for document {document_id} (File: {file.filename})")
    
    # Start background processing
    background_tasks.add_task(process_document, document_id, file_path)
    
    return DocumentResponse(
        document_id=document_id,
        filename=file.filename,
        status="pending",
        created_at=timestamp
    )


@router.get("/list", response_model=DocumentsListResponse)
async def list_documents():
    """List all processed documents"""
    documents = [
        DocumentResponse(
            document_id=doc_id,
            filename=info["filename"],
            status=info["status"],
            pages=info.get("pages"),
            chunks=info.get("chunks"),
            embeddings_path=info.get("embeddings_path"),
            created_at=info["created_at"]
        )
        for doc_id, info in sorted(
            document_store.items(), 
            key=lambda item: item[1]["created_at"], 
            reverse=True
        )
    ]
    
    return DocumentsListResponse(documents=documents)


@router.get("/{document_id}/status", response_model=ProcessingStatus)
async def get_document_status(document_id: str = Path(..., description="The ID of the document")):
    """Get the processing status of a document"""
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    info = document_store[document_id]
    
    return ProcessingStatus(
        document_id=document_id,
        status=info["status"],
        progress=info.get("progress", 0),
        message=info.get("message", "")
    )


@router.get("/{document_id}/preview")
async def get_document_preview(
    document_id: str = Path(..., description="The ID of the document"),
    max_length: int = Query(500, description="Maximum length of the preview text")
):
    """Get a text preview of the processed document"""
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    info = document_store[document_id]
    
    if info["status"] != "completed":
        return JSONResponse(
            content={"message": f"Document processing is {info['status']}. Preview not available."},
            status_code=400
        )
    
    try:
        with open(info["text_path"], 'r', encoding='utf-8') as f:
            text = f.read()
            preview = text[:max_length] + ("..." if len(text) > max_length else "")
        
        return {"document_id": document_id, "preview": preview}
    
    except Exception as e:
        logger.error(f"Error getting preview for document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting preview: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(document_id: str = Path(..., description="The ID of the document")):
    """Delete a document and its associated files"""
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    info = document_store[document_id]
    
    # Delete file paths if they exist
    for path_key in ["file_path", "structured_json_path", "text_path"]:
        path = info.get(path_key)
        if path and os.path.exists(path):
            try:
                os.remove(path)
                logger.info(f"Removed file: {path}")
            except Exception as e:
                logger.error(f"Error deleting file {path}: {str(e)}")
    
    # Remove embeddings directory if it exists
    embeddings_path = info.get("embeddings_path")
    if embeddings_path and os.path.exists(embeddings_path):
        try:
            shutil.rmtree(embeddings_path)
            logger.info(f"Removed embeddings directory: {embeddings_path}")
        except Exception as e:
            logger.error(f"Error deleting embeddings directory {embeddings_path}: {str(e)}")
    
    # Remove from document store
    del document_store[document_id]
    
    return {"message": "Document deleted successfully"}