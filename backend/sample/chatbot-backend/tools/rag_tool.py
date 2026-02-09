from typing import Dict, List, Any, Optional
import logging
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 💡 FIX: Define the local path to the cached model
# The model is usually cached under: ~/.cache/huggingface/hub/models--<repo_id>
# os.path.expanduser('~') resolves to C:\Users\Aksystems on Windows
LOCAL_MODEL_DIR = os.path.expanduser(r'~\.cache\huggingface/hub\models--sentence-transformers--all-MiniLM-L6-v2\c9745ed1d9f207416be6d2e6f8de32d1f16199bf') 
# The actual files are nested inside a 'snapshots' folder, so we check if the base folder exists.

class RAGSearchInput(BaseModel):
    query: str = Field(..., description="The search query to find relevant book content")
    top_k: int = Field(default=5, description="Number of top results to return")

class RAGTool(BaseTool):
    """
    Custom Agent Tool that interfaces with Qdrant for vector database retrieval.
    """
    name: str = "rag_search_tool"
    description: str = "Search for relevant book content using vector similarity"
    args_schema: type = RAGSearchInput

    # Define class attributes to ensure they exist
    embedding_model: Any = SentenceTransformer
    qdrant_client: Any = QdrantClient
    collection_name: str = ""

    def __init__(self):
        logger.info("RAGTool: Starting __init__ process.")

        # 1. Initialize parent class
        try:
            super().__init__()
            logger.info("RAGTool: super().__init__() completed.")
        except Exception as e:
            logger.error(f"RAGTool: Error during super().__init__: {str(e)}")
            raise

        # Initialize attributes to None initially
        self.embedding_model = None
        self.qdrant_client = None
        self.collection_name = ""

        # 2. Initialize embedding model (FIX APPLIED HERE)
        try:
            model_path = "all-MiniLM-L6-v2"

            # Check if the local cache path exists (files are already downloaded)
            if os.path.exists(LOCAL_MODEL_DIR):
                # 💡 Use the local directory path to force loading from disk
                # SentenceTransformer can be initialized with a local path containing config.json
                # This should bypass the network/low-level issue.
                model_path = LOCAL_MODEL_DIR
                logger.info(f"RAGTool: Loading embedding model from local cache: {model_path}")
            else:
                logger.warning(f"RAGTool: Local cache not found at {LOCAL_MODEL_DIR}. Attempting remote load.")

            self.embedding_model = SentenceTransformer(model_path)
            logger.info("RAGTool: embedding_model initialized successfully.")

        except Exception as e:
            # We explicitly check for this now
            logger.error(f"RAGTool: FATAL Error initializing SentenceTransformer: {str(e)}")
            logger.error("The local path might be incorrect, files corrupted, or a PyTorch dependency is missing.")
            raise # Re-raise to crash initialization

        # 3. Initialize Qdrant client
        try:
            self.qdrant_client = QdrantClient(
                url=os.getenv("QDRANT_URL", "http://localhost:6333"),
                api_key=os.getenv("QDRANT_API_KEY"),
                timeout=10.0
            )
            self.collection_name = "book_content"
            logger.info("RAGTool: Qdrant client initialized successfully.")
        except Exception as e:
            logger.error(f"RAGTool: Error initializing Qdrant client: {str(e)}")
            logger.error("Please verify QDRANT_URL and QDRANT_API_KEY environment variables.")
            raise # Re-raise to crash initialization

    def _run(self, query: str, top_k: int = 5) -> str:
        """Execute the RAG search"""
        try:
            # Check if initialization failed silently before proceeding
            if self.embedding_model is None:
                raise RuntimeError("Embedding model failed to load during initialization.")

            # Generate embedding for the query
            query_embedding = self.embedding_model.encode([query])[0].tolist()

            # Validate embedding dimension (should be 384 for all-MiniLM-L6-v2)
            if len(query_embedding) != 384:
                raise ValueError(f"Query embedding dimension mismatch: expected 384, got {len(query_embedding)}")

            # Check if Qdrant client is available
            if self.qdrant_client is None:
                raise RuntimeError("Qdrant client failed to initialize.")

            # Search in Qdrant collection - try multiple API approaches
            search_results = None

            # Try different possible method names and API structures
            if hasattr(self.qdrant_client, 'search') and callable(getattr(self.qdrant_client, 'search')):
                # Standard approach for current qdrant-client versions
                search_results = self.qdrant_client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=top_k,
                    with_payload=True,
                    search_params=models.SearchParams(
                       hnsw_ef=256
                    )
                )
            elif hasattr(self.qdrant_client, 'search_points') and callable(getattr(self.qdrant_client, 'search_points')):
                # Alternative method name for older versions
                search_results = self.qdrant_client.search_points(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=top_k,
                    with_payload=True,
                    search_params=models.SearchParams(
                       hnsw_ef=256
                    )
                )
            elif hasattr(self.qdrant_client, 'grpc_points_client') and self.qdrant_client.grpc_points_client is not None:
                # Try gRPC-based approach
                from qdrant_client.http import models as http_models
                search_result = self.qdrant_client.grpc_points_client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=top_k,
                    with_payload=True,
                    search_params=models.SearchParams(
                       hnsw_ef=256
                    )
                )
                search_results = search_result
            elif hasattr(self.qdrant_client, 'http') and hasattr(self.qdrant_client.http, 'search_api'):
                # Try HTTP API approach - use the search_api which has search_points method
                from qdrant_client.http import models as http_models
                search_response = self.qdrant_client.http.search_api.search_points(
                    collection_name=self.collection_name,
                    consistency=None,
                    timeout=None,
                    search_request=http_models.SearchRequest(
                        vector=query_embedding,
                        limit=top_k,
                        with_payload=True,
                        params=http_models.SearchParams(
                           hnsw_ef=256
                        )
                    )
                )
                # Extract the results from the response
                search_results = search_response.result
            else:
                # If none of the common approaches work, try to introspect the client
                available_methods = [method for method in dir(self.qdrant_client) if 'search' in method.lower() or 'find' in method.lower()]
                raise RuntimeError(f"Qdrant client has no recognizable search method. Available search-related methods: {available_methods}")

            # Format results - handle different result types based on API used
            formatted_results = []
            if search_results is not None:
                for hit in search_results:
                    # Handle different result types depending on which API was used
                    if hasattr(hit, 'payload') and hasattr(hit, 'score'):
                        # Standard search result from high-level client
                        score = getattr(hit, 'score', 0.0)
                        raw_payload = getattr(hit, 'payload', {})
                        # Ensure payload is a dictionary
                        if hasattr(raw_payload, '__dict__'):
                            # If payload is an object, convert to dict
                            payload = raw_payload.__dict__ if hasattr(raw_payload, '__dict__') else {}
                        else:
                            payload = raw_payload if isinstance(raw_payload, dict) else {}
                    elif hasattr(hit, 'payload') and hasattr(hit, 'id'):
                        # SearchResult from HTTP API
                        score = getattr(hit, 'score', 0.0)
                        raw_payload = getattr(hit, 'payload', {})
                        payload = raw_payload if isinstance(raw_payload, dict) else {}
                    elif hasattr(hit, 'document'):
                        # Some result formats
                        score = getattr(hit, 'score', 0.0)
                        raw_payload = getattr(hit, 'document', {}).get('payload', {}) if hasattr(hit, 'document') else {}
                        payload = raw_payload if isinstance(raw_payload, dict) else {}
                    else:
                        # Fallback for other structures
                        score = getattr(hit, 'score', 0.0)
                        raw_payload = getattr(hit, 'payload', {})
                        payload = raw_payload if isinstance(raw_payload, dict) else {}

                    result = {
                        "score": score,
                        "content": payload.get("content", "")[:500],  # Limit content length
                        "source_file": payload.get("source_file", "unknown"),
                        "metadata": payload.get("metadata", {})
                    }
                    formatted_results.append(result)

            # Return list of dictionaries, not a string
            return formatted_results

        except Exception as e:
            logger.error(f"Error in RAG search: {str(e)}")
            # Return empty list instead of string to match expected format
            return []

    async def _arun(self, query: str, top_k: int = 5) -> list:
        """Async version of the RAG search"""
        return self._run(query, top_k)

