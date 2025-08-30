"""Vector store for RAG system."""

import json
import os
from typing import Any, Dict, List, Optional, Tuple
import hashlib

import structlog
import numpy as np

logger = structlog.get_logger()


class VectorStore:
    """Vector store for similarity search."""
    
    def __init__(self, store_type: str = "chroma", collection_name: str = "legend_docs"):
        """
        Initialize vector store.
        
        Args:
            store_type: Type of vector store (chroma, faiss, pgvector)
            collection_name: Name of the collection
        """
        self.store_type = store_type
        self.collection_name = collection_name
        self.store = None
        self.embeddings_model = None
        
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize the vector store backend."""
        if self.store_type == "chroma":
            try:
                import chromadb
                from chromadb.config import Settings
                
                # Initialize ChromaDB
                self.client = chromadb.Client(Settings(
                    persist_directory=".chroma_db",
                    anonymized_telemetry=False
                ))
                
                # Get or create collection
                try:
                    self.store = self.client.get_collection(self.collection_name)
                    logger.info(f"Loaded existing collection: {self.collection_name}")
                except:
                    self.store = self.client.create_collection(
                        name=self.collection_name,
                        metadata={"description": "Legend Guardian knowledge base"}
                    )
                    logger.info(f"Created new collection: {self.collection_name}")
                    
            except ImportError:
                logger.warning("ChromaDB not installed, using in-memory store")
                self._use_simple_store()
                
        elif self.store_type == "faiss":
            try:
                import faiss
                
                # Initialize FAISS index
                self.dimension = 768  # Default embedding dimension
                self.index = faiss.IndexFlatL2(self.dimension)
                self.documents = []
                self.store = self.index
                logger.info("FAISS index initialized")
                
            except ImportError:
                logger.warning("FAISS not installed, using in-memory store")
                self._use_simple_store()
                
        elif self.store_type == "pgvector":
            try:
                import psycopg2
                from pgvector.psycopg2 import register_vector
                
                # Connect to PostgreSQL with pgvector
                conn_string = os.getenv("DATABASE_URL", "postgresql://legend:legend@localhost:5432/legend")
                self.conn = psycopg2.connect(conn_string)
                register_vector(self.conn)
                
                # Create table if not exists
                with self.conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS vector_store (
                            id TEXT PRIMARY KEY,
                            content TEXT,
                            metadata JSONB,
                            embedding vector(768)
                        )
                    """)
                    self.conn.commit()
                
                logger.info("pgvector store initialized")
                
            except Exception as e:
                logger.warning(f"pgvector initialization failed: {e}")
                self._use_simple_store()
        else:
            self._use_simple_store()
        
        # Initialize embeddings model
        self._initialize_embeddings()
    
    def _use_simple_store(self):
        """Use simple in-memory store as fallback."""
        self.store_type = "simple"
        self.store = {
            "documents": [],
            "embeddings": []
        }
        logger.info("Using simple in-memory vector store")
    
    def _initialize_embeddings(self):
        """Initialize embeddings model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer embeddings initialized")
        except ImportError:
            logger.warning("Sentence transformers not installed, using simple embeddings")
            self.embeddings_model = None
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents with content and metadata
        """
        if not documents:
            return
        
        # Generate embeddings
        contents = [doc["content"] for doc in documents]
        embeddings = self._generate_embeddings(contents)
        
        if self.store_type == "chroma":
            # Add to ChromaDB
            ids = [self._generate_id(doc["content"]) for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            
            self.store.add(
                documents=contents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
        elif self.store_type == "faiss":
            # Add to FAISS
            import faiss
            embeddings_array = np.array(embeddings).astype('float32')
            self.index.add(embeddings_array)
            self.documents.extend(documents)
            
        elif self.store_type == "pgvector":
            # Add to pgvector
            with self.conn.cursor() as cur:
                for doc, embedding in zip(documents, embeddings):
                    doc_id = self._generate_id(doc["content"])
                    cur.execute("""
                        INSERT INTO vector_store (id, content, metadata, embedding)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE
                        SET content = EXCLUDED.content,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding
                    """, (
                        doc_id,
                        doc["content"],
                        json.dumps(doc.get("metadata", {})),
                        embedding
                    ))
                self.conn.commit()
                
        elif self.store_type == "simple":
            # Add to simple store
            self.store["documents"].extend(documents)
            self.store["embeddings"].extend(embeddings)
        
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def query(
        self,
        query_text: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Query the vector store.
        
        Args:
            query_text: Query text
            k: Number of results to return
            filter_metadata: Optional metadata filter
        
        Returns:
            List of (document, score) tuples
        """
        # Generate query embedding
        query_embedding = self._generate_embeddings([query_text])[0]
        
        results = []
        
        if self.store_type == "chroma":
            # Query ChromaDB
            query_results = self.store.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=filter_metadata if filter_metadata else None
            )
            
            if query_results["documents"] and query_results["documents"][0]:
                for i in range(len(query_results["documents"][0])):
                    doc = {
                        "content": query_results["documents"][0][i],
                        "metadata": query_results["metadatas"][0][i] if query_results["metadatas"] else {}
                    }
                    score = query_results["distances"][0][i] if query_results["distances"] else 0
                    results.append((doc, score))
                    
        elif self.store_type == "faiss":
            # Query FAISS
            import faiss
            query_array = np.array([query_embedding]).astype('float32')
            distances, indices = self.index.search(query_array, k)
            
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx]
                    score = float(distances[0][i])
                    results.append((doc, score))
                    
        elif self.store_type == "pgvector":
            # Query pgvector
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT content, metadata, 
                           embedding <-> %s::vector as distance
                    FROM vector_store
                    ORDER BY distance
                    LIMIT %s
                """, (query_embedding, k))
                
                for row in cur.fetchall():
                    doc = {
                        "content": row[0],
                        "metadata": row[1] if row[1] else {}
                    }
                    score = float(row[2])
                    results.append((doc, score))
                    
        elif self.store_type == "simple":
            # Simple cosine similarity search
            if self.store["embeddings"]:
                similarities = []
                for i, emb in enumerate(self.store["embeddings"]):
                    similarity = self._cosine_similarity(query_embedding, emb)
                    similarities.append((i, similarity))
                
                # Sort by similarity and get top k
                similarities.sort(key=lambda x: x[1], reverse=True)
                
                for idx, score in similarities[:k]:
                    doc = self.store["documents"][idx]
                    results.append((doc, 1 - score))  # Convert similarity to distance
        
        return results
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts
        
        Returns:
            List of embeddings
        """
        if self.embeddings_model:
            # Use sentence transformers
            embeddings = self.embeddings_model.encode(texts)
            return embeddings.tolist()
        else:
            # Simple TF-IDF style embeddings as fallback
            embeddings = []
            for text in texts:
                # Very simple hash-based embedding
                words = text.lower().split()
                embedding = [0.0] * 768  # Standard embedding size
                
                for word in words:
                    # Hash word to position
                    hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
                    pos = hash_val % 768
                    embedding[pos] += 1.0
                
                # Normalize
                norm = sum(e**2 for e in embedding) ** 0.5
                if norm > 0:
                    embedding = [e / norm for e in embedding]
                
                embeddings.append(embedding)
            
            return embeddings
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content."""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a**2 for a in vec1) ** 0.5
        norm2 = sum(b**2 for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def clear(self) -> None:
        """Clear all documents from the store."""
        if self.store_type == "chroma":
            # Delete and recreate collection
            self.client.delete_collection(self.collection_name)
            self.store = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Legend Guardian knowledge base"}
            )
            
        elif self.store_type == "faiss":
            import faiss
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            
        elif self.store_type == "pgvector":
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM vector_store")
                self.conn.commit()
                
        elif self.store_type == "simple":
            self.store = {
                "documents": [],
                "embeddings": []
            }
        
        logger.info("Vector store cleared")