import sys
import os
# Add the parent directory to the Python path to enable absolute imports


from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional
import logging
from dotenv import load_dotenv
from pydantic import BaseModel
import tempfile
import hashlib
from pathlib import Path

# Import Qdrant services
from backend.src.qdrant_service import QdrantService
from backend.ingestion.qdrant_uploader import QdrantUploader
from backend.src.authentication import get_current_active_user, User
from backend.src.error_handler import retry_with_backoff, handle_api_errors, RetryConfig
from backend.exceptions import APIError, QdrantUploadError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class UploadResponse(BaseModel):
    message: str
    file_name: str
    chunks_uploaded: int
    collection_name: str

class BookUploadRequest(BaseModel):
    file_name: str
    source_type: str = "pdf"  # pdf, txt, md, etc.
    chunk_size: int = 1000  # characters per chunk
    overlap: int = 100      # overlap between chunks

class IngestionConfig(BaseModel):
    chunk_size: int = 1000
    overlap: int = 100
    embedding_model: str = "all-MiniLM-L6-v2"

# --- FILE EXTRACTION FUNCTIONS ---

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except ImportError:
        logger.error("PyPDF2 library not installed.")
        raise HTTPException(status_code=500, detail="PyPDF2 library not installed")
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT or MD file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 💡 LOGGING ADDED FOR DEBUGGING
        logger.info(f"Extracted content length (before strip): {len(content)}")
        
        # Strip content to check for empty strings
        stripped_content = content.strip()
        
        if not stripped_content:
            logger.warning(f"File {file_path} extracted content is empty or only whitespace.")
            return ""
        
        # Return the original content (not stripped, as whitespace is needed for chunking)
        return content
        
    except Exception as e:
        logger.error(f"Error extracting text from file {file_path}: {str(e)}")
        # Check for common encoding errors
        try:
             with open(file_path, 'r', encoding='latin-1') as file:
                 content = file.read()
             logger.warning(f"Successfully read file with latin-1 encoding.")
             return content
        except Exception:
             raise HTTPException(status_code=500, detail=f"Error processing TXT/MD: {str(e)}")

# --- CHUNKING FUNCTION ---

def chunk_text(text: str, chunk_size: int, overlap: int) -> list:
    """Split text into overlapping chunks"""
    chunks = []
    text_length = len(text)
    start = 0

    while start < text_length:
        end = start + chunk_size
        
        # 💡 FIX: Ensure end does not exceed text length
        chunk = text[start:min(end, text_length)]
        
        if chunk.strip(): 
            chunks.append(chunk.strip())

        # 💡 FIX: Move the start position correctly
        # If we reached the end, break the loop
        if end >= text_length:
             break
        
        # Move start back by overlap
        start = end - overlap 
        
        # Ensure start doesn't go negative if chunk_size < overlap (shouldn't happen here)
        if start < 0:
             start = 0 

    return chunks

# --- EMBEDDING FUNCTION ---

def generate_embedding(text: str) -> list:
    """Generate embedding for text using sentence transformer"""
    # ... (No changes needed here, assuming the embedding issues are resolved)
    try:
        from sentence_transformers import SentenceTransformer
        
        # 💡 NOTE: For high throughput production, this model should be initialized globally (like in RAGTool)
        # but for upload, it's safer to keep it here unless a global IngestionService is defined.
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embedding = model.encode([text])[0].tolist()
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

import re
def normalize_content(text: str) -> str:
    """Removes non-standard characters and normalizes whitespace."""
    # 1. Remove non-printable characters (a common source of errors)
    cleaned_text = ''.join(filter(lambda x: x in printable, text))
    
    # 2. Normalize all types of whitespace (tabs, multiple spaces, newlines) to a single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text


from string import printable 
# --- END NEW/UPDATED UTILITY FUNCTION ---

@router.post("/ingestion/upload", response_model=UploadResponse)
@handle_api_errors(status_code=500, detail="Error uploading book content")
@retry_with_backoff(RetryConfig(max_attempts=3, timeout=30.0))
async def upload_book_content(
file: UploadFile = File(...),
):

    temp_file_path = None
    try:
        logger.info(f"Processing file upload: {file.filename}")

        allowed_extensions = {'.pdf', '.txt', '.md', '.docx', '.doc'}
        file_extension = Path(file.filename).suffix.lower()
        # Create temporary file to save uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Extract text based on file type
            if file_extension == '.pdf':
                text_content = extract_text_from_pdf(temp_file_path)
            elif file_extension in ['.txt', '.md', '.docx', '.doc']:
                text_content = extract_text_from_txt(temp_file_path)
            else:
                text_content = extract_text_from_txt(temp_file_path)

            # --- CRITICAL CHECK ---
            # 💡 APPLY NORMALIZATION HERE to ensure only clean content is chunked
            clean_text_content = normalize_content(text_content)
            
            if not clean_text_content:
                logger.error(f"File {file.filename} produced empty content after normalization.")
                raise HTTPException(status_code=400, detail="File content is empty or unreadable after extraction.")
            # --- CRITICAL CHECK END ---

            # Chunk the text using the original text_content (for accurate character counting)
            chunks = chunk_text(text_content, chunk_size=1000, overlap=100)
            logger.info(f"Text chunked into {len(chunks)} pieces")
            
            if not chunks:
                logger.error(f"File {file.filename} produced zero chunks. Content length: {len(text_content)}")
                raise HTTPException(status_code=400, detail="File content could not be split into meaningful chunks. Check chunk size.")

            # Initialize Qdrant uploader
            uploader = QdrantUploader()

            if not uploader.test_connection():
                raise HTTPException(status_code=500, detail="Cannot connect to Qdrant")

            uploaded_count = 0
            
            # 💡 FIX: Implementing hash-based unique IDs
            for i, chunk in enumerate(chunks):
                # 1. Normalize the chunk content for a stable hash input
                normalized_chunk = normalize_content(chunk)

                # 2. Create a unique source string: filename + chunk index + content hash
                # This ensures the ID changes if content or index changes, preventing overwrite errors.
                id_source = f"{file.filename}_{i}_{hashlib.sha256(normalized_chunk.encode('utf-8')).hexdigest()}"
                
                # 3. Use a hash of the stable source as the Qdrant string ID (UUID format)
                # This is more resilient than raw hashing for ID generation.
                point_id_qdrant = hashlib.sha256(id_source.encode('utf-8')).hexdigest()
                point_id_qdrant = point_id_qdrant[:32]
                
                # Generate embedding for the chunk
                embedding = generate_embedding(chunk)

                # Prepare payload
                payload = {
                    "content": chunk, # Use original chunk for storage/retrieval
                    "normalized_content": normalized_chunk, # Store clean version for debugging/analysis
                    "source_file": file.filename,
                    "chunk_id": i,
                    "metadata": {
                        "file_name": file.filename,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                }

                # Upload to Qdrant
                success = uploader.upload_single_point(
                    point_id=point_id_qdrant, # <-- Unique, stable ID
                    vector=embedding,
                    payload=payload
                )

                if success:
                    uploaded_count += 1
                else:
                    logger.warning(f"Failed to upload chunk {i} with ID {point_id_qdrant}")
            
            os.unlink(temp_file_path)

            response = UploadResponse(
                message=f"Successfully uploaded {uploaded_count} chunks from {file.filename}",
                file_name=file.filename,
                chunks_uploaded=uploaded_count,
                collection_name=uploader.collection_name
            )

            logger.info(f"Upload completed: {response.message}")
            return response

        except Exception as e:
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_book_content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
@router.get("/ingestion/status")
async def ingestion_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get status of the ingestion service
    """
    try:
        uploader = QdrantUploader()
        connection_ok = uploader.test_connection()

        if connection_ok:
            # Get collection info
            client = uploader.qdrant_service.get_client()
            collection_info = client.get_collection(uploader.collection_name)

            return {
                "status": "healthy",
                "connection": "ok",
                "collection": uploader.collection_name,
                "vector_count": collection_info.points_count,
                "collection_exists": True
            }
        else:
            return {
                "status": "unhealthy",
                "connection": "failed",
                "collection": uploader.collection_name,
                "vector_count": 0,
                "collection_exists": False
            }

    except Exception as e:
        logger.error(f"Error getting ingestion status: {str(e)}")
        return {
            "status": "unhealthy",
            "connection": "failed",
            "collection": "book_content",
            "vector_count": 0,
            "collection_exists": False,
            "error": str(e)
        }

# Health check for the ingestion service
@router.get("/ingestion/health")
async def ingestion_health():
    """Health check for the ingestion service"""
    return {
        "status": "healthy",
        "service": "Ingestion Service",
        "message": "Ingestion service is operational"
    }