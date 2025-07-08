"""
Knowledge Base implementation with RAG (Retrieval Augmented Generation).
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from sentence_transformers import SentenceTransformer

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    # Fallback to simple numpy-based search
    

@dataclass
class Document:
    """A document in the knowledge base."""
    
    id: str
    content: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


@dataclass
class SearchResult:
    """A search result with relevance score."""
    
    document: Document
    score: float
    snippet: str = ""


class VectorIndex:
    """Vector index for similarity search."""
    
    def __init__(self, dimension: int = 384):
        """Initialize vector index.
        
        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension
        self.documents: List[Document] = []
        self.embeddings: Optional[np.ndarray] = None
        
        if HAS_FAISS:
            # Use FAISS for efficient search
            self.index = faiss.IndexFlatL2(dimension)
            self.use_faiss = True
        else:
            # Fallback to numpy
            self.index = None
            self.use_faiss = False
    
    def add(self, documents: List[Document]) -> None:
        """Add documents to index."""
        if not documents:
            return
        
        # Extract embeddings
        embeddings = np.array([doc.embedding for doc in documents])
        
        if self.use_faiss:
            self.index.add(embeddings.astype('float32'))
        else:
            # Numpy fallback
            if self.embeddings is None:
                self.embeddings = embeddings
            else:
                self.embeddings = np.vstack([self.embeddings, embeddings])
        
        self.documents.extend(documents)
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[int, float]]:
        """Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results
            
        Returns:
            List of (index, distance) tuples
        """
        if not self.documents:
            return []
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        if self.use_faiss:
            distances, indices = self.index.search(query_embedding, min(k, len(self.documents)))
            return list(zip(indices[0], distances[0]))
        else:
            # Numpy fallback - compute cosine similarity
            if self.embeddings is None:
                return []
            
            # Normalize for cosine similarity
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            embeddings_norm = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            
            # Compute similarities
            similarities = np.dot(embeddings_norm, query_norm.T).flatten()
            
            # Get top k
            top_indices = np.argsort(similarities)[::-1][:k]
            
            # Convert similarity to distance (1 - similarity)
            results = [(idx, 1 - similarities[idx]) for idx in top_indices]
            return results
    
    def clear(self) -> None:
        """Clear the index."""
        self.documents = []
        self.embeddings = None
        if self.use_faiss:
            self.index = faiss.IndexFlatL2(self.dimension)


class KnowledgeBase:
    """Knowledge base with RAG capabilities."""
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        max_documents: int = 10000
    ):
        """Initialize knowledge base.
        
        Args:
            storage_path: Path for persistent storage
            model_name: Sentence transformer model name
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            max_documents: Maximum documents to store
        """
        self.storage_path = storage_path or Path("knowledge_base")
        self.storage_path.mkdir(exist_ok=True)
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_documents = max_documents
        
        # Initialize embedding model
        self.embedder = SentenceTransformer(model_name)
        self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
        
        # Initialize vector index
        self.index = VectorIndex(self.embedding_dim)
        
        # Document storage
        self.documents: Dict[str, Document] = {}
        
        # Load existing documents
        self._load_documents()
    
    def _load_documents(self) -> None:
        """Load documents from storage."""
        docs_file = self.storage_path / "documents.json"
        embeddings_file = self.storage_path / "embeddings.npy"
        
        if docs_file.exists():
            with open(docs_file, 'r') as f:
                docs_data = json.load(f)
            
            # Load embeddings if available
            embeddings = None
            if embeddings_file.exists():
                embeddings = np.load(embeddings_file)
            
            # Reconstruct documents
            for i, doc_data in enumerate(docs_data):
                doc = Document(
                    id=doc_data["id"],
                    content=doc_data["content"],
                    source=doc_data["source"],
                    metadata=doc_data.get("metadata", {}),
                    timestamp=doc_data.get("timestamp", time.time())
                )
                
                if embeddings is not None and i < len(embeddings):
                    doc.embedding = embeddings[i]
                
                self.documents[doc.id] = doc
            
            # Rebuild index
            if self.documents:
                self.index.add(list(self.documents.values()))
    
    def _save_documents(self) -> None:
        """Save documents to storage."""
        docs_file = self.storage_path / "documents.json"
        embeddings_file = self.storage_path / "embeddings.npy"
        
        # Save document data
        docs_data = [doc.to_dict() for doc in self.documents.values()]
        with open(docs_file, 'w') as f:
            json.dump(docs_data, f, indent=2)
        
        # Save embeddings
        if self.documents:
            embeddings = np.array([doc.embedding for doc in self.documents.values()])
            np.save(embeddings_file, embeddings)
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Find a good break point (sentence end or space)
            if end < len(text):
                # Look for sentence end
                for punct in ['. ', '! ', '? ', '\n\n']:
                    last_punct = text.rfind(punct, start, end)
                    if last_punct != -1:
                        end = last_punct + len(punct)
                        break
                else:
                    # Fall back to space
                    last_space = text.rfind(' ', start, end)
                    if last_space != -1:
                        end = last_space + 1
            
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap
        
        return chunks
    
    def ingest_document(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Ingest a document into the knowledge base.
        
        Args:
            content: Document content
            source: Document source (file path, URL, etc.)
            metadata: Additional metadata
            
        Returns:
            List of document IDs created
        """
        # Chunk the document
        chunks = self._chunk_text(content)
        
        # Create documents for each chunk
        doc_ids = []
        documents = []
        
        for i, chunk in enumerate(chunks):
            # Generate ID based on content hash
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
            doc_id = f"{source}_{i}_{chunk_hash}"
            
            # Skip if already exists
            if doc_id in self.documents:
                doc_ids.append(doc_id)
                continue
            
            # Create document
            doc = Document(
                id=doc_id,
                content=chunk,
                source=source,
                metadata={
                    **(metadata or {}),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            )
            
            # Generate embedding
            doc.embedding = self.embedder.encode(chunk)
            
            self.documents[doc_id] = doc
            documents.append(doc)
            doc_ids.append(doc_id)
        
        # Add to index
        if documents:
            self.index.add(documents)
        
        # Save periodically
        if len(self.documents) % 100 == 0:
            self._save_documents()
        
        # Cleanup if needed
        if len(self.documents) > self.max_documents:
            self._cleanup_old_documents()
        
        return doc_ids
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_source: Optional[str] = None
    ) -> List[SearchResult]:
        """Search for relevant documents.
        
        Args:
            query: Search query
            k: Number of results
            filter_source: Optional source filter
            
        Returns:
            List of search results
        """
        if not self.documents:
            return []
        
        # Embed query
        start_time = time.perf_counter()
        query_embedding = self.embedder.encode(query)
        embedding_time = (time.perf_counter() - start_time) * 1000
        
        # Search in index
        start_time = time.perf_counter()
        results = self.index.search(query_embedding, k * 2)  # Get more for filtering
        search_time = (time.perf_counter() - start_time) * 1000
        
        # Convert to SearchResults
        search_results = []
        for idx, distance in results:
            if idx >= len(self.index.documents):
                continue
                
            doc = self.index.documents[idx]
            
            # Apply source filter
            if filter_source and doc.source != filter_source:
                continue
            
            # Create snippet
            snippet = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
            
            # Convert distance to similarity score (0-1)
            score = 1 / (1 + distance)
            
            search_results.append(SearchResult(
                document=doc,
                score=score,
                snippet=snippet
            ))
            
            if len(search_results) >= k:
                break
        
        # Log performance
        total_time = embedding_time + search_time
        if total_time > 200:  # Log if slower than 200ms
            print(f"Slow search: embedding={embedding_time:.1f}ms, search={search_time:.1f}ms")
        
        return search_results
    
    def update_document(
        self,
        doc_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing document.
        
        Args:
            doc_id: Document ID
            content: New content (if provided)
            metadata: Metadata updates
            
        Returns:
            True if updated, False if not found
        """
        if doc_id not in self.documents:
            return False
        
        doc = self.documents[doc_id]
        
        # Update content and re-embed if needed
        if content is not None and content != doc.content:
            doc.content = content
            doc.embedding = self.embedder.encode(content)
            
            # Rebuild index (inefficient but simple)
            self.index.clear()
            self.index.add(list(self.documents.values()))
        
        # Update metadata
        if metadata is not None:
            doc.metadata.update(metadata)
        
        doc.timestamp = time.time()
        
        # Save changes
        self._save_documents()
        
        return True
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if deleted, False if not found
        """
        if doc_id not in self.documents:
            return False
        
        del self.documents[doc_id]
        
        # Rebuild index
        self.index.clear()
        if self.documents:
            self.index.add(list(self.documents.values()))
        
        # Save changes
        self._save_documents()
        
        return True
    
    def get_source_tracking(self) -> Dict[str, Any]:
        """Get statistics about document sources."""
        source_stats = {}
        
        for doc in self.documents.values():
            source = doc.source
            if source not in source_stats:
                source_stats[source] = {
                    "count": 0,
                    "total_size": 0,
                    "last_updated": 0
                }
            
            source_stats[source]["count"] += 1
            source_stats[source]["total_size"] += len(doc.content)
            source_stats[source]["last_updated"] = max(
                source_stats[source]["last_updated"],
                doc.timestamp
            )
        
        return source_stats
    
    def _cleanup_old_documents(self) -> None:
        """Remove oldest documents to stay under limit."""
        if len(self.documents) <= self.max_documents:
            return
        
        # Sort by timestamp
        sorted_docs = sorted(
            self.documents.items(),
            key=lambda x: x[1].timestamp
        )
        
        # Remove oldest
        to_remove = len(self.documents) - self.max_documents
        for doc_id, _ in sorted_docs[:to_remove]:
            del self.documents[doc_id]
        
        # Rebuild index
        self.index.clear()
        self.index.add(list(self.documents.values()))
        
        # Save changes
        self._save_documents()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        if not self.documents:
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "unique_sources": 0,
                "avg_chunk_size": 0,
                "storage_size_mb": 0
            }
        
        # Calculate storage size
        storage_size = 0
        for file in self.storage_path.iterdir():
            if file.is_file():
                storage_size += file.stat().st_size
        
        # Get unique sources
        unique_sources = set(doc.source for doc in self.documents.values())
        
        # Calculate average chunk size
        avg_chunk_size = np.mean([len(doc.content) for doc in self.documents.values()])
        
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.documents),
            "unique_sources": len(unique_sources),
            "avg_chunk_size": avg_chunk_size,
            "storage_size_mb": storage_size / (1024 * 1024),
            "embedding_model": self.embedder.get_sentence_embedding_dimension(),
            "has_faiss": HAS_FAISS
        }