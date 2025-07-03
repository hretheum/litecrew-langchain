# 🔍 Szczegółowa Analiza: Co Tracisz Bez ChromaDB

## Executive Summary

Przejście z ChromaDB na Faiss-CPU lub SQLite-vec **NIE JEST** prostą zamianą 1:1. Utracisz wiele zaawansowanych funkcji, które wymagają znacznej reimplementacji.

## 📊 Funkcje ChromaDB Używane w LiteCrew

### 🔴 Krytyczne Funkcje (Brak Alternatyw)

#### 1. **Zarządzanie Kolekcjami**
```python
# ChromaDB - automatyczne
client.get_or_create_collection(
    name="agent_memory",
    embedding_function=embedding_func
)

# Faiss - musisz sam zaimplementować
class CollectionManager:
    def __init__(self):
        self.collections = {}
        self.metadata_stores = {}
        
    def get_or_create_collection(self, name, dimension):
        if name not in self.collections:
            self.collections[name] = faiss.IndexFlatL2(dimension)
            self.metadata_stores[name] = {}
        return self.collections[name]
```

#### 2. **Operacja Upsert (Update or Insert)**
```python
# ChromaDB - automatyczne
collection.upsert(
    documents=["doc1", "doc2"],
    metadatas=[{"source": "web"}, {"source": "pdf"}],
    ids=["id1", "id2"]
)

# Faiss - musisz sam sprawdzać czy dokument istnieje
def upsert(self, id, embedding, metadata):
    if id in self.id_to_index:
        # Update - usuń stary i dodaj nowy
        old_index = self.id_to_index[id]
        # Faiss nie wspiera usuwania! Musisz przebudować indeks
        self.rebuild_index_without(old_index)
    # Insert
    self.index.add(embedding)
    self.metadata[id] = metadata
```

#### 3. **Persystencja Automatyczna**
```python
# ChromaDB - zapisuje automatycznie
client = chromadb.PersistentClient(path="./chroma_db")

# Faiss - musisz sam zarządzać
class PersistentFaissIndex:
    def save(self):
        faiss.write_index(self.index, "index.faiss")
        with open("metadata.pkl", "wb") as f:
            pickle.dump(self.metadata, f)
            
    def load(self):
        self.index = faiss.read_index("index.faiss")
        with open("metadata.pkl", "rb") as f:
            self.metadata = pickle.load(f)
```

### 🟡 Funkcje Wysokiej Wartości (Trudne do Zastąpienia)

#### 4. **Filtrowanie po Metadanych**
```python
# ChromaDB - eleganckie
results = collection.query(
    query_texts=["find docs about AI"],
    where={"source": "pdf", "year": {"$gte": 2023}},
    where_document={"$contains": "machine learning"}
)

# Faiss - brak wsparcia, musisz sam
def query_with_filter(self, embedding, filters):
    # Najpierw znajdź wszystkie podobne
    distances, indices = self.index.search(embedding, k=100)
    
    # Potem filtruj po metadanych
    filtered_results = []
    for idx, dist in zip(indices[0], distances[0]):
        metadata = self.metadata.get(idx, {})
        if self.match_filters(metadata, filters):
            filtered_results.append((idx, dist, metadata))
            
    return filtered_results[:k]
```

#### 5. **Wbudowane Embedding Functions**
```python
# ChromaDB - 15+ providerów out-of-the-box
from chromadb.utils.embedding_functions import (
    OpenAIEmbeddingFunction,
    CohereEmbeddingFunction, 
    HuggingFaceEmbeddingFunction,
    SentenceTransformerEmbeddingFunction
)

collection = client.create_collection(
    name="docs",
    embedding_function=OpenAIEmbeddingFunction(api_key="...")
)

# Faiss - musisz sam integrować każdy
class EmbeddingManager:
    def __init__(self, provider="openai"):
        if provider == "openai":
            self.client = openai.Client()
        elif provider == "cohere":
            self.client = cohere.Client()
        # ... dla każdego providera osobno
        
    def embed(self, texts):
        if self.provider == "openai":
            return self.client.embeddings.create(...)
        # ... obsługa każdego providera
```

### 🟢 Funkcje Średniej Wartości (Możliwe do Zastąpienia)

#### 6. **Multi-tenancy / Namespace Isolation**
```python
# ChromaDB - wbudowane
client.get_collection("user_123_memories")
client.get_collection("user_456_memories")

# Faiss - możliwe przez prefixing
self.indices[f"user_{user_id}_memories"]
```

#### 7. **Różne Metryki Odległości**
```python
# ChromaDB - łatwe przełączanie
collection = client.create_collection(
    name="images",
    metadata={"hnsw:space": "cosine"}  # lub "l2", "ip"
)

# Faiss - wymaga różnych typów indeksów
index_l2 = faiss.IndexFlatL2(d)
index_ip = faiss.IndexFlatIP(d)  # inner product
# Cosine wymaga normalizacji embeddingów
```

## 🛠️ Przykład Pełnej Reimplementacji

```python
# chromadb_to_faiss_adapter.py
import faiss
import numpy as np
import pickle
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

class FaissChromaAdapter:
    """Adapter implementujący API ChromaDB na Faiss"""
    
    def __init__(self, persist_directory: str = "./faiss_db"):
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(exist_ok=True)
        self.collections = {}
        self.load_collections()
        
    def get_or_create_collection(
        self, 
        name: str, 
        embedding_function=None,
        metadata: Dict[str, Any] = None
    ):
        if name not in self.collections:
            self.collections[name] = FaissCollection(
                name=name,
                persist_dir=self.persist_dir / name,
                embedding_function=embedding_function,
                metadata=metadata
            )
        return self.collections[name]
        
    def delete_collection(self, name: str):
        if name in self.collections:
            self.collections[name].delete()
            del self.collections[name]
            
    def reset(self):
        for collection in self.collections.values():
            collection.delete()
        self.collections = {}

class FaissCollection:
    def __init__(self, name: str, persist_dir: Path, embedding_function=None, metadata=None):
        self.name = name
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(exist_ok=True)
        self.embedding_function = embedding_function
        self.metadata = metadata or {}
        
        # Główne struktury danych
        self.index = None
        self.id_to_idx = {}  # mapowanie: document_id -> faiss_index
        self.idx_to_id = {}  # mapowanie: faiss_index -> document_id
        self.documents = {}  # document_id -> document_text
        self.metadatas = {}  # document_id -> metadata
        self.dimension = None
        self.current_idx = 0
        
        self.load()
        
    def add(self, 
            embeddings: List[List[float]] = None,
            documents: List[str] = None,
            metadatas: List[Dict[str, Any]] = None,
            ids: List[str] = None):
        
        # Generuj embeddingi jeśli nie podano
        if embeddings is None and documents is not None:
            if self.embedding_function is None:
                raise ValueError("No embeddings provided and no embedding function set")
            embeddings = self.embedding_function(documents)
            
        # Generuj IDs jeśli nie podano
        if ids is None:
            ids = [f"{self.name}_{i}" for i in range(len(embeddings))]
            
        # Inicjalizuj indeks jeśli pierwszy raz
        if self.index is None:
            self.dimension = len(embeddings[0])
            self.index = faiss.IndexFlatL2(self.dimension)
            
        # Dodaj do indeksu
        embeddings_array = np.array(embeddings, dtype=np.float32)
        self.index.add(embeddings_array)
        
        # Zapisz metadane
        for i, (id, doc, meta) in enumerate(zip(ids, documents or [None]*len(ids), metadatas or [{}]*len(ids))):
            self.id_to_idx[id] = self.current_idx
            self.idx_to_id[self.current_idx] = id
            if doc:
                self.documents[id] = doc
            if meta:
                self.metadatas[id] = meta
            self.current_idx += 1
            
        self.save()
        
    def upsert(self, **kwargs):
        """Upsert = sprawdź czy istnieje, update lub insert"""
        ids = kwargs.get('ids', [])
        
        # Rozdziel na update i insert
        to_update = []
        to_insert = []
        
        for i, id in enumerate(ids):
            if id in self.id_to_idx:
                to_update.append(i)
            else:
                to_insert.append(i)
                
        # Najpierw usuń stare (update)
        if to_update:
            # UWAGA: Faiss nie wspiera usuwania!
            # Musimy przebudować cały indeks bez starych wektorów
            self._rebuild_without_ids([ids[i] for i in to_update])
            
        # Potem dodaj wszystko
        self.add(**kwargs)
        
    def query(self,
              query_embeddings: List[List[float]] = None,
              query_texts: List[str] = None,
              n_results: int = 10,
              where: Dict[str, Any] = None,
              where_document: Dict[str, str] = None,
              include: List[str] = None):
        
        # Generuj embeddingi z tekstów jeśli potrzeba
        if query_embeddings is None and query_texts is not None:
            if self.embedding_function is None:
                raise ValueError("No embeddings provided and no embedding function set")
            query_embeddings = self.embedding_function(query_texts)
            
        # Szukaj w Faiss
        query_array = np.array(query_embeddings, dtype=np.float32)
        distances, indices = self.index.search(query_array, n_results * 3)  # x3 dla filtrowania
        
        # Przygotuj wyniki
        results = {
            'ids': [],
            'distances': [],
            'metadatas': [],
            'documents': []
        }
        
        for query_idx in range(len(query_embeddings)):
            query_results = {
                'ids': [],
                'distances': [],
                'metadatas': [],
                'documents': []
            }
            
            count = 0
            for idx, dist in zip(indices[query_idx], distances[query_idx]):
                if idx == -1:  # Faiss zwraca -1 gdy brak wyników
                    continue
                    
                doc_id = self.idx_to_id.get(int(idx))
                if not doc_id:
                    continue
                    
                # Filtrowanie po metadanych
                if where:
                    meta = self.metadatas.get(doc_id, {})
                    if not self._match_where(meta, where):
                        continue
                        
                # Filtrowanie po dokumencie
                if where_document:
                    doc = self.documents.get(doc_id, "")
                    if not self._match_where_document(doc, where_document):
                        continue
                        
                # Dodaj do wyników
                query_results['ids'].append(doc_id)
                query_results['distances'].append(float(dist))
                query_results['metadatas'].append(self.metadatas.get(doc_id, {}))
                query_results['documents'].append(self.documents.get(doc_id, ""))
                
                count += 1
                if count >= n_results:
                    break
                    
            results['ids'].append(query_results['ids'])
            results['distances'].append(query_results['distances'])
            results['metadatas'].append(query_results['metadatas'])
            results['documents'].append(query_results['documents'])
            
        return results
        
    def _match_where(self, metadata: Dict, where: Dict) -> bool:
        """Prosta implementacja filtrowania where"""
        for key, value in where.items():
            if key.startswith("$"):
                # Operatory jak $gt, $gte, $lt, $lte, $ne, $in, $nin
                # TODO: implementacja
                return False
            else:
                if metadata.get(key) != value:
                    return False
        return True
        
    def _match_where_document(self, document: str, where_document: Dict) -> bool:
        """Prosta implementacja filtrowania where_document"""
        if "$contains" in where_document:
            return where_document["$contains"].lower() in document.lower()
        return True
        
    def _rebuild_without_ids(self, ids_to_remove: List[str]):
        """Przebuduj indeks bez podanych IDs"""
        # Zbierz wszystkie embeddingi oprócz usuniętych
        new_embeddings = []
        new_ids = []
        new_idx_mapping = {}
        
        for old_idx in range(self.current_idx):
            doc_id = self.idx_to_id.get(old_idx)
            if doc_id and doc_id not in ids_to_remove:
                # Pobierz embedding z indeksu
                embedding = self.index.reconstruct(old_idx)
                new_embeddings.append(embedding)
                new_ids.append(doc_id)
                
        # Stwórz nowy indeks
        if new_embeddings:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(np.array(new_embeddings, dtype=np.float32))
            
            # Zaktualizuj mapowania
            self.id_to_idx = {id: i for i, id in enumerate(new_ids)}
            self.idx_to_id = {i: id for i, id in enumerate(new_ids)}
            self.current_idx = len(new_ids)
        else:
            # Pusty indeks
            self.index = None
            self.id_to_idx = {}
            self.idx_to_id = {}
            self.current_idx = 0
            
        # Usuń metadane i dokumenty
        for id in ids_to_remove:
            self.documents.pop(id, None)
            self.metadatas.pop(id, None)
            
    def save(self):
        """Zapisz indeks i metadane na dysk"""
        if self.index is not None:
            faiss.write_index(self.index, str(self.persist_dir / "index.faiss"))
            
        metadata = {
            'name': self.name,
            'dimension': self.dimension,
            'id_to_idx': self.id_to_idx,
            'idx_to_id': self.idx_to_id,
            'documents': self.documents,
            'metadatas': self.metadatas,
            'current_idx': self.current_idx,
            'collection_metadata': self.metadata
        }
        
        with open(self.persist_dir / "metadata.pkl", "wb") as f:
            pickle.dump(metadata, f)
            
    def load(self):
        """Wczytaj indeks i metadane z dysku"""
        index_path = self.persist_dir / "index.faiss"
        metadata_path = self.persist_dir / "metadata.pkl"
        
        if index_path.exists():
            self.index = faiss.read_index(str(index_path))
            
        if metadata_path.exists():
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
                self.dimension = metadata.get('dimension')
                self.id_to_idx = metadata.get('id_to_idx', {})
                self.idx_to_id = metadata.get('idx_to_id', {})
                self.documents = metadata.get('documents', {})
                self.metadatas = metadata.get('metadatas', {})
                self.current_idx = metadata.get('current_idx', 0)
                self.metadata = metadata.get('collection_metadata', {})
                
    def delete(self):
        """Usuń kolekcję z dysku"""
        import shutil
        if self.persist_dir.exists():
            shutil.rmtree(self.persist_dir)
```

## 💡 Podsumowanie: Co NAPRAWDĘ Tracisz

### 🔴 Największe Straty:
1. **Automatyczna persystencja** - musisz sam implementować save/load
2. **Metadata filtering** - brak WHERE clause, musisz post-filtrować
3. **Upsert** - Faiss nie wspiera update, musisz przebudowywać indeks
4. **Collection management** - brak namespaces, musisz sam zarządzać
5. **Embedding providers** - brak gotowych integracji

### 🟡 Średnie Straty:
1. **Różne metryki** - musisz używać różnych typów indeksów
2. **Batch operations** - musisz sam optymalizować
3. **Error handling** - ChromaDB ma lepszą obsługę błędów
4. **Dokumentacja** - mniej przykładów dla Faiss

### 🟢 Małe Straty:
1. **API kompatybilność** - można zaadaptować
2. **Podstawowe search** - działa podobnie
3. **Performance** - Faiss często szybszy

## 🎯 Rekomendacja Końcowa

**Jeśli używasz:**
- ✅ Tylko podstawowe vector search → Faiss OK
- ✅ Proste use case bez metadanych → Faiss OK
- ❌ Metadata filtering → Zostań przy ChromaDB
- ❌ Multi-tenant/collections → Zostań przy ChromaDB
- ❌ Częste updates → Zostań przy ChromaDB

**Alternatywa**: Rozważ **Qdrant** (30MB) lub **Weaviate** (50MB) - mniejsze niż ChromaDB ale z podobnymi funkcjami.