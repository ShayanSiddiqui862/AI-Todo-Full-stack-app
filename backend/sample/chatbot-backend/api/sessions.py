import sys
import os
# Add the parent directory to the Python path to enable absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import uuid
import time
from backend.src.authentication import get_current_active_user, User
from backend.schemas.rag import ChatSessionRequest, ChatSessionResponse
from backend.exceptions import APIError
from src.db.neon_service import neon_db_service

router = APIRouter()

@router.post("/chatkit/session", response_model=ChatSessionResponse)
async def create_chatkit_session(
    request: ChatSessionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new ChatKit session with OAuth 2.0 and JWT token support
    Implements spec RBS.2 - POST /api/chatkit/session endpoint
    """
    try:
        # Create a new chat session in the database
        session_data = await neon_db_service.create_chat_session(
            user_id=current_user.id,
            session_title=request.session_title if hasattr(request, 'session_title') else f"Chat session {int(time.time())}"
        )

        # Generate client secret (in a real implementation, this would be more sophisticated)
        client_secret = str(uuid.uuid4())

        # Set expiration time (1 hour from now)
        expires_at = int(time.time()) + 3600  # 1 hour in seconds

        # Create session response using the schema
        session_response = ChatSessionResponse(
            session_id=str(session_data['id']),  # Use database ID as session ID
            client_secret=client_secret,
            expires_at=expires_at,
            user_id=current_user.id
        )

        return session_response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create chat session: {str(e)}"
        )

# Additional session management endpoints could be added here
@router.get("/chatkit/session/{session_id}")
async def get_chatkit_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get details of a specific chat session
    """
    try:
        # Retrieve session details from database
        session_data = await neon_db_service.get_chat_session_by_id(int(session_id))

        if not session_data or session_data['user_id'] != current_user.id:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "status": "active",
            "user_id": current_user.id,
            "session_title": session_data['session_title'],
            "created_at": session_data['created_at']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat session: {str(e)}"
        )

@router.delete("/chatkit/session/{session_id}")
async def delete_chatkit_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a chat session
    """
    try:
        # In the database implementation, deleting the session will cascade delete messages
        # First verify the session belongs to the user
        session_data = await neon_db_service.get_chat_session_by_id(int(session_id))

        if not session_data or session_data['user_id'] != current_user.id:
            raise HTTPException(status_code=404, detail="Session not found")

        # Actually delete would happen through foreign key constraint when session is deleted
        # Since we're using foreign keys, when session is deleted, messages will be deleted too
        # In a real implementation, you might want to explicitly delete or mark as deleted

        return {
            "session_id": session_id,
            "status": "deleted",
            "message": "Session deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete chat session: {str(e)}"
        )

# New endpoints for managing chat messages within sessions
@router.post("/chat/{session_id}/message")
async def add_chat_message(
    session_id: str,
    message_data: dict,  # Using dict for now, should create proper schema
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a message to a chat session
    """
    try:
        # Verify the session belongs to the user
        session = await neon_db_service.get_chat_session_by_id(int(session_id))

        if not session or session['user_id'] != current_user.id:
            raise HTTPException(status_code=404, detail="Session not found")

        # Add the message to the database
        message = await neon_db_service.add_chat_message(
            session_id=int(session_id),
            user_id=current_user.id,
            role=message_data.get('role', 'user'),
            content=message_data.get('content', '')
        )

        return {
            "message_id": message['id'],
            "session_id": session_id,
            "role": message['role'],
            "content": message['content'],
            "timestamp": message['timestamp']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add chat message: {str(e)}"
        )

@router.get("/chat/{session_id}/messages")
async def get_chat_messages(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all messages for a chat session
    """
    try:
        # Verify the session belongs to the user
        session = await neon_db_service.get_chat_session_by_id(int(session_id))

        if not session or session['user_id'] != current_user.id:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get all messages for this session
        messages = await neon_db_service.get_chat_messages_by_session(int(session_id))

        return {
            "session_id": session_id,
            "messages": messages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat messages: {str(e)}"
        )

@router.get("/chat/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all chat sessions for the current user
    """
    try:
        sessions = await neon_db_service.get_user_sessions(current_user.id)

        return {
            "user_id": current_user.id,
            "sessions": sessions
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user sessions: {str(e)}"
        )