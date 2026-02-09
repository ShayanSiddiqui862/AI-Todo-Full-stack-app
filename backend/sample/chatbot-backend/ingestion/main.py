import os
import sys
from typing import List, Dict, Any
import logging
from pathlib import Path

# Add the parent directory to the path to import other modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ingestion.context7_processor import Context7Processor
from ingestion.embedding import EmbeddingService
from ingestion.qdrant_uploader import QdrantUploader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIngestionPipeline:
    """
    Implements the complete document ingestion pipeline with metadata extraction
    including section/chapter information from context7-Mcp as required by spec
    """

    def __init__(self, docs_path: str = "Phase-2 Chatbot using Nextjs/docs",
                 model_name: str = "all-MiniLM-L6-v2"):
        self.docs_path = docs_path
        self.processor = Context7Processor(docs_path)
        self.embedding_service = EmbeddingService(model_name)
        self.qdrant_uploader = QdrantUploader()

        # Validate that embedding dimension is correct (spec T013)
        if self.embedding_service.get_embedding_dimension() != 384:
            raise ValueError("Embedding dimension must be 384 as per spec DIP.2")

    def run_ingestion_pipeline(self) -> bool:
        """
        Execute the complete ingestion pipeline:
        1. Process documents using context7-Mcp utility
        2. Generate embeddings using sentence-transformer model
        3. Upload to Qdrant via qdrant-mcp-server
        """
        try:
            logger.info("Starting document ingestion pipeline...")

            # Step 1: Process documents using context7-Mcp utility
            logger.info("Step 1: Processing documents with context7-Mcp utility...")
            chunks = self.processor.process_all_documents()

            if not chunks:
                logger.warning("No documents were processed. Check if docs directory has content.")
                return False

            logger.info(f"Processed {len(chunks)} document chunks")

            # Step 2: Generate embeddings for all chunks
            logger.info("Step 2: Generating embeddings...")

            # Extract content from chunks for batch processing
            contents = [chunk['content'] for chunk in chunks]

            # Generate embeddings in batch for efficiency
            embeddings = self.embedding_service.embed_texts(contents)

            logger.info(f"Generated {len(embeddings)} embeddings")

            # Step 3: Upload to Qdrant via qdrant-mcp-server with metadata
            logger.info("Step 3: Uploading to Qdrant via qdrant-mcp-server...")

            # Prepare points for Qdrant upload
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point = {
                    'id': i,
                    'vector': embedding,
                    'payload': {
                        'content': chunk['content'],
                        'metadata': chunk['metadata'],
                        'source_file': chunk['source_file']
                    }
                }
                points.append(point)

            # Upload to Qdrant
            success = self.qdrant_uploader.upload_points(points)

            if success:
                logger.info(f"Successfully uploaded {len(points)} points to Qdrant")
            else:
                logger.error("Failed to upload points to Qdrant")
                return False

            logger.info("Document ingestion pipeline completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Error in ingestion pipeline: {str(e)}")
            return False

    def validate_pipeline(self) -> Dict[str, Any]:
        """
        Validate the pipeline components and return status
        """
        validation_results = {
            'docs_path_exists': os.path.exists(self.docs_path),
            'docs_path_readable': os.access(self.docs_path, os.R_OK),
            'embedding_service_loaded': self.embedding_service.model is not None,
            'qdrant_connection': self.qdrant_uploader.test_connection(),
            'expected_embedding_dimension': self.embedding_service.get_embedding_dimension(),
            'documents_count': len(self.processor.discover_documents()) if os.path.exists(self.docs_path) else 0
        }

        # Validate embedding dimension as per spec T013
        validation_results['correct_embedding_dimension'] = (
            validation_results['expected_embedding_dimension'] == 384
        )

        return validation_results

def main():
    """Main function to run the ingestion pipeline"""
    try:
        # Create the ingestion pipeline
        pipeline = DocumentIngestionPipeline()

        # Validate the pipeline before running
        validation_results = pipeline.validate_pipeline()
        logger.info(f"Validation results: {validation_results}")

        if not validation_results['docs_path_exists']:
            logger.error(f"Docs path does not exist: {pipeline.docs_path}")
            return False

        if validation_results['documents_count'] == 0:
            logger.warning(f"No documents found in {pipeline.docs_path}")
            return False

        # Run the ingestion pipeline
        success = pipeline.run_ingestion_pipeline()

        if success:
            logger.info("Ingestion pipeline completed successfully!")
            return True
        else:
            logger.error("Ingestion pipeline failed!")
            return False

    except Exception as e:
        logger.error(f"Error in main ingestion pipeline: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("Document ingestion pipeline completed successfully!")
    else:
        print("Document ingestion pipeline failed!")
        sys.exit(1)