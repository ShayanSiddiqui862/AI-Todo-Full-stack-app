"""
Agent Runner Module
Implements the Agent using the OpenAI Agents SDK with Gemini API to process user messages
and interact with tools for task management operations.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, function_tool
from sqlmodel import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Task
from datetime import datetime

load_dotenv()

# Database setup for sync access in tools
DATABASE_URL = os.getenv("DATABASE_URL")
tool_engine = create_async_engine(DATABASE_URL)
ToolSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=tool_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Gemini API Configuration
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Create external client for Gemini
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Create model configuration
model = OpenAIChatCompletionsModel(
    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    openai_client=external_client
)

# Create run configuration
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)


def run_async(coro):
    """Helper to run async code from sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop and loop.is_running():
        # We're in an async context, need to use thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)


# Define task management tools using @function_tool decorator
@function_tool
def list_tasks(user_id: str) -> str:
    """
    List all tasks for the specified user. Returns a summary of their tasks.
    
    Args:
        user_id: The ID of the user whose tasks to retrieve
    """
    async def _list():
        async with ToolSessionLocal() as session:
            query = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
            result = await session.execute(query)
            tasks = result.scalars().all()
            
            if not tasks:
                return "No tasks found. You can ask me to add a new task."
            
            task_lines = []
            for task in tasks:
                status = "✓" if task.completed else "○"
                task_lines.append(f"{status} [{task.id}] {task.title}")
            
            return f"Found {len(tasks)} task(s):\n" + "\n".join(task_lines)
    
    return run_async(_list())


@function_tool
def add_task(user_id: str, title: str, description: str = "") -> str:
    """
    Create a new task for the user.
    
    Args:
        user_id: The ID of the user creating the task
        title: The title of the task
        description: Optional description of the task
    """
    async def _add():
        if not title or len(title.strip()) == 0:
            return "Error: Task title is required and cannot be empty."
        
        async with ToolSessionLocal() as session:
            task = Task(
                user_id=user_id,
                title=title.strip(),
                description=description or "",
                completed=False
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            
            return f"Task created successfully! Task ID: {task.id}, Title: '{task.title}'"
    
    return run_async(_add())


@function_tool
def complete_task(user_id: str, task_id: int) -> str:
    """
    Mark a task as completed.
    
    Args:
        user_id: The ID of the user who owns the task
        task_id: The ID of the task to mark as completed
    """
    async def _complete():
        async with ToolSessionLocal() as session:
            query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            result = await session.execute(query)
            task = result.scalar_one_or_none()
            
            if not task:
                return f"Error: No task found with ID {task_id}."
            
            if task.completed:
                return f"Task '{task.title}' is already completed."
            
            task.completed = True
            task.updated_at = datetime.utcnow()
            await session.commit()
            
            return f"Task '{task.title}' marked as completed! ✓"
    
    return run_async(_complete())


@function_tool
def delete_task(user_id: str, task_id: int) -> str:
    """
    Delete a task.
    
    Args:
        user_id: The ID of the user who owns the task
        task_id: The ID of the task to delete
    """
    async def _delete():
        async with ToolSessionLocal() as session:
            query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            result = await session.execute(query)
            task = result.scalar_one_or_none()
            
            if not task:
                return f"Error: No task found with ID {task_id}."
            
            task_title = task.title
            await session.delete(task)
            await session.commit()
            
            return f"Task '{task_title}' deleted successfully."
    
    return run_async(_delete())


@function_tool
def update_task(user_id: str, task_id: int, title: str = None, description: str = None) -> str:
    """
    Update a task's title or description.
    
    Args:
        user_id: The ID of the user who owns the task
        task_id: The ID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)
    """
    async def _update():
        async with ToolSessionLocal() as session:
            query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            result = await session.execute(query)
            task = result.scalar_one_or_none()
            
            if not task:
                return f"Error: No task found with ID {task_id}."
            
            if title is not None:
                if len(title.strip()) == 0:
                    return "Error: Task title cannot be empty."
                task.title = title.strip()
            
            if description is not None:
                task.description = description
            
            task.updated_at = datetime.utcnow()
            await session.commit()
            
            return f"Task '{task.title}' updated successfully."
    
    return run_async(_update())


class AgentRunner:
    """
    Class responsible for initializing and running the Agent
    that processes natural language and interacts with task tools.
    """
    
    def __init__(self):
        """
        Initialize the AgentRunner with Gemini-powered agent.
        """
        self.agent = Agent(
            name="Task Assistant",
            instructions=(
                "You are a helpful assistant that helps users manage their tasks. "
                "Recognize various ways users express the same intent. "
                "For example: 'Complete task 1', 'Finish task 1', and 'Done with task 1' all mean the same thing. "
                "When calling tools, always use the user_id that was provided in the context. "
                "Be concise and helpful in your responses. "
                "After successfully completing an action, confirm what was done."
            ),
            tools=[list_tasks, add_task, complete_task, delete_task, update_task]
        )
    
    async def run_agent(self, user_message: str, user_id: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Run the Agent to process a user message and return a response.
        
        Args:
            user_message: The message from the user
            user_id: The ID of the user (needed for tool execution)
            conversation_history: Previous conversation history (optional)
            
        Returns:
            The agent's response to the user
        """
        try:
            # Prepend user_id context to the message so tools know which user to operate on
            context_message = f"The user_id is: {user_id}\n\nUser message: {user_message}"
            
            # Run the agent
            result = await Runner.run(
                self.agent,
                context_message,
                run_config=config
            )
            
            return result.final_output or "I processed your request but didn't generate a specific response."
                
        except Exception as e:
            # Handle any errors gracefully
            error_msg = f"Sorry, I encountered an error processing your request: {str(e)}"
            print(f"Error in AgentRunner.run_agent: {str(e)}")  # Log the error
            import traceback
            traceback.print_exc()
            return error_msg
    
    def validate_user_input(self, user_message: str) -> Dict[str, Any]:
        """
        Validate user input before processing.
        
        Args:
            user_message: The message from the user
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "is_valid": True,
            "errors": [],
            "sanitized_message": user_message.strip()
        }
        
        # Check for empty message
        if not result["sanitized_message"]:
            result["is_valid"] = False
            result["errors"].append("Message cannot be empty")
        
        # Check for message length
        if len(result["sanitized_message"]) > 10000:
            result["is_valid"] = False
            result["errors"].append("Message exceeds maximum length of 10000 characters")
        
        return result


# Global instance of AgentRunner
agent_runner = AgentRunner()


# Export the agent runner instance
__all__ = ['agent_runner', 'AgentRunner']