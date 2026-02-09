import os
import glob
from typing import List, Dict, Any
import markdown
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Context7Processor:
    """
    Implements context7-Mcp utility for document processing from Phase-2 Chatbot using Nextjs/docs/
    as required by spec DIP.1
    """

    def __init__(self, docs_path: str = "Phase-2 Chatbot using Nextjs/docs"):
        self.docs_path = docs_path
        self.supported_extensions = ['.md', '.markdown']

    def discover_documents(self) -> List[str]:
        """Discover all markdown documents in the docs directory"""
        documents = []

        for ext in self.supported_extensions:
            pattern = os.path.join(self.docs_path, f"**/*{ext}")
            files = glob.glob(pattern, recursive=True)
            documents.extend(files)

        logger.info(f"Discovered {len(documents)} documents in {self.docs_path}")
        return documents

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from the file path and content"""
        path_obj = Path(file_path)

        # Extract basic metadata from file path
        metadata = {
            'file_path': str(path_obj),
            'file_name': path_obj.name,
            'relative_path': str(path_obj.relative_to(self.docs_path)),
            'directory': str(path_obj.parent.relative_to(self.docs_path)),
            'extension': path_obj.suffix,
            'size': path_obj.stat().st_size,
            'modified': path_obj.stat().st_mtime
        }

        return metadata

    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single document using context7-Mcp utility principles"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract metadata
            metadata = self.extract_metadata(file_path)

            # Convert markdown to HTML for better text extraction
            html_content = markdown.markdown(content)

            # Simple chunking strategy - split by paragraphs while preserving context
            paragraphs = content.split('\n\n')

            chunks = []
            chunk_size_limit = 1000  # characters per chunk

            current_chunk = ""
            current_chunk_metadata = metadata.copy()

            for para in paragraphs:
                # If adding this paragraph would exceed the limit, save the current chunk
                if len(current_chunk + para) > chunk_size_limit and current_chunk:
                    # Create a chunk with content and metadata
                    chunk_data = {
                        'content': current_chunk.strip(),
                        'metadata': current_chunk_metadata,
                        'source_file': file_path
                    }
                    chunks.append(chunk_data)

                    # Start a new chunk with the current paragraph
                    current_chunk = para + "\n\n"
                else:
                    # Add paragraph to current chunk
                    current_chunk += para + "\n\n"

            # Add the last chunk if it has content
            if current_chunk.strip():
                chunk_data = {
                    'content': current_chunk.strip(),
                    'metadata': metadata,
                    'source_file': file_path
                }
                chunks.append(chunk_data)

            logger.info(f"Processed {file_path} into {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return []

    def process_all_documents(self) -> List[Dict[str, Any]]:
        """Process all documents in the docs directory"""
        all_chunks = []
        documents = self.discover_documents()

        for doc_path in documents:
            chunks = self.process_document(doc_path)
            all_chunks.extend(chunks)

        logger.info(f"Total processed chunks: {len(all_chunks)}")
        return all_chunks

# Example usage
if __name__ == "__main__":
    processor = Context7Processor()
    chunks = processor.process_all_documents()
    print(f"Processed {len(chunks)} total chunks from documents")

    # Print first chunk as example
    if chunks:
        print("\nFirst chunk example:")
        print(f"Content preview: {chunks[0]['content'][:100]}...")
        print(f"Metadata: {chunks[0]['metadata']}")