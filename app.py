from fastapi import FastAPI
import chromadb
import ollama

app = FastAPI()
chroma = chromadb.PersistentClient(path="./db")
collection = chroma.get_or_create_collection(name="docs")

@app.post("/query")
def query(q: str):
    result = collection.query(query_texts=[q], n_results=1)
    context = result['documents'][0][0] if result['documents'] else ""

    answer = ollama.generate(
        model = "tinyllama",
        prompt = f"Context:\n{context}\n\nQuestion:\n{q}\n\nAnswer clearly and concisely:"
    )

    return {"answer": answer['response']}

@app.post("/add")
def add_text(text: str):
    try:
        import uuid
        doc_id = str(uuid.uuid4())

        collection.add(documents = [text], ids = [doc_id])

        return {
            "status": "success",
            "message": "Text added successfully.",
            "id": doc_id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }