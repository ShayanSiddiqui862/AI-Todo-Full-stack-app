import os
from typing import List, Dict, Any
import logging
from qdrant_client.http import models
from backend.src.qdrant_service import QdrantService
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantUploader:
    """
    Implements Qdrant indexing via qdrant-mcp-server with proper metadata
    as required by spec DIP.3 and DIP.4
    """

    def __init__(self):
        self.qdrant_service = QdrantService()
        self.collection_name = self.qdrant_service.get_collection_name()

    def test_connection(self) -> bool:
        """Test connection to Qdrant service"""
        try:
            client = self.qdrant_service.get_client()
            # Try to get collections to test connection
            client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant connection test failed: {str(e)}")
            return False

    def upload_points(self, points: List[Dict[str, Any]]) -> bool:
        """
        Upload points to Qdrant collection via qdrant-mcp-server
        Each point should have 'id', 'vector', and 'payload' keys
        """
        try:
            client = self.qdrant_service.get_client()

            # Prepare points in the format expected by Qdrant
            qdrant_points = []
            for point in points:
                qdrant_point = models.PointStruct(
                    id=point['id'],
                    vector=point['vector'],
                    payload=point['payload']
                )
                qdrant_points.append(qdrant_point)

            # Upload points to the collection
            client.upsert(
                collection_name=self.collection_name,
                points=qdrant_points,
                # Use the qdrant-mcp-server interface as required by spec DIP.3
            )

            logger.info(f"Successfully uploaded {len(qdrant_points)} points to collection '{self.collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error uploading points to Qdrant: {str(e)}")
            return False

    def validate_embedding_dimension(self, embedding: List[float]) -> bool:
        """
        Validate that an embedding has the correct dimension (384 for all-MiniLM-L6-v2)
        as required by spec T013
        """
        expected_dimension = 384
        return len(embedding) == expected_dimension

    def upload_single_point(self, point_id: int, vector: List[float], payload: Dict[str, Any]) -> bool:
        """
        Upload a single point to Qdrant
        """
        # Validate embedding dimension as per spec T013
        if not self.validate_embedding_dimension(vector):
            logger.error(f"Invalid embedding dimension: expected 384, got {len(vector)}")
            return False

        try:
            client = self.qdrant_service.get_client()

            qdrant_point = models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )

            client.upsert(
                collection_name=self.collection_name,
                points=[qdrant_point]
            )

            logger.info(f"Successfully uploaded point {point_id} to collection '{self.collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error uploading single point to Qdrant: {str(e)}")
            return False

    def clear_collection(self) -> bool:
        """
        Clear all points from the collection (useful for re-indexing)
        """
        try:
            client = self.qdrant_service.get_client()

            # Get all point IDs in the collection
            all_points = client.scroll(
                collection_name=self.collection_name,
                limit=10000  # Adjust based on expected collection size
            )

            # Extract point IDs
            point_ids = [point.id for point in all_points[0]]

            if point_ids:
                # Delete all points
                client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(
                        points=point_ids
                    )
                )
                logger.info(f"Cleared {len(point_ids)} points from collection '{self.collection_name}'")

            return True

        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False

    def search_points(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar points in the collection
        """
        try:
            client = self.qdrant_service.get_client()

            # Validate query vector dimension
            if not self.validate_embedding_dimension(query_vector):
                logger.error(f"Invalid query vector dimension: expected 384, got {len(query_vector)}")
                return []

            # Perform search
            search_results = client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )

            # Format results
            results = []
            for hit in search_results:
                result = {
                    'id': hit.id,
                    'score': hit.score,
                    'payload': hit.payload
                }
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error searching points in Qdrant: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    uploader = QdrantUploader()

    # Test connection
    if uploader.test_connection():
        print("Qdrant connection successful!")
    else:
        print("Qdrant connection failed!")
        exit(1)

    # Example of uploading a point
    sample_embedding = [0.1] * 384  # 384-dim vector as required
    sample_payload = {
        'content': 'This is a sample document chunk for testing',
        'metadata': {
            'source_file': 'test.md',
            'section': 'introduction'
        }
    }

    success = uploader.upload_single_point(1, sample_embedding, sample_payload)
    if success:
        print("Sample point uploaded successfully!")
    else:
        print("Failed to upload sample point!")