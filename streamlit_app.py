import streamlit as st
from simple_rag import SimpleRAG
from config import Config
import logging

# Disable logging for cleaner UI
logging.disable(logging.CRITICAL)

# Page configuration
st.set_page_config(
    page_title="RAG Q&A System",
    page_icon="🤖",
    layout="wide"
)

# Initialize RAG system
@st.cache_resource
def initialize_rag():
    """Initialize RAG system with caching."""
    try:
        return SimpleRAG(Config)
    except Exception as e:
        st.error(f"Failed to initialize RAG system: {e}")
        st.stop()

def main():
    st.title("🤖 RAG Question & Answer System")
    st.markdown("Ask questions about your documents and get AI-powered answers!")
    
    # Initialize RAG system
    with st.spinner("Initializing RAG system..."):
        rag = initialize_rag()
    
    st.success("✅ RAG system ready!")
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Ask Your Question")
        
        # Question input
        question = st.text_area(
            "Enter your question:",
            placeholder="What would you like to know about your documents?",
            height=100
        )
        
        # Ask button
        if st.button("🔍 Get Answer", type="primary", use_container_width=True):
            if question.strip():
                with st.spinner("Thinking..."):
                    result = rag.answer_question(question.strip())
                
                if result["success"]:
                    st.subheader("🤖 Answer")
                    st.write(result["answer"])
                    
                    # Show sources if available
                    if result["sources"]:
                        st.subheader("📚 Sources")
                        for i, source in enumerate(result["sources"][:3], 1):
                            with st.expander(f"Source {i}: {source['metadata'].get('filename', 'Unknown')}"):
                                st.text(source["content"][:500] + "..." if len(source["content"]) > 500 else source["content"])
                else:
                    st.error(f"❌ {result['answer']}")
            else:
                st.warning("Please enter a question!")
    
    with col2:
        st.subheader("ℹ️ Information")
        
        # Get database stats
        try:
            count = rag.collection.count()
            st.metric("Documents in Database", count)
        except:
            st.metric("Documents in Database", "Unknown")
        
        st.markdown("---")
        
        st.markdown("""
        **How to use:**
        1. Type your question in the text area
        2. Click "Get Answer" button
        3. View the AI-generated answer
        4. Check sources for more details
        
        **Tips:**
        - Be specific in your questions
        - Ask about content in your documents
        - Try different phrasings if needed
        """)
        
        st.markdown("---")
        
        # Sample questions
        st.subheader("💡 Sample Questions")
        sample_questions = [
            "What is the main topic?",
            "Can you summarize the key points?",
            "What are the technical specifications?",
            "How does this work?",
            "What are the benefits?"
        ]
        
        for q in sample_questions:
            if st.button(q, key=f"sample_{q}", use_container_width=True):
                st.session_state.sample_question = q
                st.rerun()
        
        # Auto-fill sample question
        if 'sample_question' in st.session_state:
            question = st.session_state.sample_question
            del st.session_state.sample_question

if __name__ == "__main__":
    main() 