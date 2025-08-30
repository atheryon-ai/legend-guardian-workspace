#!/usr/bin/env python3
"""Initialize RAG system with Legend knowledge base."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.loader import DocumentLoader
from src.rag.store import VectorStore
from src.settings import get_settings


def init_rag_system():
    """Initialize the RAG system with Legend documentation and examples."""
    print("Initializing RAG system...")
    
    settings = get_settings()
    
    # Initialize document loader
    loader = DocumentLoader(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap
    )
    
    # Initialize vector store
    store = VectorStore(
        store_type=settings.vector_store_type,
        collection_name="legend_knowledge"
    )
    
    # Clear existing data
    print("Clearing existing vector store...")
    store.clear()
    
    documents = []
    
    # Load PURE examples if available
    pure_dir = "examples/pure"
    if os.path.exists(pure_dir):
        print(f"Loading PURE examples from {pure_dir}...")
        pure_docs = loader.load_pure_examples(pure_dir)
        documents.extend(pure_docs)
        print(f"  Loaded {len(pure_docs)} PURE document chunks")
    
    # Load Legend documentation
    docs_dir = "docs"
    if os.path.exists(docs_dir):
        print(f"Loading documentation from {docs_dir}...")
        doc_chunks = loader.load_legend_docs(docs_dir)
        documents.extend(doc_chunks)
        print(f"  Loaded {len(doc_chunks)} documentation chunks")
    
    # Load mapping examples
    mapping_file = "examples/mappings.yaml"
    if os.path.exists(mapping_file):
        print(f"Loading mapping examples from {mapping_file}...")
        mapping_docs = loader.load_mapping_examples(mapping_file)
        documents.extend(mapping_docs)
        print(f"  Loaded {len(mapping_docs)} mapping examples")
    
    # Load API specifications
    api_spec_file = "openapi.json"
    if os.path.exists(api_spec_file):
        print(f"Loading API specification from {api_spec_file}...")
        api_docs = loader.load_api_specs(api_spec_file)
        documents.extend(api_docs)
        print(f"  Loaded {len(api_docs)} API specifications")
    
    # Add hardcoded Legend knowledge
    legend_knowledge = [
        {
            "content": """Legend PURE Language Basics:
            
            Classes define data models:
            Class model::Trade {
                id: String[1];
                ticker: String[1];
                quantity: Integer[1];
                price: Float[1];
                notional: Float[1];
            }
            
            Associations define relationships:
            Association model::TradeToProduct {
                trade: Trade[1];
                product: Product[1];
            }
            
            Functions define business logic:
            function totalNotional(trades: Trade[*]): Float[1] {
                $trades->map(t | $t.notional)->sum()
            }
            
            Constraints ensure data quality:
            constraint PositiveQuantity on Trade {
                $this.quantity > 0
            }""",
            "metadata": {
                "type": "knowledge",
                "topic": "PURE basics",
                "source": "hardcoded"
            }
        },
        {
            "content": """Legend Mapping Concepts:
            
            Mappings connect models to data sources:
            
            Relational Mapping:
            Mapping mapping::TradeMapping {
                Trade: Relational {
                    id: [db]trades.trade_id,
                    ticker: [db]trades.symbol,
                    quantity: [db]trades.qty
                }
            }
            
            FlatData Mapping (CSV/JSON):
            Mapping mapping::TradeFlatMapping {
                Trade: FlatData {
                    id: $src.tradeId,
                    ticker: $src.symbol,
                    quantity: parseInt($src.quantity)
                }
            }""",
            "metadata": {
                "type": "knowledge",
                "topic": "Mapping patterns",
                "source": "hardcoded"
            }
        },
        {
            "content": """Legend Service Creation:
            
            Services expose data through REST APIs:
            
            Service service::TradeService {
                pattern: '/api/trades/{ticker}';
                documentation: 'Get trades by ticker';
                execution: Single {
                    query: |Trade.all()->filter(t | $t.ticker == $ticker);
                    mapping: mapping::TradeMapping;
                    runtime: runtime::H2Runtime;
                }
            }
            
            Multi-execution services:
            Service service::TradeAnalytics {
                pattern: '/api/analytics/trades';
                execution: Multi {
                    query: |Trade.all()->groupBy([t | $t.ticker], [agg(t | $t.notional, y | $y->sum())]);
                    key: 'analytics';
                }
            }""",
            "metadata": {
                "type": "knowledge", 
                "topic": "Service patterns",
                "source": "hardcoded"
            }
        }
    ]
    
    documents.extend(legend_knowledge)
    
    # Add documents to vector store
    if documents:
        print(f"\nAdding {len(documents)} documents to vector store...")
        store.add_documents(documents)
        print("Documents indexed successfully!")
    else:
        print("No documents found to index")
    
    # Test the system
    print("\nTesting RAG system...")
    test_queries = [
        "How do I create a Trade model in PURE?",
        "What is a mapping in Legend?",
        "How to create a REST service?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = store.query(query, k=2)
        if results:
            print(f"  Found {len(results)} relevant documents")
            for doc, score in results[:1]:  # Show top result
                content_preview = doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
                print(f"  Top result (score: {score:.3f}):")
                print(f"    {content_preview}")
        else:
            print("  No results found")
    
    print("\n✅ RAG system initialized successfully!")
    return store


if __name__ == "__main__":
    init_rag_system()