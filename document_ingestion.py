import chromadb
from openai import OpenAI
from pathlib import Path
import logging
from document_processor import DocumentProcessor

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIngestion:
    """Handles document processing and ingestion into the vector store."""
    
    def __init__(self, openai_client, chroma_collection, embedding_model, 
                 chunk_size=1000, chunk_overlap=200, max_file_size_mb=50, 
                 supported_extensions=None):
        """
        Initialize the document ingestion system.
        
        Args:
            openai_client: OpenAI client instance
            chroma_collection: Chroma collection instance
            embedding_model: OpenAI embedding model name
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            max_file_size_mb: Maximum file size in MB
            supported_extensions: List of supported file extensions
        """
        self.client = openai_client
        self.collection = chroma_collection
        self.embedding_model = embedding_model
        
        # Set default supported extensions if not provided
        if supported_extensions is None:
            supported_extensions = [".pdf", ".docx", ".xlsx", ".xls"]
        
        # Initialize document processor with configuration
        self.doc_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_file_size_mb=max_file_size_mb,
            supported_extensions=supported_extensions
        )
    
    def get_embedding(self, text: str) -> list:
        """Get embedding for text using OpenAI."""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None
    
    def add_document_chunks(self, chunks: list, metadata: dict) -> dict:
        """Add processed document chunks to the vector store."""
        try:
            chunks_added = 0
            
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                
                # Get embedding
                embedding = self.get_embedding(chunk)
                if embedding is None:
                    continue
                
                # Create unique document ID
                doc_id = f"{Path(metadata['filename']).stem}_{i}"
                
                # Add to collection
                self.collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        **metadata,
                        "chunk_id": i
                    }],
                    ids=[doc_id]
                )
                chunks_added += 1
            print(f"Added {chunks_added} chunks from {metadata['filename']}")
            logger.info(f"Added {chunks_added} chunks from {metadata['filename']}")
            return {
                "success": True,
                "chunks_added": chunks_added,
                "message": f"Successfully added {chunks_added} chunks"
            }
            
        except Exception as e:
            logger.error(f"Error adding document chunks: {e}")
            return {
                "success": False,
                "chunks_added": 0,
                "message": f"Error adding chunks: {str(e)}"
            }
    
    def process_and_add_document(self, file_path: str) -> dict:
        """Process a document and add it to the vector store."""
        # Use document processor to extract and chunk
        processing_result = self.doc_processor.process_file(file_path)
        
        if not processing_result["success"]:
            return processing_result
        
        # Add chunks to vector store
        add_result = self.add_document_chunks(
            processing_result["chunks"], 
            processing_result["metadata"]
        )
        
        return {
            "success": add_result["success"],
            "message": add_result["message"],
            "chunks_added": add_result["chunks_added"],
            "file_metadata": processing_result["metadata"]
        }
    
    def process_and_add_folder(self, folder_path: str) -> dict:
        """Process all documents in a folder and add them to the vector store."""
        # Use document processor
        processing_result = self.doc_processor.process_folder(folder_path)
        
        if not processing_result["success"]:
            return processing_result
        
        total_chunks_added = 0
        successful_files = []
        failed_files = list(processing_result["failed_files"])  # Copy existing failures
        
        # Process each successfully extracted file
        for file_data in processing_result["processed_files"]:
            add_result = self.add_document_chunks(
                file_data["chunks"], 
                file_data["metadata"]
            )
            
            if add_result["success"]:
                total_chunks_added += add_result["chunks_added"]
                successful_files.append({
                    "file_path": file_data["file_path"],
                    "chunks_added": add_result["chunks_added"],
                    "metadata": file_data["metadata"]
                })
            else:
                failed_files.append({
                    "file_path": file_data["file_path"],
                    "error": add_result["message"],
                    "metadata": file_data["metadata"]
                })
        
        return {
            "success": True,
            "message": f"Processed {len(successful_files)} files, added {total_chunks_added} chunks",
            "files_processed": len(successful_files),
            "total_chunks_added": total_chunks_added,
            "successful_files": successful_files,
            "failed_files": failed_files
        } 