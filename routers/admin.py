from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict
import os
import shutil
import logging
import psutil
import sqlite3
from utils.database import get_all_documents, DB_PATH

router = APIRouter()
logger = logging.getLogger(__name__)

class SystemStats(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    processed_documents: int
    pending_documents: int
    failed_documents: int

class DocumentStats(BaseModel):
    total_documents: int
    total_pages: int
    total_chunks: int
    average_chunks_per_page: float
    document_statuses: Dict[str, int]

class DocumentDirectoryStats(BaseModel):
    uploads_dir_size_mb: float
    pages_dir_size_mb: float
    text_dir_size_mb: float
    json_dir_size_mb: float
    embeddings_dir_size_mb: float

def get_dir_size(path):
    """Calculate directory size in bytes."""
    total_size = 0
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path):
        for dirpath, dirnames, filenames in os.walk(abs_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
    return total_size

@router.get("/stats/system", response_model=SystemStats)
async def get_system_stats():
    """Get current system statistics."""
    try:
        all_docs = get_all_documents()
        processed_docs = sum(1 for doc in all_docs if doc["status"] == "completed")
        pending_docs = sum(1 for doc in all_docs if doc["status"] in ["pending", "processing"])
        failed_docs = sum(1 for doc in all_docs if doc["status"] == "failed")

        return SystemStats(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage_percent=psutil.disk_usage('/').percent,
            processed_documents=processed_docs,
            pending_documents=pending_docs,
            failed_documents=failed_docs
        )
    except Exception as e:
        logger.error(f"System stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/documents", response_model=DocumentStats)
async def get_document_stats():
    """Get document processing statistics."""
    try:
        all_docs = get_all_documents()
        status_counts = {}
        total_pages = 0
        total_chunks = 0

        for doc in all_docs:
            status = doc["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            if status == "completed":
                total_pages += doc.get("pages") or 0
                total_chunks += doc.get("chunks") or 0

        avg_chunks_per_page = (total_chunks / total_pages) if total_pages else 0

        return DocumentStats(
            total_documents=len(all_docs),
            total_pages=total_pages,
            total_chunks=total_chunks,
            average_chunks_per_page=avg_chunks_per_page,
            document_statuses=status_counts
        )
    except Exception as e:
        logger.error(f"Document stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/storage", response_model=DocumentDirectoryStats)
async def get_storage_stats():
    """Get storage statistics for directories."""
    try:
        dirs = ["Uploads", "Pages", "Sample Text", "Structured Text", "Embeddings"]
        sizes = [get_dir_size(d) / (1024 * 1024) for d in dirs]

        return DocumentDirectoryStats(
            uploads_dir_size_mb=sizes[0],
            pages_dir_size_mb=sizes[1],
            text_dir_size_mb=sizes[2],
            json_dir_size_mb=sizes[3],
            embeddings_dir_size_mb=sizes[4]
        )
    except Exception as e:
        logger.error(f"Storage stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup", status_code=202)
async def cleanup_temp_files(background_tasks: BackgroundTasks):
    """Initiate cleanup of temporary files."""

    def cleanup_task():
        all_docs = get_all_documents()
        preserved_files = {
            os.path.abspath(doc[key])
            for doc in all_docs
            for key in ["file_path", "structured_json_path", "text_path"]
            if doc.get(key)
        }

        pages_dir = os.path.abspath("Pages")
        if os.path.exists(pages_dir):
            for filename in os.listdir(pages_dir):
                file_path = os.path.abspath(os.path.join(pages_dir, filename))
                if file_path not in preserved_files and os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed temporary file: {file_path}")

        logger.info("Cleanup completed successfully.")

    background_tasks.add_task(cleanup_task)
    return {"message": "Cleanup task initiated."}

@router.delete("/reset", status_code=202)
async def reset_application(background_tasks: BackgroundTasks):
    """Reset application by clearing all stored data."""

    def reset_task():
        # Clear database tables
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chat_history')
            cursor.execute('DELETE FROM documents')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error clearing database: {e}")

        for directory in ['Uploads', 'Pages', 'Sample Text', 'Structured Text', 'Embeddings']:
            abs_directory = os.path.abspath(directory)
            if os.path.exists(abs_directory):
                for item in os.listdir(abs_directory):
                    item_path = os.path.join(abs_directory, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        logger.info(f"Deleted: {item_path}")
                    except Exception as e:
                        logger.error(f"Error deleting {item_path}: {e}")

        logger.info("Application reset completed successfully.")

    background_tasks.add_task(reset_task)
    return {"message": "Reset task initiated."}
