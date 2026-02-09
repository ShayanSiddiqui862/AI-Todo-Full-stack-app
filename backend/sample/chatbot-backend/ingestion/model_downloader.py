import os
import requests
from pathlib import Path
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelDownloader:
    """
    Implements Hugging Face model download function to fetch sentence-transformer/all-MiniLM-L6-V2 model
    with caching as required by spec
    """

    def __init__(self, cache_dir: str = "models"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"

    def download_model(self, force_download: bool = False) -> str:
        """
        Download the model from Hugging Face Hub with caching
        Returns the path to the downloaded model
        """
        model_path = self.cache_dir / self.model_name.replace("/", "_")

        # Check if model already exists in cache
        if model_path.exists() and not force_download:
            logger.info(f"Model already exists in cache: {model_path}")
            return str(model_path)

        try:
            logger.info(f"Downloading model {self.model_name} to {model_path}")

            # Download the model using Hugging Face Hub
            snapshot_path = snapshot_download(
                repo_id=self.model_name,
                cache_dir=str(self.cache_dir),
                local_dir=str(model_path),
                local_dir_use_symlinks=False  # Avoid symlinks for portability
            )

            logger.info(f"Model downloaded successfully to {snapshot_path}")
            return snapshot_path

        except Exception as e:
            logger.error(f"Error downloading model {self.model_name}: {str(e)}")
            raise

    def check_model_availability(self) -> bool:
        """Check if the model is available on Hugging Face Hub"""
        try:
            from huggingface_hub import model_info
            info = model_info(self.model_name)
            return info.id == self.model_name
        except Exception:
            return False

    def get_cached_model_path(self) -> str:
        """Get the path where the model would be cached"""
        model_path = self.cache_dir / self.model_name.replace("/", "_")
        return str(model_path)

    def download_tokenizer_and_model(self) -> tuple:
        """
        Download both tokenizer and model separately (alternative approach)
        Returns (tokenizer_path, model_path)
        """
        tokenizer_path = self.cache_dir / f"{self.model_name.replace('/', '_')}_tokenizer"
        model_path = self.cache_dir / f"{self.model_name.replace('/', '_')}_model"

        try:
            # Download tokenizer
            logger.info(f"Downloading tokenizer for {self.model_name}")
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            tokenizer.save_pretrained(tokenizer_path)

            # Download model
            logger.info(f"Downloading model {self.model_name}")
            model = AutoModel.from_pretrained(self.model_name)
            model.save_pretrained(model_path)

            logger.info(f"Tokenizer saved to: {tokenizer_path}")
            logger.info(f"Model saved to: {model_path}")

            return str(tokenizer_path), str(model_path)

        except Exception as e:
            logger.error(f"Error downloading tokenizer and model: {str(e)}")
            raise

def download_hf_model_if_needed(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> str:
    """
    Convenience function to download the model if needed
    """
    downloader = ModelDownloader()
    return downloader.download_model()

if __name__ == "__main__":
    # Example usage
    downloader = ModelDownloader()

    # Check if model is available
    if downloader.check_model_availability():
        print(f"Model {downloader.model_name} is available on Hugging Face Hub")

        # Download the model
        model_path = downloader.download_model()
        print(f"Model downloaded to: {model_path}")

        # Get cached path
        cached_path = downloader.get_cached_model_path()
        print(f"Cached model path: {cached_path}")
    else:
        print(f"Model {downloader.model_name} is not available on Hugging Face Hub")