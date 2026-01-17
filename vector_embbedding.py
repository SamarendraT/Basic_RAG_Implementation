from pathlib import Path
from typing import List, Dict, Any
import chromadb
from document_parser import DocumentParser, TextChunker


class VectorEmbedding:
    """Manage document embeddings and vector storage with chunking."""
    
    def __init__(self, db_path: str = "./db", collection_name: str = "docs"):
        """Initialize the vector embedding client."""
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_or_create_collection(name=collection_name)
        except Exception as e:
            raise ValueError(f"Error initializing ChromaDB client: {str(e)}")
    
    def add_document(self, file_path: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Add a parsed document to the vector store with chunking.
        
        Args:
            file_path: Path to the document
            chunk_size: Target size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunk IDs
        """
        try:
            text, file_type = DocumentParser.parse_document(file_path)
            chunks = TextChunker.chunk_text(text, chunk_size, overlap)
            
            import uuid
            file_name = Path(file_path).name
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid4())
                self.collection.add(
                    documents=[chunk],
                    ids=[chunk_id],
                    metadatas=[{"source": file_name, "chunk_index": i, "file_type": file_type}]
                )
                chunk_ids.append(chunk_id)
            
            print(f"✓ Document embedded: {file_name} ({len(chunks)} chunks)")
            return chunk_ids
        except Exception as e:
            raise ValueError(f"Error adding document to vector store: {str(e)}")
    
    def add_documents_from_directory(self, directory_path: str, chunk_size: int = 500, overlap: int = 50) -> Dict[str, int]:
        """
        Add all supported documents from a directory to the vector store.
        
        Returns:
            Dictionary with file names and number of chunks embedded
        """
        try:
            supported_extensions = {'.pdf', '.docx', '.txt'}
            results = {}
            
            for file_path in Path(directory_path).iterdir():
                if file_path.suffix.lower() in supported_extensions:
                    try:
                        chunk_ids = self.add_document(str(file_path), chunk_size, overlap)
                        results[file_path.name] = len(chunk_ids)
                    except Exception as e:
                        print(f"✗ Error embedding {file_path.name}: {str(e)}")
                        results[file_path.name] = 0
            
            total_chunks = sum(results.values())
            print(f"\n✓ Total: {len(results)} files, {total_chunks} chunks embedded")
            return results
        except Exception as e:
            raise ValueError(f"Error adding documents from directory: {str(e)}")
    
    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar chunks.
        
        Returns:
            List of matching chunks with metadata
        """
        try:
            result = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            if not result['documents'] or not result['documents'][0]:
                return []
            
            matches = []
            for i, doc in enumerate(result['documents'][0]):
                matches.append({
                    "text": doc,
                    "source": result['metadatas'][0][i].get("source", "unknown"),
                    "chunk_index": result['metadatas'][0][i].get("chunk_index", 0),
                    "distance": result['distances'][0][i] if result.get('distances') else None
                })
            
            return matches
        except Exception as e:
            raise ValueError(f"Error querying vector store: {str(e)}")
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            self.client.delete_collection(name=self.collection.name)
            self.collection = self.client.get_or_create_collection(name=self.collection.name)
            print("✓ Collection cleared")
            return True
        except Exception as e:
            raise ValueError(f"Error clearing collection: {str(e)}")