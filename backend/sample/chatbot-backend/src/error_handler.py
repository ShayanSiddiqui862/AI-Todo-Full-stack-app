import asyncio
import functools
import logging
from typing import Callable, Any
from fastapi import HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetryConfig(BaseModel):
    max_attempts: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 10.0  # seconds
    timeout: float = 10.0    # seconds

def retry_with_backoff(config: RetryConfig = RetryConfig()):
    """
    Decorator to implement retry logic with exponential backoff
    Implements spec requirement for 3 retry attempts and 10s timeout
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    # Set timeout for the function call
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=config.timeout
                    )
                    return result
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout on attempt {attempt + 1} for function {func.__name__}")
                    last_exception = TimeoutError(f"Function {func.__name__} timed out after {config.timeout}s")
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for function {func.__name__}: {str(e)}")
                    last_exception = e

                if attempt < config.max_attempts - 1:
                    # Calculate delay with exponential backoff
                    delay = min(config.base_delay * (2 ** attempt), config.max_delay)
                    await asyncio.sleep(delay)

            logger.error(f"All {config.max_attempts} attempts failed for function {func.__name__}")
            raise last_exception

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    start_time = time.time()
                    if time.time() - start_time > config.timeout:
                        raise TimeoutError(f"Function {func.__name__} timed out after {config.timeout}s")

                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for function {func.__name__}: {str(e)}")
                    last_exception = e

                if attempt < config.max_attempts - 1:
                    # Calculate delay with exponential backoff
                    delay = min(config.base_delay * (2 ** attempt), config.max_delay)
                    time.sleep(delay)

            logger.error(f"All {config.max_attempts} attempts failed for function {func.__name__}")
            raise last_exception

        # Return appropriate wrapper based on whether the original function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

def handle_api_errors(status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, detail: str = "Internal server error"):
    """
    Decorator to handle API errors with consistent error responses
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"API error in {func.__name__}: {str(e)}")
                raise HTTPException(
                    status_code=status_code,
                    detail=f"{detail}: {str(e)}"
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"API error in {func.__name__}: {str(e)}")
                raise HTTPException(
                    status_code=status_code,
                    detail=f"{detail}: {str(e)}"
                )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# Error response model
class ErrorResponse(BaseModel):
    error: str
    timestamp: datetime
    path: str
    status_code: int

# Example usage
@retry_with_backoff(RetryConfig(max_attempts=3, timeout=10.0))
async def example_api_call():
    # Simulate an API call that might fail
    import random
    if random.random() < 0.7:  # 70% chance of failure for testing
        raise Exception("Simulated API failure")
    return "Success!"

if __name__ == "__main__":
    # Test the retry mechanism
    async def test_retry():
        try:
            result = await example_api_call()
            print(f"API call succeeded: {result}")
        except Exception as e:
            print(f"API call failed after retries: {str(e)}")

    # Run the test
    asyncio.run(test_retry())