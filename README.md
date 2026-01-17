# RAG with ChromaDB

A simple RAG (Retrieval-Augmented Generation) implementation using ChromaDB for vector storage and Ollama for LLM responses.

## Setup

```bash
pip install PyPDF2 python-docx chromadb ollama fastapi uvicorn
```
Check whether Ollama running using cmd ```bash curl http://localhost:11435"``` --> Y --> ollama is running
Here i have used tinyllama cmd ```bash ollama pull tinyllama ``` to pull the model
Test the model using cmd ```bash ollama run tinyllama``` or any model which u have pulled from ollama model repo
Try pulling different models with model(small or large) to compare response
## Usage

### 1. Add Documents
Place your files (`.pdf`, `.docx`, `.txt`) in the `Documents/` folder.

### 2. Start Server
```bash
uvicorn app:app --reload
```

### 3. Embed Documents
```bash
curl -X POST http://localhost:8000/embed
```

### 4. Query
```bash
Invoke-RestMethod -Uri "http://127.0.0.1:8000/query" -Method Post -ContentType "application/json" -Body '{"query": "?????..."}''
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/embed` | POST | Embed documents from `./Documents` |
| `/query` | POST | Query with LLM response |
| `/clear` | DELETE | Clear all embeddings |
| `/stats` | GET | Get chunk count |
