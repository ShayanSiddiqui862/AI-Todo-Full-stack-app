from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Callable, Any
import logging
import time
import asyncio
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIErrorHandler:
    """
    Error handling middleware with 3 retry attempts and 10s timeout
    as required by spec
    """

    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_error_handlers()

    def setup_error_handlers(self):
        """Setup global error handlers for the FastAPI app"""

        @self.app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            """Handle HTTP exceptions"""
            logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": "HTTP Error",
                    "detail": exc.detail,
                    "status_code": exc.status_code
                }
            )

        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            """Handle request validation errors"""
            logger.error(f"Validation Error: {exc.errors()}")
            return JSONResponse(
                status_code=422,
                content={
                    "error": "Validation Error",
                    "detail": exc.errors(),
                    "status_code": 422
                }
            )

        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """Handle general exceptions"""
            logger.error(f"General Exception: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred",
                    "status_code": 500
                }
            )

    @staticmethod
    def retry_with_timeout(max_attempts: int = 3, timeout: int = 10):
        """Decorator to add retry logic with timeout"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception = None

                for attempt in range(max_attempts):
                    try:
                        # Execute with timeout
                        result = await asyncio.wait_for(
                            func(*args, **kwargs),
                            timeout=timeout
                        )
                        return result
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout on attempt {attempt + 1} for function {func.__name__}")
                        last_exception = TimeoutError(f"Function {func.__name__} timed out after {timeout}s")
                    except Exception as e:
                        logger.warning(f"Attempt {attempt + 1} failed for function {func.__name__}: {str(e)}")
                        last_exception = e

                    if attempt < max_attempts - 1:
                        # Exponential backoff: wait 1s, 2s, 4s, etc.
                        delay = min(2 ** attempt, 10)  # Max 10s delay
                        await asyncio.sleep(delay)

                logger.error(f"All {max_attempts} attempts failed for function {func.__name__}")
                raise last_exception

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                last_exception = None

                for attempt in range(max_attempts):
                    try:
                        start_time = time.time()

                        result = func(*args, **kwargs)

                        # Check if execution exceeded timeout
                        elapsed = time.time() - start_time
                        if elapsed > timeout:
                            raise TimeoutError(f"Function {func.__name__} timed out after {timeout}s")

                        return result
                    except Exception as e:
                        logger.warning(f"Attempt {attempt + 1} failed for function {func.__name__}: {str(e)}")
                        last_exception = e

                    if attempt < max_attempts - 1:
                        # Exponential backoff for sync functions
                        delay = min(2 ** attempt, 10)  # Max 10s delay
                        time.sleep(delay)

                logger.error(f"All {max_attempts} attempts failed for function {func.__name__}")
                raise last_exception

            # Return appropriate wrapper based on whether the original function is async
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

# Example usage in API endpoints
def setup_error_middleware(app: FastAPI):
    """Setup error handling middleware for the application"""
    error_handler = APIErrorHandler(app)
    return error_handler

# Custom exception classes for specific error types
class RAGServiceError(Exception):
    """Exception raised when RAG service operations fail"""
    pass

class QdrantConnectionError(Exception):
    """Exception raised when Qdrant connection fails"""
    pass

class DocumentProcessingError(Exception):
    """Exception raised when document processing fails"""
    pass

class AuthenticationError(Exception):
    """Exception raised when authentication fails"""
    pass

# Utility function for consistent error responses
def create_error_response(error_type: str, detail: str, status_code: int):
    """Create a consistent error response format"""
    return {
        "error": error_type,
        "detail": detail,
        "status_code": status_code,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    # Example usage
    from fastapi import FastAPI

    app = FastAPI()
    error_handler = APIErrorHandler(app)

    @app.get("/test-error")
    @APIErrorHandler.retry_with_timeout(max_attempts=3, timeout=5)
    async def test_error_endpoint():
        # Simulate an operation that might fail
        import random
        if random.random() < 0.7:  # 70% chance of failure
            raise Exception("Simulated error for testing")
        return {"message": "Success!"}

    print("Error handler setup completed")