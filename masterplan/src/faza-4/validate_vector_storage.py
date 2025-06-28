# validate_vector_storage.py
import numpy as np
import time
from sklearn.metrics.pairwise import cosine_similarity
from litecrewai.storage.vector import VectorStore, Document

async def test_vector_extension():
    """Test sqlite-vec extension is loaded"""
    import sqlite3
    
    conn = sqlite3.connect(":memory:")
    
    # Load extension
    conn.enable_load_extension(True)
    conn.load_extension("vec0")
    conn.enable_load_extension(False)
    
    # Test vector functions
    cursor = conn.cursor()
    
    # Create vector table
    cursor.execute("""
        CREATE VIRTUAL TABLE test_vectors USING vec0(
            id INTEGER PRIMARY KEY,
            embedding FLOAT[3]
        )
    """)
    
    # Insert test vector
    cursor.execute(
        "INSERT INTO test_vectors(id, embedding) VALUES (?, ?)",
        (1, "[1.0, 2.0, 3.0]")
    )
    
    # Test vector search
    cursor.execute("""
        SELECT id, vec_distance_cosine(embedding, '[1.0, 2.0, 3.0]') as distance
        FROM test_vectors
        WHERE embedding MATCH '[1.0, 2.0, 3.0]'
        ORDER BY distance
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    assert result is not None
    assert result[1] < 0.01  # Very close
    
    print("✅ sqlite-vec extension working")
    conn.close()

async def test_vector_store_operations():
    """Test basic vector store operations"""
    vector_store = VectorStore(
        db_path=":memory:",
        embedding_model="test",  # Mock model
        dimension=384
    )
    
    await vector_store.initialize()
    
    # Mock embedding function
    def mock_embed(text):
        # Simple hash-based embedding for testing
        np.random.seed(hash(text) % 2**32)
        return np.random.randn(384).tolist()
    
    vector_store._embed = mock_embed
    
    # Add documents
    doc_ids = []
    for i in range(10):
        doc_id = await vector_store.add_document(
            content=f"Document {i} about AI and machine learning",
            metadata={"index": i, "category": "AI"}
        )
        doc_ids.append(doc_id)
    
    print(f"✅ Added {len(doc_ids)} documents")
    
    # Search
    results = await vector_store.search(
        query="artificial intelligence",
        k=5
    )
    
    assert len(results) <= 5
    assert all(hasattr(r, 'score') for r in results)
    assert all(hasattr(r, 'content') for r in results)
    
    print(f"✅ Vector search returned {len(results)} results")

async def test_similarity_accuracy():
    """Test vector similarity accuracy"""
    vector_store = VectorStore(
        db_path=":memory:",
        dimension=128
    )
    
    await vector_store.initialize()
    
    # Create known embeddings
    embeddings = {
        "doc1": np.random.randn(128),
        "doc2": np.random.randn(128),
        "doc3": np.random.randn(128),
    }
    
    # Make doc2 similar to doc1
    embeddings["doc2"] = embeddings["doc1"] + np.random.randn(128) * 0.1
    
    # Add to store
    for name, embedding in embeddings.items():
        await vector_store.add_document_with_embedding(
            content=f"Content for {name}",
            embedding=embedding.tolist(),
            metadata={"name": name}
        )
    
    # Search for doc1
    results = await vector_store.search_by_embedding(
        embedding=embeddings["doc1"].tolist(),
        k=3
    )
    
    # doc1 should be first, doc2 second
    assert results[0].metadata["name"] == "doc1"
    assert results[1].metadata["name"] == "doc2"
    assert results[0].score > results[1].score
    
    print("✅ Similarity search accuracy verified")

async def test_batch_operations():
    """Test batch embedding and insertion"""
    vector_store = VectorStore(
        db_path=":memory:",
        dimension=384
    )
    
    await vector_store.initialize()
    
    # Mock batch embed
    def mock_embed_batch(texts):
        return [np.random.randn(384).tolist() for _ in texts]
    
    vector_store._embed_batch = mock_embed_batch
    
    # Prepare batch
    documents = [
        Document(
            content=f"Batch document {i}",
            metadata={"batch": True, "index": i}
        )
        for i in range(100)
    ]
    
    # Batch insert
    start = time.time()
    doc_ids = await vector_store.add_many(documents)
    batch_time = time.time() - start
    
    assert len(doc_ids) == 100
    print(f"✅ Batch insert: 100 docs in {batch_time:.2f}s")
    
    # Verify
    count = await vector_store.count()
    assert count == 100

async def test_filtered_search():
    """Test search with metadata filters"""
    vector_store = VectorStore(db_path=":memory:", dimension=128)
    await vector_store.initialize()
    
    # Add documents with categories
    categories = ["tech", "science", "tech", "art", "science"]
    for i, category in enumerate(categories):
        await vector_store.add_document(
            content=f"Document {i} in {category}",
            metadata={"category": category, "index": i},
            embedding=np.random.randn(128).tolist()
        )
    
    # Search with filter
    results = await vector_store.search(
        query_embedding=np.random.randn(128).tolist(),
        k=10,
        filter={"category": "tech"}
    )
    
    # Should only return tech documents
    assert all(r.metadata["category"] == "tech" for r in results)
    assert len(results) == 2
    
    print("✅ Filtered search working")

async def test_hybrid_search():
    """Test hybrid vector + keyword search"""
    vector_store = VectorStore(db_path=":memory:", dimension=128)
    await vector_store.initialize()
    
    # Add documents
    docs = [
        "Python is a programming language",
        "Machine learning with Python",
        "Java programming tutorial",
        "Deep learning frameworks",
        "Python data science tools"
    ]
    
    for i, doc in enumerate(docs):
        await vector_store.add_document(
            content=doc,
            embedding=np.random.randn(128).tolist()
        )
    
    # Hybrid search
    results = await vector_store.hybrid_search(
        vector_query="programming",
        keyword_query="Python",
        k=5,
        alpha=0.5  # Equal weight
    )
    
    # Should favor documents with "Python"
    python_docs = [r for r in results if "Python" in r.content]
    assert len(python_docs) >= 2
    
    # Top results should contain Python
    assert "Python" in results[0].content
    
    print(f"✅ Hybrid search: {len(python_docs)}/5 contain 'Python'")

async def test_vector_index_performance():
    """Test vector index performance with larger dataset"""
    vector_store = VectorStore(
        db_path=":memory:",
        dimension=128,
        index_type="hnsw"
    )
    await vector_store.initialize()
    
    # Add many documents
    print("Adding 1000 documents...")
    for i in range(1000):
        embedding = np.random.randn(128)
        # Create clusters
        if i % 100 < 10:
            embedding += np.array([1.0] * 128)  # Cluster 1
        elif i % 100 < 20:
            embedding += np.array([-1.0] * 128)  # Cluster 2
        
        await vector_store.add_document(
            content=f"Document {i}",
            embedding=embedding.tolist()
        )
    
    # Test search performance
    query_embedding = np.random.randn(128) + np.array([1.0] * 128)
    
    start = time.time()
    results = await vector_store.search(
        query_embedding=query_embedding.tolist(),
        k=10
    )
    search_time = (time.time() - start) * 1000
    
    print(f"✅ Search time on 1000 docs: {search_time:.1f}ms")
    assert search_time < 100  # Should be fast with index
    
    # Check we get cluster 1 documents
    cluster1_docs = [r for r in results if int(r.content.split()[1]) % 100 < 10]
    assert len(cluster1_docs) >= 5  # Most should be from cluster 1

async def test_embedding_models():
    """Test different embedding models"""
    # Test with different dimensions
    dimensions = [128, 384, 768]
    
    for dim in dimensions:
        vector_store = VectorStore(
            db_path=":memory:",
            dimension=dim
        )
        await vector_store.initialize()
        
        # Add document
        embedding = np.random.randn(dim).tolist()
        doc_id = await vector_store.add_document_with_embedding(
            content=f"Test with {dim}D",
            embedding=embedding
        )
        
        # Verify
        assert doc_id is not None
        
        # Search
        results = await vector_store.search_by_embedding(
            embedding=embedding,
            k=1
        )
        
        assert len(results) == 1
        assert results[0].content == f"Test with {dim}D"
        
        print(f"✅ {dim}D embeddings working")

if __name__ == "__main__":
    print("🔍 Validating vector storage...\n")
    
    async def run_tests():
        await test_vector_extension()
        await test_vector_store_operations()
        await test_similarity_accuracy()
        await test_batch_operations()
        await test_filtered_search()
        await test_hybrid_search()
        await test_vector_index_performance()
        await test_embedding_models()
    
    import asyncio
    asyncio.run(run_tests())
    
    print("\n✅ Vector storage validation complete!")