import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

load_dotenv()

class QdrantService:
    def __init__(self):
        # Initialize Qdrant client using qdrant-mcp-server interface as required by spec
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=10.0
        )
        self.collection_name = "book_content"

    def create_collection(self):
        """Create persistent collection in Qdrant Cloud as per spec DIP.4"""
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection with 384 dimensions for all-MiniLM-L6-v2 model
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=384,  # 384-dim vectors from all-MiniLM-L6-v2 model as per spec DIP.2
                        distance=models.Distance.COSINE
                    )
                )
                print(f"Collection '{self.collection_name}' created successfully.")
            else:
                print(f"Collection '{self.collection_name}' already exists.")

            # Configure collection for persistent storage
            self.client.update_collection(
                collection_name=self.collection_name,
                optimizer_config=models.OptimizersConfigDiff(
                    vacuum_min_vector_number=1000,
                    indexing_threshold=20000,
                )
            )
            return True
        except Exception as e:
            print(f"Error creating collection: {str(e)}")
            return False

    def get_client(self):
        return self.client

    def get_collection_name(self):
        return self.collection_name

# For testing purposes
if __name__ == "__main__":
    qdrant_service = QdrantService()
    qdrant_service.create_collection()