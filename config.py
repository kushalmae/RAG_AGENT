import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the RAG Agent application."""
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE"))
    
    # Document Processing Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP"))    
    DOCUMENTS_FOLDER_PATH: str = os.getenv("DOCUMENTS_FOLDER_PATH")
    
    # Vector Store Settings
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME")
    CHROMA_EMBEDDING_MODEL: str = os.getenv("CHROMA_EMBEDDING_MODEL")
    
    # Application Settings
    DEFAULT_RETRIEVAL_K: int = int(os.getenv("DEFAULT_RETRIEVAL_K"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL")
    
    # File Processing Settings
    SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".xlsx", ".xls"]
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB"))
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate that all required configuration values are set.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set")
            return False
        
        return True
    
    @classmethod
    def get_config_dict(cls) -> dict:
        """
        Get configuration as a dictionary.
        
        Returns:
            dict: Configuration values
        """
        return {
            "openai_model": cls.OPENAI_MODEL,
            "openai_temperature": cls.OPENAI_TEMPERATURE,
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "persist_directory": cls.CHROMA_PERSIST_DIRECTORY,
            "collection_name": cls.CHROMA_COLLECTION_NAME,
            "retrieval_k": cls.DEFAULT_RETRIEVAL_K,
            "supported_extensions": cls.SUPPORTED_EXTENSIONS,
            "max_file_size_mb": cls.MAX_FILE_SIZE_MB,
            "documents_folder_path": cls.DOCUMENTS_FOLDER_PATH,
            "embedding_model": cls.CHROMA_EMBEDDING_MODEL,
            "log_level": cls.LOG_LEVEL            
        } 