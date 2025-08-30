
import asyncio
from src.rag.loader import loader
from src.rag.store import vector_store

async def main():
    """Initializes the RAG system by loading documents into the vector store."""
    document_paths = [
        "README.md",
        "artifacts/docs/runbook.md",
        "artifacts/docs/usecases.md"
    ]
    
    print("Loading documents...")
    documents = await loader.load_documents(document_paths)
    
    print("Adding documents to the vector store...")
    await vector_store.add_documents(documents)
    
    print("RAG system initialized.")

if __name__ == "__main__":
    asyncio.run(main())
