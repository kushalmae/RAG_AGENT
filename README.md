# 🤖 Simple RAG System

A powerful yet simple Retrieval-Augmented Generation (RAG) system that allows you to ingest documents and ask questions using natural language. Built with Python, OpenAI, ChromaDB, and Streamlit.

## ✨ Features

- 📁 **Multi-format Document Support**: PDF, Word (.docx), and Excel (.xlsx, .xls) files
- 🔍 **Intelligent Document Processing**: Automatic text extraction and smart chunking
- 💾 **Persistent Vector Storage**: ChromaDB for efficient document embedding storage
- 🤖 **AI-Powered Q&A**: Leverages OpenAI's language models for accurate responses
- 🌐 **Beautiful Web Interface**: Streamlit-based UI with modern design
- 🖥️ **Command Line Interface**: Full CLI support for automation and scripting
- 📊 **Document Management**: Add, remove, and manage your document collection
- 🔧 **Configurable Settings**: Customizable model parameters and processing options
- 🔄 **Modular Architecture**: Clean separation between ingestion and querying

## 🏗️ Architecture

The system consists of several modular components:

1. **Document Processor** (`document_processor.py`): Handles text extraction from various file formats
2. **Document Ingestion** (`document_ingestion.py`): Manages document chunking and vector storage
3. **Ingestion CLI** (`ingest_documents.py`): Command-line interface for document management
4. **Simple RAG** (`simple_rag.py`): Core Q&A engine with CLI interface
5. **Streamlit App** (`streamlit_app.py`): Web-based user interface
6. **Configuration** (`config.py`): Centralized settings management

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd RAG_AGENT
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   OPENAI_TEMPERATURE=0.1
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   CHROMA_PERSIST_DIRECTORY=./chroma_db
   CHROMA_COLLECTION_NAME=documents
   CHROMA_EMBEDDING_MODEL=text-embedding-ada-002
   DEFAULT_RETRIEVAL_K=4
   MAX_FILE_SIZE_MB=50
   DOCUMENTS_FOLDER_PATH=./documents
   LOG_LEVEL=INFO
   ```

### Run the Application

#### Option 1: Web Interface (Recommended)
```bash
# Windows
run_streamlit.bat

# Or directly
streamlit run streamlit_app.py
```

```

## 📖 Usage

### Web Interface

1. **Start the Streamlit app**: Run `streamlit run streamlit_app.py`
2. **Open your browser**: Navigate to `http://localhost:8501`
3. **Ask questions**: Type your questions and get AI-powered answers with source citations

### Command Line Interface

#### Document Management
```bash
# Add documents from default folder
python ingest_documents.py ingest-default

# Add documents from specific folder
python ingest_documents.py add-folder --path "path/to/documents"

# Add a single file
python ingest_documents.py add-file --path "document.pdf"

# Check database statistics
python ingest_documents.py stats

# Clear the database
python ingest_documents.py clear
```

#### Question & Answer
```bash
# Interactive mode (prompts for question)
python simple_rag.py

# Direct question
python simple_rag.py --question "What is the main topic?"
```

#### Document Processing (Standalone)
```bash
# Process documents without adding to RAG
python document_processor.py folder "path/to/documents"
python document_processor.py file "document.pdf"
```

### Programmatic Usage

```python
from simple_rag import SimpleRAG
from config import Config

# Initialize the RAG system
rag = SimpleRAG(Config)

# Ask a question
response = rag.answer_question("What is the main topic?")
print(response["answer"])

# Check sources
for source in response["sources"]:
    print(f"Source: {source['metadata']['filename']}")
```

## 🔧 Configuration

All settings can be configured through environment variables or the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Your OpenAI API key (required) |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | OpenAI model to use |
| `OPENAI_TEMPERATURE` | `0.1` | Response randomness (0.0-1.0) |
| `CHUNK_SIZE` | `1000` | Text chunk size for processing |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `CHROMA_PERSIST_DIRECTORY` | `./chroma_db` | Vector database storage path |
| `CHROMA_COLLECTION_NAME` | `documents` | Collection name in ChromaDB |
| `CHROMA_EMBEDDING_MODEL` | `text-embedding-ada-002` | OpenAI embedding model |
| `DEFAULT_RETRIEVAL_K` | `4` | Number of documents to retrieve |
| `MAX_FILE_SIZE_MB` | `50` | Maximum file size to process |
| `DOCUMENTS_FOLDER_PATH` | `./documents` | Default folder for document ingestion |
| `LOG_LEVEL` | `INFO` | Logging level |

## 📁 Supported File Types

- **PDF files** (`.pdf`) - Full text extraction
- **Word documents** (`.docx`) - Text and tables
- **Excel files** (`.xlsx`, `.xls`) - All sheets and data

## 🛠️ Development

### Project Structure
```
RAG_AGENT/
├── simple_rag.py           # Core Q&A engine
├── ingest_documents.py     # Document ingestion CLI
├── document_processor.py   # Text extraction and chunking
├── document_ingestion.py   # Vector store management
├── streamlit_app.py        # Web interface
├── config.py               # Configuration management
├── requirements.txt        # Dependencies
└── run_streamlit.bat       # Windows launcher
```

### Key Design Principles

- **Modular Architecture**: Clean separation between components
- **Configuration-Driven**: All settings managed through environment variables
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Flexible Interfaces**: Both CLI and web interfaces available
- **Production Ready**: Logging, validation, and robust error handling

## 🎯 Sample Workflow

```bash
# 1. Check initial state
python ingest_documents.py stats

# 2. Add your documents
python ingest_documents.py add-folder --path "my_documents/"

# 3. Verify documents were added
python ingest_documents.py stats

# 4. Start asking questions
python simple_rag.py --question "What are the key findings?"

# 5. Or use the web interface
streamlit run streamlit_app.py
```

## 🔍 Troubleshooting

### Common Issues

1. **API Key Error**: Make sure `OPENAI_API_KEY` is set in your `.env` file
2. **File Not Found**: Check file paths and ensure files are in supported formats
3. **No Results**: Ensure documents are added to the database first
4. **Import Errors**: Run `pip install -r requirements.txt` to install dependencies

### Debug Mode

Set `LOG_LEVEL=DEBUG` in your `.env` file for detailed logging.

### Quick Test

Test the system with a simple workflow:
```bash
# Add some documents
python ingest_documents.py add-folder --path "your_documents/"

# Ask a question
python simple_rag.py --question "What is this about?"
```

## 📊 Performance Tips

1. **Chunk Size**: Use 500-800 for precise answers, 1200-2000 for broader context
2. **File Size**: Keep files under 50MB for optimal performance
3. **Database Maintenance**: Clear old documents periodically with `python ingest_documents.py clear`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use, modify, and distribute as needed.

## 🆘 Support

For questions or issues:
1. Review the troubleshooting section above
2. Test with the quick workflow provided
3. Check your configuration in `.env`
4. Verify your OpenAI API key is working

---

**Built with ❤️ using Python, OpenAI, ChromaDB, and Streamlit**