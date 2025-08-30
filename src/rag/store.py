from typing import List, Dict


class VectorStore:
    def __init__(self):
        self.documents = {}

    async def add_documents(self, documents: List[Dict]):
        """Adds documents to the in-memory store."""
        for doc in documents:
            self.documents[doc["path"]] = doc["content"]

    async def query(self, text: str) -> List[Dict]:
        """Queries the in-memory store with a simple keyword search."""
        results = []
        for path, content in self.documents.items():
            if text in content:
                results.append({"path": path, "content": content})
        return results


vector_store = VectorStore()
