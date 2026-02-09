"""
Chat Session Endpoint for OpenAI ChatKit
Provides session tokens for the @openai/chatkit-react frontend library.
"""

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
import os

router = APIRouter(prefix="/chat", tags=["chat-session"])


@router.post("/session")
async def create_chat_session():
    """
    Generate a session token for ChatKit frontend.
    
    Returns a client_secret that the frontend can use to initialize
    the ChatKit component and communicate directly with OpenAI.
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API key not configured"
            )
        
        client = OpenAI(api_key=api_key)
        session = client.realtime.sessions.create(
            model="gpt-4o-realtime-preview"
        )
        
        return {"client_secret": session.client_secret.value}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create chat session: {str(e)}"
        )
