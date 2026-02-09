from tools.rag_tool import RAGTool
from typing import Any, Optional, List, Dict
from pydantic import BaseModel
import sys
import os

from fastapi import APIRouter, HTTPException, Depends
import logging
from openai import OpenAI
from dotenv import load_dotenv

# NOTE: Removed 'connection' import, assuming create_agent, create_runner, config are global or defined elsewhere
from connection import create_agent, create_runner, config

from backend.src.authentication import get_current_active_user, User
from src.error_handler import retry_with_backoff, handle_api_errors, RetryConfig
from src.db.neon_service import neon_db_service

from schemas.rag import RAGQueryRequest, RAGQueryResponse, SearchRequest, SearchResponse
from schemas.rag import SourceInfo, SearchResult

from exceptions import APIError, RAGServiceError

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize RAG Tool
try:
    GLOBAL_RAG_TOOL = RAGTool()
    logger.info("RAGTool (with embedding model and Qdrant client) initialized successfully.")
except Exception as e:
    logger.error(f"FATAL: Failed to initialize RAGTool globally: {e}")

router = APIRouter()

# --- RAG QUERY ENDPOINT ---

@router.post("/rag/query", response_model=RAGQueryResponse)
@handle_api_errors(status_code=500, detail="Error processing RAG query")
@retry_with_backoff(RetryConfig(max_attempts=15, timeout=60.0))
async def rag_query(
    request: RAGQueryRequest,
    current_user: User = Depends(get_current_active_user)
):
    try:
        logger.info(f"Processing RAG query: {request.message[:50]}...")
        raw_search_results: List[Dict[str, Any]] = GLOBAL_RAG_TOOL._run(
            request.message, request.top_k
        )

        sources: List[SourceInfo] = []
        context_text = ""

        for i, result_dict in enumerate(raw_search_results):
            context_text += (
                f"\n--- Source {i+1} ({result_dict.get('source_file')} - "
                f"Score: {result_dict.get('score'):.3f}) ---\n"
            )
            context_text += result_dict.get("content", "") + "\n"

            sources.append(
                SourceInfo(
                    score=result_dict.get("score", 0.0),
                    content=result_dict.get("content", "")[:500],
                    source_file=result_dict.get("source_file", "unknown"),
                    metadata=result_dict.get("metadata", {}),
                )
            )

        context = f"Relevant book content:\n{context_text}\n\n"

        if request.selected_text:
            context += f"User selected text for context:\n{request.selected_text}\n\n"
            logger.info(
                f"Including selected text in context: {request.selected_text[:100]}..."
            )

        full_prompt = (
            f"{context}User question: {request.message}\n\n"
            "Please provide an answer based on the book content and context provided above."
        )

        agent = create_agent(
            name="RAG_Question_Answering_Agent",
            instructions=(
                "You are a helpful assistant that answers questions based on "
                "provided book content. Use the context provided to give accurate answers."
            ),
        )

        runner = create_runner(agent)

        agent_response = await runner.run(
            agent,
            input=[
                {
                    "role": "system",
                    "content": (
                        """"You are a AI-assitant designed to answer question related to Humanoid Robotics 
                        Give an detailed answer to the question use context provided to  include in answer .
                        The answer also have code snippets where neccessary . If you don't know the answer, just say that you don't know you can use web for searching answer also"""
                    ),
                },
                {"role": "user", "content": full_prompt},
            ],
            run_config=config,
        )


        ai_response = str(agent_response.final_output)

        # Store the conversation in the database
        # First, create or get a default chat session for the user
        # In a real implementation, you might want to pass the session ID in the request
        # For now, we'll create a default session if one doesn't exist recently
        import time
        session_title = f"Chat session {int(time.time())}"
        chat_session = await neon_db_service.create_chat_session(
            user_id=current_user.id,  # Using the user ID from the authenticated user
            session_title=session_title
        )

        # Add user message to database
        await neon_db_service.add_chat_message(
            session_id=chat_session['id'],
            user_id=current_user.id,  # Using the user ID from the authenticated user
            role='user',
            content=request.message
        )

        # Add AI response to database
        await neon_db_service.add_chat_message(
            session_id=chat_session['id'],
            user_id=current_user.id,  # Using the user ID from the authenticated user
            role='assistant',
            content=ai_response
        )

        from datetime import datetime
        return RAGQueryResponse(
            query=request.message,
            response=ai_response,
            sources=sources,
            selected_text_used=request.selected_text,
            timestamp=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Error processing RAG query: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing query: {str(e)}"
        )

# --- CONTENT SEARCH ENDPOINT ---

@router.post("/content/search", response_model=SearchResponse)
@handle_api_errors(status_code=500, detail="Error performing content search")
@retry_with_backoff(RetryConfig(max_attempts=3, timeout=10.0))
async def search_content(
    request: SearchRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Search endpoint for book content as per API contract
    """
    try:
        logger.info(f"Searching content for query: {request.query[:50]}...")

        results_dicts: List[Dict[str, Any]] = GLOBAL_RAG_TOOL._run(
            request.query, request.top_k
        )

        final_results: List[SearchResult] = []

        for i, hit_dict in enumerate(results_dicts):
            try:
                final_results.append(
                    SearchResult(
                        id=i + 1,
                        **hit_dict,
                    )
                )
            except Exception as e:
                logger.error(
                    f"Pydantic conversion failed for search result {i+1}: {e}. "
                    f"Data: {hit_dict}"
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Internal data format error during result conversion: {str(e)}",
                )

        return SearchResponse(
            results=final_results,
            query=request.query,
            total_results=len(final_results),
        )

    except Exception as e:
        logger.error(f"Error searching content: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error searching content: {str(e)}"
        )

# Health check for the RAG service
@router.get("/rag/health")
async def rag_health():
    """Health check for the RAG service"""
    return {
        "status": "healthy",
        "service": "RAG Service",
        "message": "RAG service is operational",
    }
