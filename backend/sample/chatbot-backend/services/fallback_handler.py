from typing import Optional, Dict, Any, List
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FallbackHandler:
    """
    Implements graceful failure mechanism when Qdrant is unavailable
    with user-friendly error messages as required by spec
    """

    def __init__(self):
        self.qdrant_client = None
        self.collection_name = "book_content"
        self.is_qdrant_available = False
        self.fallback_data = {}  # In-memory fallback storage for critical data

        # Initialize Qdrant client
        self._initialize_qdrant()

    def _initialize_qdrant(self):
        """Initialize Qdrant client and check availability"""
        try:
            self.qdrant_client = QdrantClient(
                url=os.getenv("QDRANT_URL", "http://localhost:6333"),
                api_key=os.getenv("QDRANT_API_KEY"),
                timeout=5.0  # Shorter timeout for availability checks
            )

            # Test connection
            self.qdrant_client.get_collections()
            self.is_qdrant_available = True
            logger.info("Qdrant connection established successfully")
        except Exception as e:
            logger.error(f"Qdrant connection failed: {str(e)}")
            self.is_qdrant_available = False

    def is_available(self) -> bool:
        """Check if Qdrant is currently available"""
        if not self.is_qdrant_available:
            return False

        try:
            # Test connection again to ensure it's still available
            self.qdrant_client.get_collections()
            return True
        except:
            self.is_qdrant_available = False
            return False

    def search_with_fallback(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search in Qdrant with fallback to alternative methods if unavailable
        """
        if self.is_available():
            try:
                # Perform normal search
                search_results = self.qdrant_client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    with_payload=True
                )

                # Format results
                results = []
                for hit in search_results:
                    result = {
                        "score": hit.score,
                        "content": hit.payload.get("content", ""),
                        "source_file": hit.payload.get("source_file", "unknown"),
                        "metadata": hit.payload.get("metadata", {})
                    }
                    results.append(result)

                return results
            except Exception as e:
                logger.error(f"Qdrant search failed: {str(e)}")
                # Fall back to alternative method
                return self._fallback_search(query_vector, top_k)
        else:
            logger.warning("Qdrant unavailable, using fallback search")
            return self._fallback_search(query_vector, top_k)

    def _fallback_search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Fallback search method when Qdrant is unavailable
        This could use alternative storage or return default responses
        """
        logger.info("Executing fallback search mechanism")

        # In a real implementation, this might:
        # 1. Search in a local database
        # 2. Use cached results
        # 3. Return default/fallback content
        # 4. Use a different vector store

        # For now, return a user-friendly error response
        fallback_results = []

        # Add a message to inform the user about the fallback
        fallback_results.append({
            "score": 1.0,
            "content": "⚠️ The knowledge base is currently unavailable. Our systems are working to restore service. Please try again later.",
            "source_file": "system_message",
            "metadata": {"type": "system_message", "fallback": True}
        })

        logger.info("Fallback search completed with system message")
        return fallback_results

    def upsert_with_fallback(self, points: List[Dict[str, Any]]) -> bool:
        """
        Upsert points to Qdrant with fallback if unavailable
        """
        if self.is_available():
            try:
                # Prepare points for Qdrant
                qdrant_points = []
                for point in points:
                    qdrant_point = models.PointStruct(
                        id=point['id'],
                        vector=point['vector'],
                        payload=point['payload']
                    )
                    qdrant_points.append(qdrant_point)

                # Perform upsert
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=qdrant_points
                )

                logger.info(f"Successfully upserted {len(points)} points to Qdrant")
                return True
            except Exception as e:
                logger.error(f"Qdrant upsert failed: {str(e)}")
                # Store in fallback storage for later processing
                self._store_fallback_points(points)
                return False
        else:
            logger.warning("Qdrant unavailable, storing points for later processing")
            # Store in fallback storage for later processing
            self._store_fallback_points(points)
            return False

    def _store_fallback_points(self, points: List[Dict[str, Any]]):
        """
        Store points in fallback storage for later processing when Qdrant is available
        """
        # In a real implementation, this might store in a local database or file
        logger.info(f"Storing {len(points)} points in fallback storage for later processing")

        # Add to in-memory fallback storage (in production, use persistent storage)
        import time
        timestamp = time.time()
        self.fallback_data[timestamp] = points

        # Log the storage action
        logger.info(f"Points stored with timestamp {timestamp} for later processing")

    def get_fallback_status(self) -> Dict[str, Any]:
        """
        Get status of fallback mechanisms
        """
        return {
            "qdrant_available": self.is_available(),
            "fallback_storage_count": len(self.fallback_data),
            "system_status": "operational_with_fallback" if not self.is_available() else "fully_operational"
        }

    def get_user_friendly_error(self) -> str:
        """
        Get a user-friendly error message for Qdrant unavailability
        """
        return (
            "The knowledge base is temporarily unavailable due to high demand or maintenance. "
            "Our AI assistant can still help answer general questions. "
            "The book content search feature will be restored shortly. "
            "Please try your query again in a few moments."
        )

    def process_fallback_data(self) -> bool:
        """
        Process any stored fallback data when Qdrant becomes available again
        """
        if not self.is_available():
            return False

        if not self.fallback_data:
            logger.info("No fallback data to process")
            return True

        logger.info(f"Processing {len(self.fallback_data)} batches of fallback data")

        success_count = 0
        for timestamp, points in self.fallback_data.items():
            try:
                if self.upsert_with_fallback(points):
                    # Remove successfully processed data
                    del self.fallback_data[timestamp]
                    success_count += 1
                    logger.info(f"Successfully processed fallback data from {timestamp}")
                else:
                    logger.warning(f"Failed to process fallback data from {timestamp}")
            except Exception as e:
                logger.error(f"Error processing fallback data from {timestamp}: {str(e)}")

        logger.info(f"Processed {success_count} batches of fallback data")
        return True

# Example usage
if __name__ == "__main__":
    fallback_handler = FallbackHandler()

    # Check status
    status = fallback_handler.get_fallback_status()
    print(f"Fallback status: {status}")

    # Example of handling a search when Qdrant might be unavailable
    sample_query_vector = [0.1] * 384  # 384-dim vector
    results = fallback_handler.search_with_fallback(sample_query_vector, top_k=3)
    print(f"Search results: {results}")

    # Get user-friendly error if needed
    if not fallback_handler.is_available():
        error_msg = fallback_handler.get_user_friendly_error()
        print(f"User-friendly error: {error_msg}")