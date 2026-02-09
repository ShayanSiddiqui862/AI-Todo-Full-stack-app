"""
Chat Service Module
Provides business logic for managing conversations and messages in the chatbot functionality.
"""

from typing import List, Optional, Dict, Any
from sqlmodel import select
from models import Conversation, Message
from db import get_session_context
from datetime import datetime


class ChatService:
    """
    Service class for handling chat-related business logic including 
    conversation management and message handling.
    """
    
    @staticmethod
    async def create_conversation(user_id: str, title: str = None) -> Optional[Conversation]:
        """
        Create a new conversation for a user.
        
        Args:
            user_id: The ID of the user creating the conversation
            title: Optional title for the conversation
            
        Returns:
            The created Conversation object or None if creation failed
        """
        async with get_session_context() as session:
            conversation = Conversation(
                user_id=user_id,
                title=title
            )
            
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            
            return conversation
    
    @staticmethod
    async def get_conversation_by_id(conversation_id: int, user_id: str) -> Optional[Conversation]:
        """
        Get a specific conversation by its ID for a user.
        
        Args:
            conversation_id: The ID of the conversation to retrieve
            user_id: The ID of the user who owns the conversation
            
        Returns:
            Conversation object if found, None otherwise
        """
        async with get_session_context() as session:
            query = select(Conversation).where(
                Conversation.id == conversation_id, 
                Conversation.user_id == user_id
            )
            result = await session.execute(query)
            conversation = result.scalar_one_or_none()
            
            return conversation
    
    @staticmethod
    async def get_user_conversations(user_id: str) -> List[Conversation]:
        """
        Get all conversations for a specific user.
        
        Args:
            user_id: The ID of the user whose conversations to retrieve
            
        Returns:
            List of Conversation objects
        """
        async with get_session_context() as session:
            query = select(Conversation).where(Conversation.user_id == user_id)
            result = await session.execute(query)
            conversations = result.scalars().all()
            
            return conversations
    
    @staticmethod
    async def add_message_to_conversation(
        conversation_id: int, 
        user_id: str, 
        role: str, 
        content: str
    ) -> Optional[Message]:
        """
        Add a message to a conversation after validating user ownership.
        
        Args:
            conversation_id: The ID of the conversation to add the message to
            user_id: The ID of the user who owns the conversation
            role: The role of the message sender ('user' or 'assistant')
            content: The content of the message
            
        Returns:
            The created Message object or None if creation failed
        """
        # First verify that the conversation belongs to the user
        conversation = await ChatService.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None
        
        async with get_session_context() as session:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content
            )
            
            session.add(message)
            await session.commit()
            await session.refresh(message)
            
            return message
    
    @staticmethod
    async def get_conversation_messages(conversation_id: int, user_id: str, limit: int = 50, offset: int = 0) -> List[Message]:
        """
        Get all messages for a specific conversation after validating user ownership.
        
        Args:
            conversation_id: The ID of the conversation whose messages to retrieve
            user_id: The ID of the user who owns the conversation
            limit: Maximum number of messages to return (default 50)
            offset: Number of messages to skip for pagination (default 0)
            
        Returns:
            List of Message objects
        """
        # First verify that the conversation belongs to the user
        conversation = await ChatService.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return []
        
        async with get_session_context() as session:
            query = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).offset(offset).limit(limit)
            
            result = await session.execute(query)
            messages = result.scalars().all()
            
            return messages
    
    @staticmethod
    async def get_recent_conversations(user_id: str, limit: int = 10) -> List[Conversation]:
        """
        Get the most recent conversations for a user.
        
        Args:
            user_id: The ID of the user whose conversations to retrieve
            limit: Maximum number of conversations to return (default 10)
            
        Returns:
            List of Conversation objects ordered by most recent
        """
        async with get_session_context() as session:
            query = select(Conversation).where(
                Conversation.user_id == user_id
            ).order_by(Conversation.updated_at.desc()).limit(limit)
            
            result = await session.execute(query)
            conversations = result.scalars().all()
            
            return conversations
    
    @staticmethod
    async def update_conversation_title(conversation_id: int, user_id: str, title: str) -> bool:
        """
        Update the title of a conversation after validating user ownership.
        
        Args:
            conversation_id: The ID of the conversation to update
            user_id: The ID of the user who owns the conversation
            title: The new title for the conversation
            
        Returns:
            True if update was successful, False otherwise
        """
        conversation = await ChatService.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False
        
        async with get_session_context() as session:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(conversation)
            
            return True
    
    @staticmethod
    async def get_latest_conversation_for_user(user_id: str) -> Optional[Conversation]:
        """
        Get the most recently created conversation for a user.
        
        Args:
            user_id: The ID of the user whose latest conversation to retrieve
            
        Returns:
            The latest Conversation object or None if no conversations exist
        """
        async with get_session_context() as session:
            query = select(Conversation).where(
                Conversation.user_id == user_id
            ).order_by(Conversation.created_at.desc()).limit(1)
            
            result = await session.execute(query)
            conversation = result.scalar_one_or_none()
            
            return conversation
    
    @staticmethod
    async def get_or_create_user_conversation(user_id: str, title: str = None) -> Optional[Conversation]:
        """
        Get the latest conversation for a user, or create a new one if none exists.
        
        Args:
            user_id: The ID of the user whose conversation to retrieve or create
            title: Optional title for the new conversation if created
            
        Returns:
            The existing or newly created Conversation object
        """
        # Try to get the latest conversation
        conversation = await ChatService.get_latest_conversation_for_user(user_id)
        
        # If no conversation exists, create a new one
        if not conversation:
            conversation = await ChatService.create_conversation(user_id, title)
        
        return conversation