import os
import pickle
import hashlib
from pathlib import Path
from typing import Any, Optional
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelCache:
    """
    Implements model caching mechanism to store sentence-transformer/all-MiniLM-L6-V2 locally
    for faster subsequent loads as required by spec
    """

    def __init__(self, cache_dir: str = "model_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _generate_cache_key(self, model_name: str, *args) -> str:
        """Generate a unique cache key based on model name and parameters"""
        key_string = f"{model_name}_{'_'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key"""
        return self.cache_dir / f"{cache_key}.pkl"

    def is_cached(self, cache_key: str) -> bool:
        """Check if a model is already cached"""
        cache_file = self._get_cache_file_path(cache_key)
        return cache_file.exists()

    def save_to_cache(self, cache_key: str, model: Any, metadata: Optional[dict] = None) -> bool:
        """Save a model to cache"""
        try:
            cache_file = self._get_cache_file_path(cache_key)

            # Create metadata if not provided
            if metadata is None:
                metadata = {
                    'timestamp': time.time(),
                    'size': len(pickle.dumps(model)) if hasattr(model, '__dict__') else 0
                }

            # Save model and metadata
            cache_data = {
                'model': model,
                'metadata': metadata
            }

            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)

            logger.info(f"Model cached successfully: {cache_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving model to cache: {str(e)}")
            return False

    def load_from_cache(self, cache_key: str) -> Optional[Any]:
        """Load a model from cache"""
        cache_file = self._get_cache_file_path(cache_key)

        if not cache_file.exists():
            logger.info(f"Cache file does not exist: {cache_file}")
            return None

        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)

            logger.info(f"Model loaded from cache: {cache_file}")
            return cache_data['model']
        except Exception as e:
            logger.error(f"Error loading model from cache: {str(e)}")
            # Remove corrupted cache file
            try:
                cache_file.unlink()
                logger.info(f"Removed corrupted cache file: {cache_file}")
            except:
                pass
            return None

    def get_cache_info(self, cache_key: str) -> Optional[dict]:
        """Get cache information for a specific cache key"""
        cache_file = self._get_cache_file_path(cache_key)

        if not cache_file.exists():
            return None

        try:
            stat = cache_file.stat()
            return {
                'file_path': str(cache_file),
                'size_bytes': stat.st_size,
                'modified': stat.st_mtime,
                'exists': True
            }
        except Exception as e:
            logger.error(f"Error getting cache info: {str(e)}")
            return None

    def clear_cache(self, cache_key: str = None) -> bool:
        """Clear specific cache entry or entire cache if no key provided"""
        if cache_key:
            cache_file = self._get_cache_file_path(cache_key)
            if cache_file.exists():
                try:
                    cache_file.unlink()
                    logger.info(f"Cleared cache: {cache_file}")
                    return True
                except Exception as e:
                    logger.error(f"Error clearing cache: {str(e)}")
                    return False
        else:
            # Clear entire cache directory
            import shutil
            try:
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(exist_ok=True)
                logger.info(f"Cleared entire cache directory: {self.cache_dir}")
                return True
            except Exception as e:
                logger.error(f"Error clearing cache directory: {str(e)}")
                return False

    def list_cached_models(self) -> list:
        """List all cached models"""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        return [f.stem for f in cache_files]

    def cache_model_operation(self, model_name: str, operation_func, *args, **kwargs) -> Any:
        """
        Helper method to cache the result of an operation
        """
        cache_key = self._generate_cache_key(model_name, *args)

        # Check if result is already cached
        cached_result = self.load_from_cache(cache_key)
        if cached_result is not None:
            logger.info(f"Cache hit for {model_name}")
            return cached_result

        # Execute operation and cache the result
        logger.info(f"Cache miss for {model_name}, executing operation...")
        result = operation_func(*args, **kwargs)

        # Cache the result
        if result is not None:
            self.save_to_cache(cache_key, result)

        return result

# Example usage with sentence transformer model
def load_sentence_transformer_model(model_name: str = "all-MiniLM-L6-v2"):
    """Example function that loads a sentence transformer model"""
    from sentence_transformers import SentenceTransformer
    logger.info(f"Loading sentence transformer model: {model_name}")
    return SentenceTransformer(model_name)

if __name__ == "__main__":
    cache = ModelCache()

    # Example: Cache a model
    model_name = "all-MiniLM-L6-v2"
    cache_key = cache._generate_cache_key(model_name)

    print(f"Cache key: {cache_key}")
    print(f"Is cached: {cache.is_cached(cache_key)}")

    # Try to load from cache first
    model = cache.load_from_cache(cache_key)

    if model is None:
        print("Model not in cache, loading fresh...")
        # In a real scenario, you would load the actual model here
        # For this example, we'll create a mock model object
        mock_model = {"model_name": model_name, "loaded_at": time.time()}
        cache.save_to_cache(cache_key, mock_model)
        print("Model saved to cache")

        # Load again to test caching
        model = cache.load_from_cache(cache_key)
        print(f"Model loaded from cache: {model}")
    else:
        print(f"Model loaded from cache: {model}")

    # List cached models
    cached_models = cache.list_cached_models()
    print(f"Cached models: {cached_models}")

    # Get cache info
    cache_info = cache.get_cache_info(cache_key)
    print(f"Cache info: {cache_info}")