import os
import fitz  # PyMuPDF
import pandas as pd
from docx import Document as DocxDocument
from pathlib import Path
import logging

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document text extraction and chunking."""
    
    def __init__(self, chunk_size=1000, chunk_overlap=200, max_file_size_mb=50, supported_extensions=None):
        """
        Initialize the document processor with configuration settings.
        
        Args:
            chunk_size: Size of text chunks (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
            max_file_size_mb: Maximum file size in MB (default: 50)
            supported_extensions: List of supported file extensions (default: [".pdf", ".docx", ".xlsx", ".xls"])
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_file_size_mb = max_file_size_mb
        self.supported_extensions = supported_extensions or [".pdf", ".docx", ".xlsx", ".xls"]
    
    def extract_text_from_file(self, file_path: str) -> dict:
        """
        Extract text from different file types.
        
        Args:
            file_path: Path to the file to extract text from
            
        Returns:
            dict: Contains success status, text content, and metadata
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            return {
                "success": False,
                "text": "",
                "error": f"File not found: {file_path}",
                "metadata": {}
            }
        
        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            return {
                "success": False,
                "text": "",
                "error": f"File too large: {file_size_mb:.1f}MB (max: {self.max_file_size_mb}MB)",
                "metadata": {"file_size_mb": file_size_mb}
            }
        
        # Check supported extensions
        if file_path.suffix.lower() not in self.supported_extensions:
            return {
                "success": False,
                "text": "",
                "error": f"Unsupported file type: {file_path.suffix}",
                "metadata": {"file_extension": file_path.suffix}
            }
        
        text = ""
        metadata = {
            "filename": file_path.name,
            "file_path": str(file_path),
            "file_size_mb": file_size_mb,
            "file_extension": file_path.suffix.lower()
        }
        
        try:
            if file_path.suffix.lower() == '.pdf':
                text = self._extract_from_pdf(file_path)
            elif file_path.suffix.lower() == '.docx':
                text = self._extract_from_docx(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                text = self._extract_from_excel(file_path)
            
            if not text.strip():
                return {
                    "success": False,
                    "text": "",
                    "error": f"No text content extracted from {file_path.name}",
                    "metadata": metadata
                }
            
            metadata["text_length"] = len(text)
            
            return {
                "success": True,
                "text": text,
                "error": None,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return {
                "success": False,
                "text": "",
                "error": f"Extraction error: {str(e)}",
                "metadata": metadata
            }
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        text = ""
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        text = ""
        doc = DocxDocument(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _extract_from_excel(self, file_path: Path) -> str:
        """Extract text from Excel file."""
        text = ""
        df = pd.read_excel(file_path, sheet_name=None)
        for sheet_name, sheet_df in df.items():
            text += f"\n--- {sheet_name} ---\n"
            text += sheet_df.to_string(index=False) + "\n"
        return text
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> list:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk (uses config default if None)
            overlap: Overlap between chunks (uses config default if None)
            
        Returns:
            list: List of text chunks
        """
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence or word boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_space = chunk.rfind(' ')
                if last_period > chunk_size * 0.8:
                    end = start + last_period + 1
                elif last_space > chunk_size * 0.8:
                    end = start + last_space
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(chunk_text)
            
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def process_file(self, file_path: str) -> dict:
        """
        Process a single file: extract text and chunk it.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            dict: Processing results with chunks and metadata
        """
        # Extract text
        extraction_result = self.extract_text_from_file(file_path)
        
        if not extraction_result["success"]:
            return {
                "success": False,
                "chunks": [],
                "metadata": extraction_result["metadata"],
                "error": extraction_result["error"]
            }
        
        # Chunk text
        try:
            chunks = self.chunk_text(extraction_result["text"])
            
            return {
                "success": True,
                "chunks": chunks,
                "metadata": {
                    **extraction_result["metadata"],
                    "chunk_count": len(chunks),
                    "average_chunk_size": sum(len(chunk) for chunk in chunks) / len(chunks) if chunks else 0
                },
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error chunking text from {file_path}: {e}")
            return {
                "success": False,
                "chunks": [],
                "metadata": extraction_result["metadata"],
                "error": f"Chunking error: {str(e)}"
            }
    
    def process_folder(self, folder_path: str) -> dict:
        """
        Process all supported files in a folder.
        
        Args:
            folder_path: Path to the folder containing documents
            
        Returns:
            dict: Processing results for all files
        """
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            return {
                "success": False,
                "processed_files": [],
                "failed_files": [],
                "total_chunks": 0,
                "error": f"Folder not found: {folder_path}"
            }
        
        if not folder_path.is_dir():
            return {
                "success": False,
                "processed_files": [],
                "failed_files": [],
                "total_chunks": 0,
                "error": f"Path is not a directory: {folder_path}"
            }
        
        processed_files = []
        failed_files = []
        total_chunks = 0
        
        # Find all supported files
        supported_files = []
        for ext in self.supported_extensions:
            supported_files.extend(folder_path.rglob(f"*{ext}"))
        
        if not supported_files:
            return {
                "success": True,
                "processed_files": [],
                "failed_files": [],
                "total_chunks": 0,
                "error": f"No supported files found in {folder_path}"
            }
        
        # Process each file
        for file_path in supported_files:
            logger.info(f"Processing file: {file_path}")
            print(f"Text Chunking - Processing file: {file_path}")
            result = self.process_file(str(file_path))
            
            if result["success"]:
                processed_files.append({
                    "file_path": str(file_path),
                    "chunks": result["chunks"],
                    "metadata": result["metadata"]
                })
                logger.info(f"metadata: {result['metadata']}")
                total_chunks += len(result["chunks"])
            else:
                failed_files.append({
                    "file_path": str(file_path),
                    "error": result["error"],
                    "metadata": result["metadata"]
                })
        
        return {
            "success": True,
            "processed_files": processed_files,
            "failed_files": failed_files,
            "total_chunks": total_chunks,
            "error": None
        }

def main():
    """Command line interface for document processing."""
    import argparse
    from config import Config
    
    parser = argparse.ArgumentParser(description="Document Processing Tool")
    parser.add_argument("action", choices=["file", "folder"], help="Process a single file or folder")
    parser.add_argument("path", help="Path to file or folder to process")
    parser.add_argument("--output", help="Output file to save results (optional)")
    
    args = parser.parse_args()
    
    # Initialize processor with configuration
    processor = DocumentProcessor(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        max_file_size_mb=Config.MAX_FILE_SIZE_MB,
        supported_extensions=Config.SUPPORTED_EXTENSIONS
    )
    
    print(f"🔧 Document Processor")
    print(f"Action: {args.action}")
    print(f"Path: {args.path}")
    print(f"Chunk Size: {processor.chunk_size}")
    print(f"Chunk Overlap: {processor.chunk_overlap}")
    print("=" * 50)
    
    # Process based on action
    if args.action == "file":
        result = processor.process_file(args.path)
        
        if result["success"]:
            print(f"✅ Successfully processed {result['metadata']['filename']}")
            print(f"📊 Generated {len(result['chunks'])} chunks")
            print(f"📏 Average chunk size: {result['metadata']['average_chunk_size']:.0f} characters")
        else:
            print(f"❌ Failed to process file: {result['error']}")
    
    elif args.action == "folder":
        result = processor.process_folder(args.path)
        
        if result["success"]:
            print(f"✅ Processed {len(result['processed_files'])} files")
            print(f"📊 Generated {result['total_chunks']} total chunks")
            
            if result['failed_files']:
                print(f"❌ Failed to process {len(result['failed_files'])} files:")
                for failed in result['failed_files']:
                    print(f"   - {Path(failed['file_path']).name}: {failed['error']}")
        else:
            print(f"❌ Failed to process folder: {result['error']}")
    
    # Save results if output specified
    if args.output and 'result' in locals():
        try:
            import json
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Results saved to {args.output}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

if __name__ == "__main__":
    main() 