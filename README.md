# Transcript to BRD: RAG-Based Business Requirement Document Generator

A production-ready Python project that converts Microsoft Teams meeting transcripts into comprehensive Business Requirement Documents (BRDs) using a RAG-based workflow with intelligent clarification loops and complete audit trails.

## Features

- **Smart Transcript Ingestion**: Parse `.txt`, `.vtt`, and `.docx` transcript formats with speaker/timestamp metadata
- **Intelligent Segmentation & Chunking**: Automatic topic-based segmentation with configurable overlap
- **RAG-Based Retrieval**: FAISS vector store integration with domain knowledge base
- **Classification Pipeline**: Automatic categorization of transcript segments into BRD sections
- **Contradiction Detection**: Identify missing fields, duplicates, and inconsistent requirements
- **Interactive Clarification Loop**: CLI-based dialog system to resolve ambiguities with confirmed decisions
- **Professional BRD Export**: Generate `.docx` documents with tables, diagrams, and charts
- **Complete Auditability**: Full provenance tracking with audit JSON logs
- **Knowledge Persistence**: Maintain and evolve domain knowledge across runs

## Project Structure

```
transcript-to-brd/
├── app/
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── config.py               # Configuration management
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py           # Transcript file loader
│   │   ├── parser.py           # Speaker/timestamp parser
│   │   └── normalizer.py       # Text cleaning & normalization
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── segmenter.py        # Topic-based segmentation
│   │   ├── chunker.py          # Text chunking with overlap
│   │   └── classifier.py       # Requirement classification
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py       # Embeddings provider interface
│   │   ├── vector_store.py     # FAISS wrapper
│   │   └── knowledge_base.py   # Domain KB management
│   ├── dialog/
│   │   ├── __init__.py
│   │   ├── clarifier.py        # Question generation
│   │   ├── validator.py        # Contradiction & completeness checks
│   │   └── cli.py              # CLI interaction loop
│   ├── brd/
│   │   ├── __init__.py
│   │   ├── schema.py           # BRD data model
│   │   ├── composer.py         # BRD assembly logic
│   │   └── diagrams.py         # Diagram generation (Mermaid/Graphviz)
│   ├── export/
│   │   ├── __init__.py
│   │   └── docx_exporter.py    # Word (.docx) export
│   ├── audit/
│   │   ├── __init__.py
│   │   └── trail.py            # Audit trail recording
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # Logging setup
│       ├── types.py            # Type definitions
│       └── helpers.py          # Utility functions
├── examples/
│   ├── sample_transcript.txt
│   ├── sample_transcript.vtt
│   └── README.md
├── knowledge_base/
│   ├── confirmed_facts.yaml
│   ├── conventions.yaml
│   └── index/                  # FAISS vector index
├── output/                     # Generated BRDs and audit logs
├── tests/
│   ├── __init__.py
│   ├── test_ingestion.py
│   ├── test_nlp.py
│   ├── test_rag.py
│   ├── test_dialog.py
│   ├── test_brd.py
│   └── test_export.py
├── requirements.txt
├── setup.py
├── .env.example
└── .gitignore
```

## Installation

### Prerequisites
- Python 3.9+
- pip or poetry

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Utkarsh242000/transcript-to-brd.git
   cd transcript-to-brd
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys (optional for mock mode)
   ```

## Usage

### Basic Workflow

```bash
# Run the full pipeline
python -m app.main process \
  --transcript examples/sample_transcript.txt \
  --output output/brd_demo.docx \
  --interactive

# Without interactive clarification
python -m app.main process \
  --transcript examples/sample_transcript.txt \
  --output output/brd_demo.docx

# Use mock LLM (no API keys required)
python -m app.main process \
  --transcript examples/sample_transcript.txt \
  --output output/brd_demo.docx \
  --llm mock

# Verbose logging
python -m app.main process \
  --transcript examples/sample_transcript.txt \
  --output output/brd_demo.docx \
  --log-level DEBUG
```

### Advanced Options

```bash
# Specify chunk size and overlap
python -m app.main process \
  --transcript examples/sample_transcript.txt \
  --output output/brd_demo.docx \
  --chunk-size 256 \
  --chunk-overlap 50

# Custom embeddings provider
python -m app.main process \
  --transcript examples/sample_transcript.txt \
  --embeddings-provider openai \
  --output output/brd_demo.docx

# Skip knowledge base update
python -m app.main process \
  --transcript examples/sample_transcript.txt \
  --output output/brd_demo.docx \
  --no-kb-update
```

### Commands

```bash
# Initialize knowledge base
python -m app.main init-kb

# List available transcripts
python -m app.main list-transcripts

# Update domain knowledge
python -m app.main update-kb --facts-file custom_facts.yaml

# Run tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_ingestion.py -v
```

## Configuration

### Environment Variables (`.env`)

```bash
# LLM Configuration
LLM_PROVIDER=openai          # Options: openai, azure, mock
OPENAI_API_KEY=sk-...        # (Optional if using mock)
OPENAI_MODEL=gpt-4

# Embeddings Configuration
EMBEDDINGS_PROVIDER=openai   # Options: openai, huggingface, mock
OPENAI_EMBED_MODEL=text-embedding-3-small

# Vector Store Configuration
FAISS_INDEX_PATH=knowledge_base/index
KB_FACTS_PATH=knowledge_base/confirmed_facts.yaml

# Logging
LOG_LEVEL=INFO               # Options: DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/app.log

# Processing
CHUNK_SIZE=256
CHUNK_OVERLAP=50
TOP_K_RETRIEVAL=5
```

### config.py

All settings are centralized in `app/config.py` and can be overridden via CLI arguments or environment variables.

## Workflow

### 1. Ingestion & Normalization
- Load transcript file (`.txt`, `.vtt`, `.docx`)
- Parse speaker turns and timestamps
- Clean filler words and normalize text
- Produce utterance segments with metadata

### 2. Segmentation & Chunking
- Automatic topic-based segmentation
- Configurable chunk size and overlap
- Metadata preservation (speaker, time ranges)

### 3. Prioritization & Classification
- Categorize chunks: objectives, scope_in, scope_out, functional_req, nonfunctional_req, business_rules, risks, etc.
- LLM-based classification (pluggable providers)
- Filter noise and prioritize relevant content

### 4. RAG Retrieval
- Vectorize chunks using embeddings provider
- Build/load FAISS index
- Retrieve similar chunks for each BRD section
- Cross-reference with domain knowledge base

### 5. Validation & Contradiction Detection
- Check for missing required fields
- Identify duplicate/conflicting requirements
- Detect inconsistencies in scope, timelines, etc.
- Generate list of issues with evidence pointers

### 6. Interactive Clarification
- Generate concise questions from issues
- CLI-based dialog loop
- Record user answers as confirmed decisions
- Mark issues as resolved

### 7. BRD Composition
- Assemble BRD from validated content
- Generate functional requirements table
- Populate non-functional requirements
- Add business rules and acceptance criteria

### 8. Word Export
- Create professional `.docx` with styling
- Insert functional requirements table
- Generate and embed charts/diagrams
- Add audit trail appendix

### 9. Knowledge Update
- Store confirmed decisions in KB
- Update vector index
- Maintain version history

### 10. Audit Trail
- Record all decisions and their provenance
- Map BRD statements to source chunks
- Export audit JSON for compliance

## Example: Running a Sample

```bash
# Process the sample transcript with interactive clarification
python -m app.main process \
  --transcript examples/sample_transcript.txt \
  --output output/sample_brd.docx \
  --interactive \
  --log-level INFO

# Output files generated:
# - output/sample_brd.docx          (BRD document)
# - output/audit_<timestamp>.json   (Audit trail)
# - logs/app.log                    (Execution logs)
```

### Expected Output

**BRD Document Structure:**
```
┌─────────────────────────────────────┐
│ Cover Page & Approval Table         │
├─────────────────────────────────────┤
│ Document History                    │
├─────────────────────────────────────┤
│ Table of Contents                   │
├─────────────────────────────────────┤
│ 1. Executive Summary                │
│ 2. Business Objectives              │
│ 3. Scope (In/Out)                   │
│ 4. Assumptions & Dependencies       │
│ 5. Functional Requirements (Table)  │
│ 6. Non-Functional Requirements      │
│ 7. Business Rules                   │
│ 8. Risks & Open Items               │
│ 9. Acceptance Criteria              │
│ 10. Appendix (Evidence Excerpts)    │
│ 11. Audit Trail                     │
└─────────────────────────────────────┘
```

## Architecture Highlights

### Provider Abstraction
- **EmbeddingsProvider**: Pluggable embeddings (OpenAI, HuggingFace, mock)
- **LLMProvider**: Pluggable LLMs for classification and question generation
- **Easily extensible**: Add new providers by implementing base interfaces

### Type Safety
- Full type hints throughout codebase
- Dataclasses for structured data (BRD schema, audit records)
- Mypy-compatible for static analysis

### Auditability
- Every BRD item traces back to source chunks
- Confirmed decisions stored with timestamp and user
- Audit JSON provides compliance-ready provenance

### Extensibility
- Configuration-driven behavior
- Plugin architecture for LLMs and embeddings
- Custom classifiers via simple keyword models or LLM-based

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_ingestion.py::test_load_txt_transcript -v
```

## Performance Considerations

- **Chunking**: Configurable chunk size (default 256 tokens) with overlap for context preservation
- **Retrieval**: Top-K FAISS retrieval (default K=5) for fast similarity search
- **Caching**: Knowledge base cached in memory after first load
- **Batch Processing**: Ready for batch transcript processing (can be added)

## Troubleshooting

### No API Keys Available
Use mock mode for testing without external APIs:
```bash
python -m app.main process --transcript examples/sample_transcript.txt --llm mock
```

### FAISS Index Not Found
Rebuild the vector store:
```bash
python -m app.main init-kb
python -m app.main process --transcript examples/sample_transcript.txt
```

### Unicode Errors in `.docx` Export
Ensure your transcript file is UTF-8 encoded:
```bash
file -i examples/sample_transcript.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Write tests for new functionality
4. Run `pytest` and ensure all tests pass
5. Commit with clear messages
6. Push and create a Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please open a GitHub issue or contact the maintainer.

---

**Generated**: 2026-05-29 | **Python**: 3.9+ | **Type Safe**: ✓ | **Production Ready**: ✓