import torch
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Implements embedding pipeline using sentence-transformer/all-MiniLM-L6-V2 model
    as required by spec DIP.2 - produces 384-dim vectors
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # all-MiniLM-L6-v2 produces 384-dim vectors as per spec DIP.2
        self.load_model()

    def load_model(self):
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully. Embedding dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {str(e)}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not self.model:
            raise ValueError("Model not loaded")

        # Generate embedding
        embedding = self.model.encode([text])[0]

        # Convert to list and validate dimensions
        embedding_list = embedding.tolist()

        # Validate embedding dimensions as per spec T013
        if len(embedding_list) != self.dimension:
            raise ValueError(f"Embedding dimension mismatch: expected {self.dimension}, got {len(embedding_list)}")

        return embedding_list

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self.model:
            raise ValueError("Model not loaded")

        # Generate embeddings for all texts at once for efficiency
        embeddings = self.model.encode(texts)

        # Convert to list of lists and validate dimensions
        embeddings_list = []
        for embedding in embeddings:
            embedding_list = embedding.tolist()

            # Validate embedding dimensions as per spec T013
            if len(embedding_list) != self.dimension:
                raise ValueError(f"Embedding dimension mismatch: expected {self.dimension}, got {len(embedding_list)}")

            embeddings_list.append(embedding_list)

        return embeddings_list

    def validate_embedding(self, embedding: List[float]) -> bool:
        """Validate that an embedding has the correct dimensions"""
        return len(embedding) == self.dimension

    def get_embedding_dimension(self) -> int:
        """Get the expected embedding dimension"""
        return self.dimension

# Example usage
if __name__ == "__main__":
    # Initialize the embedding service
    embedding_service = EmbeddingService()

    # Test single text embedding
    test_text = "This is a test sentence for embedding."
    embedding = embedding_service.embed_text(test_text)
    print(f"Single embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

    # Test multiple texts embedding
    test_texts = [
        "First test sentence.",
        "Second test sentence.",
        "Third test sentence about artificial intelligence and machine learning."
    ]

    embeddings = embedding_service.embed_texts(test_texts)
    print(f"\nMultiple embeddings count: {len(embeddings)}")
    print(f"Each embedding length: {len(embeddings[0]) if embeddings else 0}")

    # Validate dimensions
    for i, emb in enumerate(embeddings):
        is_valid = embedding_service.validate_embedding(emb)
        print(f"Embedding {i} valid: {is_valid}")

    # Test with a chunk from the processor
    # Note: This would typically be used with chunks from context7_processor.py
    sample_chunk = {
        'content': "The field of artificial intelligence encompasses machine learning, deep learning, and neural networks. These technologies are transforming industries and creating new possibilities for automation and decision-making.",
        'metadata': {'source': 'test_document.md', 'section': 'introduction'},
        'source_file': 'test.md'
    }

    chunk_embedding = embedding_service.embed_text(sample_chunk['content'])
    print(f"\nSample chunk embedding length: {len(chunk_embedding)}")
    print(f"Validates correctly: {embedding_service.validate_embedding(chunk_embedding)}")