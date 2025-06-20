import chromadb
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import logging
import argparse
import sys

# Load environment variables
load_dotenv()

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
class SimpleRAG:
    """A simple RAG system that handles document ingestion and querying."""
    
    def __init__(self, config):
        """Initialize the RAG system using configuration."""
        self.config = config
        
        # Only use API key from config/environment
        self.api_key = config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables or config")
        
        # Store config settings
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize Chroma with config
        db_path = config.CHROMA_PERSIST_DIRECTORY
        collection_name = config.CHROMA_COLLECTION_NAME
        
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        try:
            self.collection = self.chroma_client.get_collection(collection_name)
        except:
            self.collection = self.chroma_client.create_collection(collection_name)      
    
    def get_embedding(self, text: str) -> list:
        """Get embedding for text using OpenAI."""
        try:
            response = self.client.embeddings.create(
                model=self.config.CHROMA_EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None   

    
    def answer_question(self, question: str, n_results: int = None) -> dict:
        """Answer a question using RAG."""
        n_results = n_results or self.config.DEFAULT_RETRIEVAL_K
        
        try:
            # Get query embedding
            query_embedding = self.get_embedding(question)
            if query_embedding is None:
                return {
                    "success": False,
                    "answer": "Error generating query embedding",
                    "sources": []
                }
            
            # Search collection for relevant documents
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            if not results['documents'] or not results['documents'][0]:
                return {
                    "success": True,
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": []
                }
            
            # Create context from search results
            context = "\n\n".join(results['documents'][0])
            
            # Generate answer using GPT
            prompt = f"""Based on the following context from documents, answer the question. If you can't answer based on the context, say so.

                    Context: {context}
                    Question: {question}
                    Answer:"""
            
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.OPENAI_TEMPERATURE
            )
            
            answer = response.choices[0].message.content
            
            # Format sources
            sources = []
            for i in range(len(results['documents'][0])):
                sources.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "success": False,
                "answer": f"Error generating answer: {str(e)}",
                "sources": []
            }


def main():
    """Command line interface for the RAG system."""
    from config import Config
    
    parser = argparse.ArgumentParser(description="Simple RAG System - Interactive Q&A")
    parser.add_argument("--question", help="Question to ask (optional - will prompt if not provided)")
    
    args = parser.parse_args()
    
    print("🤖 Simple RAG System")
    print("=" * 50)
    
    # Initialize RAG system
    try:
        rag = SimpleRAG(Config)
        print("✅ RAG system initialized!")
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
    
    # Get question from user
    question = args.question
    if not question:
        print("💬 Ask me anything about your documents!")
        question = input("❓ Your question: ").strip()
        
        if not question:
            print("❌ No question provided. Exiting.")
            sys.exit(1)
    
    print(f"🤔 Answering question: {question}")
    result = rag.answer_question(question)
    
    if result["success"]:
        print(f"\n🤖 Answer:")
        print(f"{result['answer']}")
        
        if result['sources']:
            print(f"\n📚 Based on {len(result['sources'])} sources:")
            for i, source in enumerate(result['sources'][:3], 1):  # Show first 3 sources
                filename = source['metadata'].get('filename', 'Unknown')
                print(f"   {i}. {filename}")
    else:
        print(f"❌ {result['answer']}")
        sys.exit(1)    
 

if __name__ == "__main__":
    main() 