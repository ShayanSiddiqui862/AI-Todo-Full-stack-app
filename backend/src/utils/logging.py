import logging
import sys
from datetime import datetime
from typing import Any, Dict


def setup_logging(level: str = "INFO"):
    """
    Set up logging configuration for the application.
    
    Args:
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string level to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Also configure uvicorn loggers to use the same level
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(log_level)
    logging.getLogger("uvicorn.error").setLevel(log_level)
    logging.getLogger("fastapi").setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: The name of the logger
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_chat_interaction(user_id: str, conversation_id: str, user_message: str, 
                        agent_response: str, success: bool = True):
    """
    Log a chat interaction for monitoring and debugging purposes.
    
    Args:
        user_id: The ID of the user
        conversation_id: The ID of the conversation
        user_message: The message from the user
        agent_response: The response from the agent
        success: Whether the interaction was successful
    """
    logger = get_logger("chat.interactions")
    
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"CHAT_INTERACTION - User:{user_id} | Conv:{conversation_id} | Status:{status}")
    logger.debug(f"USER_MESSAGE: {user_message}")
    logger.debug(f"AGENT_RESPONSE: {agent_response}")


def log_error(error: Exception, context: str = ""):
    """
    Log an error with context information.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    logger = get_logger("errors")
    logger.error(f"ERROR in {context}: {str(error)}", exc_info=True)