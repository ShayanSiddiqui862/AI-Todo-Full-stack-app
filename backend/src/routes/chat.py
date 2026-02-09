from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from db import get_session
from auth import verify_jwt
from src.agents.runner import agent_runner
from src.services.chat_service import ChatService
from src.utils.logging import log_chat_interaction, log_error, setup_logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import json


# Set up logging
setup_logging()

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    metadata: Optional[dict] = None


class ChatResponse(BaseModel):
    response: str
    thread_id: Optional[str] = None
    conversation_id: str
    created_at: datetime
    status: str


class ErrorResponse(BaseModel):
    error: str
    code: str
    status: str


@router.post("/users/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    chat_request: ChatRequest,
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """
    Process chat messages from authenticated users through the OpenAI Agents SDK 
    and return AI-generated responses.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user_id != user_id:
        log_error(Exception(f"Unauthorized access attempt by user {current_user_id} to access user {user_id}'s chat"), "chat_endpoint.auth")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized to access this endpoint"
        )
    
    # Validate the user's message
    validation_result = agent_runner.validate_user_input(chat_request.message)
    if not validation_result["is_valid"]:
        log_error(Exception(f"Invalid input: {'; '.join(validation_result['errors'])}"), "chat_endpoint.validation")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {'; '.join(validation_result['errors'])}"
        )
    
    try:
        # Get or create a conversation for the user
        # If thread_id is provided, try to find that specific conversation
        conversation = None
        if chat_request.thread_id:
            # Attempt to find conversation by some identifier (in a real implementation, 
            # thread_id might map to conversation.id in some way)
            # For now, we'll just get the latest conversation or create a new one
            conversation = await ChatService.get_latest_conversation_for_user(user_id)
        
        # If no conversation exists or no thread_id provided, get or create one
        if not conversation:
            conversation = await ChatService.get_or_create_user_conversation(
                user_id, 
                title=f"Chat on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
        
        if not conversation:
            error_msg = "Failed to create or retrieve conversation"
            log_error(Exception(error_msg), "chat_endpoint.conversation")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        # Add the user's message to the conversation
        user_message = await ChatService.add_message_to_conversation(
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=validation_result["sanitized_message"]
        )
        
        if not user_message:
            error_msg = "Failed to save user message"
            log_error(Exception(error_msg), "chat_endpoint.save_message")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        # Get conversation history to provide context to the agent
        conversation_history = await ChatService.get_conversation_messages(
            conversation_id=conversation.id,
            user_id=user_id
        )
        
        # Format history for the agent (excluding the current message we just added)
        formatted_history = []
        for msg in conversation_history[:-1]:  # Exclude the current message
            formatted_history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Run the agent to process the message
        agent_response = await agent_runner.run_agent(
            user_message=validation_result["sanitized_message"],
            user_id=user_id,
            conversation_history=formatted_history
        )
        
        # Add the agent's response to the conversation
        assistant_message = await ChatService.add_message_to_conversation(
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=agent_response
        )
        
        if not assistant_message:
            error_msg = "Failed to save assistant response"
            log_error(Exception(error_msg), "chat_endpoint.save_response")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        # Log the successful chat interaction
        log_chat_interaction(
            user_id=user_id,
            conversation_id=str(conversation.id),
            user_message=validation_result["sanitized_message"],
            agent_response=agent_response,
            success=True
        )
        
        # Prepare and return the response
        response = ChatResponse(
            response=agent_response,
            thread_id=str(conversation.id),  # Using conversation ID as thread ID
            conversation_id=str(conversation.id),
            created_at=datetime.utcnow(),
            status="success"
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle unexpected errors
        log_error(e, "chat_endpoint.unhandled")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing chat request"
        )


@router.get("/users/{user_id}/conversations/{conversation_id}/messages", response_model=List[Dict[str, Any]])
async def get_conversation_messages(
    user_id: str,
    conversation_id: int,
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve all messages for a specific conversation.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized to access this conversation"
        )
    
    try:
        # Get the conversation messages
        messages = await ChatService.get_conversation_messages(conversation_id, user_id)
        
        # Format the messages for the response
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": str(msg.id),
                "content": msg.content,
                "role": msg.role,
                "timestamp": msg.created_at.isoformat()
            })
        
        return formatted_messages
        
    except Exception as e:
        log_error(e, "get_conversation_messages")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving conversation messages"
        )


@router.post("/users/{user_id}/conversations", response_model=Dict[str, Any])
async def create_conversation_endpoint(
    user_id: str,
    request_data: Dict[str, Any],
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new conversation for a user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized to create conversation"
        )
    
    try:
        title = request_data.get("title")
        
        # Create the conversation
        conversation = await ChatService.create_conversation(user_id, title)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conversation"
            )
        
        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        }
        
    except Exception as e:
        log_error(e, "create_conversation_endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error creating conversation"
        )


# Include the router in the main app
# This would typically be done in main.py with: app.include_router(router)