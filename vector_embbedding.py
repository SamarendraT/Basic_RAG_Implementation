import chromadb

client  = chromadb.PersistentClient(path="./db")
collection = client.get_or_create_collection(name="docs")

with open('Document.txt', "r") as f:
    text = f.read()

collection.add(
    documents=[text], ids=["doc_about_k8s"]
)

print("Embedding stored successfully.")