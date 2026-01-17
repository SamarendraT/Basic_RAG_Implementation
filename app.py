from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
from vector_embbedding import VectorEmbedding

app = FastAPI(title="RAG API", description="Document embedding and querying with ChromaDB")
embedding_manager = VectorEmbedding(db_path="./db", collection_name="docs")


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str
    n_results: int = 3


class AddTextRequest(BaseModel):
    """Request model for add text endpoint."""
    text: str


class EmbedRequest(BaseModel):
    """Request model for embed endpoint."""
    directory: str = "./Documents"
    chunk_size: int = 500
    overlap: int = 50


@app.post("/query")
def query(request: QueryRequest):
    """Query documents and generate an answer using LLM."""
    try:
        results = embedding_manager.query(request.query, n_results=request.n_results)
        
        if not results:
            return {"answer": "No relevant documents found.", "sources": [], "status": "success"}
        
        # Combine context from all matching chunks
        context = "\n\n".join([f"[From {r['source']}]: {r['text']}" for r in results])
        sources = list(set([r['source'] for r in results]))
        
        answer = ollama.generate(
            model="tinyllama",
            prompt=f"Context:\n{context}\n\nQuestion:\n{request.query}\n\nAnswer clearly and concisely based on the context:"
        )
        
        return {
            "answer": answer['response'],
            "sources": sources,
            "chunks_used": len(results),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embed")
def embed_documents(request: EmbedRequest = EmbedRequest()):
    """Embed all documents from a directory into ChromaDB."""
    try:
        results = embedding_manager.add_documents_from_directory(
            request.directory,
            chunk_size=request.chunk_size,
            overlap=request.overlap
        )
        
        total_chunks = sum(results.values())
        return {
            "status": "success",
            "message": f"Embedded {len(results)} files with {total_chunks} chunks",
            "details": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/clear")
def clear_database():
    """Clear all documents from the vector store."""
    try:
        embedding_manager.clear_collection()
        return {"status": "success", "message": "Database cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add")
def add_text(request: AddTextRequest):
    """Add raw text to the vector store."""
    try:
        import uuid
        from document_parser import TextChunker
        
        chunks = TextChunker.chunk_text(request.text)
        chunk_ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            embedding_manager.collection.add(
                documents=[chunk],
                ids=[chunk_id],
                metadatas=[{"source": "manual_input", "chunk_index": i}]
            )
            chunk_ids.append(chunk_id)
        
        return {
            "status": "success",
            "message": f"Added {len(chunks)} chunks",
            "ids": chunk_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def get_stats():
    """Get statistics about the vector store."""
    try:
        count = embedding_manager.collection.count()
        return {
            "status": "success",
            "total_chunks": count,
            "collection_name": embedding_manager.collection.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))