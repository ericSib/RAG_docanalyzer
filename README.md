# RAG Document Analyzer

A powerful document analysis tool for RAG (Retrieval Augmented Generation) systems, enabling automated document analysis, preprocessing, and indexing.

## Features

- Multi-format document support (PDF, Word, PowerPoint, Text)
- Advanced document analysis and metadata extraction
- Intelligent text preprocessing and chunking
- Vector storage with PostgreSQL + pgvector
- Interactive Streamlit dashboard
- Comprehensive document metrics and quality analysis

## Requirements

- Python 3.9+
- PostgreSQL database with pgvector extension
- 8GB RAM minimum
- SSD storage (recommended)
- 4+ CPU cores
- GPU (optional, recommended for large volumes)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd rag-doc-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file with the following variables:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/rag_analyzer
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

5. Initialize the database:
```bash
python scripts/init_db.py
```

## Usage

1. Start the FastAPI backend:
```bash
uvicorn app.main:app --reload
```

2. Launch the Streamlit interface:
```bash
streamlit run app/frontend/main.py
```

3. Access the dashboard at `http://localhost:8501`

## Project Structure

```
rag-doc-analyzer/
├── app/
│   ├── api/            # FastAPI routes and endpoints
│   ├── core/           # Core application logic
│   ├── frontend/       # Streamlit dashboard
│   ├── models/         # Database models
│   └── utils/          # Utility functions
├── scripts/            # Database and setup scripts
├── tests/              # Test suite
├── .env                # Environment variables
├── requirements.txt    # Project dependencies
└── README.md          # Project documentation
```

## License

[License Type] - See LICENSE file for details

## Contributing

Contributions are welcome! Please read our Contributing Guidelines for details.
