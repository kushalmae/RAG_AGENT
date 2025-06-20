#!/usr/bin/env python3
"""
Document Ingestion CLI - Handles adding documents to the RAG system
"""

import chromadb
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import logging
import argparse
import sys
from document_ingestion import DocumentIngestion

# Load environment variables
load_dotenv()

# Simple logging setup - disabled
#logging.basicConfig(level=logging.INFO)
logging.disable(logging.CRITICAL)
logger = logging.getLogger(__name__)

def initialize_ingestion_system(config):
    """Initialize the document ingestion system."""
    # Check API key from config/environment only
    api_key = config.OPENAI_API_KEY
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables or config")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Initialize Chroma with config
    db_path = config.CHROMA_PERSIST_DIRECTORY
    collection_name = config.CHROMA_COLLECTION_NAME
    
    chroma_client = chromadb.PersistentClient(path=db_path)
    try:
        collection = chroma_client.get_collection(collection_name)
    except:
        collection = chroma_client.create_collection(collection_name)
    
    # Initialize document ingestion system with config parameters
    doc_ingestion = DocumentIngestion(
        openai_client=client,
        chroma_collection=collection,
        embedding_model=config.CHROMA_EMBEDDING_MODEL,
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        max_file_size_mb=config.MAX_FILE_SIZE_MB,
        supported_extensions=config.SUPPORTED_EXTENSIONS
    )
    
    logger.info("Document ingestion system initialized successfully")
    return doc_ingestion, chroma_client, collection

def main():
    from config import Config

    """Command line interface for document ingestion."""
    parser = argparse.ArgumentParser(
        description="Document Ingestion System",
        epilog="""
        Examples:
            python ingest_documents.py ingest-default              # Process default folder from config
            python ingest_documents.py add-folder                  # Process default folder from config  
            python ingest_documents.py add-folder --path docs/     # Process specific folder
            python ingest_documents.py add-file --path file.pdf    # Process specific file
            python ingest_documents.py stats                       # Show database statistics
            python ingest_documents.py clear                       # Clear database
                    """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("action", choices=["add-file", "add-folder", "ingest-default", "stats", "clear"], 
                       help="Action to perform")
    parser.add_argument("--path", help="Path to file or folder (for add-file/add-folder). Uses default from config if not specified.")
    
    args = parser.parse_args()
    
    print("📚 Document Ingestion System")
    print("=" * 50)
    
    # Show configuration info
    default_path = Config.DOCUMENTS_FOLDER_PATH
    if default_path:
        print(f"📂 Default documents folder: {default_path}")
    else:
        print("📂 No default documents folder configured")
    print("=" * 50)
    
    # Initialize ingestion system
    try:
        doc_ingestion, chroma_client, collection = initialize_ingestion_system(Config)
        print("✅ Document ingestion system initialized!")
        print(f"📡 Using API key from environment variables")
        print("=" * 50)
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Please set your OPENAI_API_KEY environment variable:")
        print("   export OPENAI_API_KEY=your_api_key_here")
        print("   or create a .env file with OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
    except Exception as e:
        print(f"❌ System Error: {e}")
        sys.exit(1)
    
    # Execute the requested action
    if args.action == "add-file":
        if not args.path:
            print("❌ Error: --path is required for add-file action")
            print("💡 Specify a file path: --path 'path/to/your/file.pdf'")
            sys.exit(1)
        
        print(f"📄 Processing file: {args.path}")
        result = doc_ingestion.process_and_add_document(args.path)
        
        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"📊 Added {result['chunks_added']} chunks")
        else:
            print(f"❌ {result['message']}")
            sys.exit(1)
    
    elif args.action == "add-folder":
        # Use provided path or default from config
        folder_path = args.path if args.path else Config.DOCUMENTS_FOLDER_PATH
        
        if not folder_path:
            print("❌ Error: No folder path specified and no default path configured")
            print("💡 Either:")
            print("   - Specify a path: --path 'path/to/your/folder'")
            print("   - Set DOCUMENTS_FOLDER_PATH in your .env file")
            sys.exit(1)
        
        # Check if folder exists
        if not Path(folder_path).exists():
            print(f"❌ Error: Folder does not exist: {folder_path}")
            sys.exit(1)
        
        if args.path:
            print(f"📁 Processing folder: {folder_path}")
        else:
            print(f"📁 Processing default folder: {folder_path}")
            print("💡 Using default path from config (DOCUMENTS_FOLDER_PATH)")
        
        result = doc_ingestion.process_and_add_folder(folder_path)
        
        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"📊 Files processed: {result['files_processed']}")
            print(f"📊 Total chunks added: {result['total_chunks_added']}")
            
            if result['failed_files']:
                print(f"❌ Failed files ({len(result['failed_files'])}):")
                for failed in result['failed_files'][:5]:  # Show first 5
                    print(f"   - {Path(failed['file_path']).name}: {failed['error']}")
                if len(result['failed_files']) > 5:
                    print(f"   ... and {len(result['failed_files']) - 5} more")
        else:
            print(f"❌ {result['message']}")
            sys.exit(1)
    
    elif args.action == "ingest-default":
        # Use default folder from config
        default_path = Config.DOCUMENTS_FOLDER_PATH
        
        if not default_path:
            print("❌ Error: No default documents folder configured")
            print("💡 Set DOCUMENTS_FOLDER_PATH in your .env file")
            print("   Example: DOCUMENTS_FOLDER_PATH=./documents")
            sys.exit(1)
        
        # Check if folder exists
        if not Path(default_path).exists():
            print(f"❌ Error: Default folder does not exist: {default_path}")
            print("💡 Create the folder or update DOCUMENTS_FOLDER_PATH in your .env file")
            sys.exit(1)
        
        print(f"📁 Processing default documents folder: {default_path}")
        print("💡 Using DOCUMENTS_FOLDER_PATH from config")
        
        result = doc_ingestion.process_and_add_folder(default_path)
        
        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"📊 Files processed: {result['files_processed']}")
            print(f"📊 Total chunks added: {result['total_chunks_added']}")
            
            if result['failed_files']:
                print(f"❌ Failed files ({len(result['failed_files'])}):")
                for failed in result['failed_files'][:5]:  # Show first 5
                    print(f"   - {Path(failed['file_path']).name}: {failed['error']}")
                if len(result['failed_files']) > 5:
                    print(f"   ... and {len(result['failed_files']) - 5} more")
        else:
            print(f"❌ {result['message']}")
            sys.exit(1)
    
    elif args.action == "stats":
        print("📊 Getting collection statistics...")
        try:
            count = collection.count()
            print(f"✅ Documents in database: {count}")
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            sys.exit(1)
    
    elif args.action == "clear":
        print("🗑️  Clearing database...")
        try:
            collection_name = Config.CHROMA_COLLECTION_NAME
            chroma_client.delete_collection(collection_name)
            chroma_client.create_collection(collection_name)
            print("✅ Database cleared successfully")
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main() 