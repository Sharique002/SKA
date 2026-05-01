"""
Vector database service for storing and retrieving embeddings
Uses FAISS for efficient similarity search
Embeddings stored in SQLite, index kept in memory
"""
import numpy as np
import sqlite3
from typing import List, Optional, Dict

try:
    import faiss
except ImportError:
    faiss = None


_index = None
_index_to_chunk_id = {}


def _get_or_create_index(dimension: int):
    """Get existing index or create new one"""
    global _index
    if _index is None:
        _index = faiss.IndexFlatL2(dimension)
        _index_to_chunk_id.clear()
    return _index


def initialize_index(db_path: str, dimension: int = 384):
    """Initialize FAISS index from embeddings stored in database"""
    global _index, _index_to_chunk_id

    if faiss is None:
        raise Exception("FAISS not installed")

    try:
        dimension = int(dimension)
        _index = faiss.IndexFlatL2(dimension)
        _index_to_chunk_id = {}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT chunk_id, embedding FROM chunks WHERE embedding IS NOT NULL')
            rows = cursor.fetchall()

            if rows:
                embeddings_list = []
                for idx, (chunk_id, emb_blob) in enumerate(rows):
                    emb_array = np.frombuffer(emb_blob, dtype=np.float32)
                    embeddings_list.append(emb_array)
                    _index_to_chunk_id[idx] = chunk_id

                if embeddings_list:
                    embeddings_array = np.array(embeddings_list, dtype=np.float32)
                    embeddings_array = np.ascontiguousarray(embeddings_array)
                    _index.add(embeddings_array)
                    print(f"[INFO] Loaded {len(embeddings_list)} embeddings into index")
        except Exception as e:
            print(f"[WARN] Could not load embeddings from database: {e}")
        finally:
            conn.close()

        print("[INFO] Index initialized successfully")

    except Exception as e:
        print(f"[ERROR] Failed to initialize index: {e}")
        raise


def store_embeddings(chunk_ids: List[str], embeddings: List[np.ndarray],
                     chunks: List[str], document_id: int, db_path: str):
    """Store embeddings in database and FAISS index"""
    global _index, _index_to_chunk_id

    if faiss is None:
        raise Exception("FAISS not installed")

    try:
        if not chunk_ids or not embeddings or not chunks:
            raise ValueError("Empty inputs")

        if len(chunk_ids) != len(embeddings) or len(embeddings) != len(chunks):
            raise ValueError("Length mismatch")

        embedding_dim = None
        for i, emb in enumerate(embeddings):
            if not isinstance(emb, np.ndarray):
                raise TypeError(f"Embedding {i} is not numpy array")
            if emb.ndim != 1:
                raise ValueError(f"Embedding {i} is not 1D")
            if embedding_dim is None:
                embedding_dim = int(len(emb))
            elif len(emb) != embedding_dim:
                raise ValueError(f"Dimension mismatch at {i}")

        try:
            if _index is None:
                print(f"[DEBUG] Creating new FAISS index with dimension {embedding_dim}")
                _index = faiss.IndexFlatL2(int(embedding_dim))
                _index_to_chunk_id.clear()
                print(f"[DEBUG] Index created successfully with dimension {embedding_dim}")

            if _index.ntotal > 0 and _index.d != embedding_dim:
                raise ValueError(f"Index dimension {_index.d} != embedding dimension {embedding_dim}")
        except Exception as e:
            print(f"[ERROR] Index access failed: {e}")
            raise

        embeddings_list = []
        for e in embeddings:
            arr = e.astype(np.float32, copy=False)
            embeddings_list.append(np.ascontiguousarray(arr))

        embeddings_array = np.array(embeddings_list, dtype=np.float32)
        embeddings_array = np.ascontiguousarray(embeddings_array)

        print(f"[INFO] Adding {len(embeddings_array)} embeddings to index")

        start_idx = _index.ntotal
        _index.add(embeddings_array)

        for i, chunk_id in enumerate(chunk_ids):
            _index_to_chunk_id[start_idx + i] = chunk_id

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for chunk_id, embedding in zip(chunk_ids, embeddings):
            emb_blob = embedding.astype(np.float32).tobytes()
            cursor.execute('''
                UPDATE chunks
                SET embedding = ?
                WHERE chunk_id = ?
            ''', (emb_blob, chunk_id))

        conn.commit()
        conn.close()

        final_count = _index.ntotal
        print(f"[INFO] Stored {len(chunk_ids)} embeddings. Index size: {final_count}")

    except Exception as e:
        print(f"[ERROR] Failed to store embeddings: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Error storing embeddings: {str(e)}")


def search_similar(query_embedding: np.ndarray, top_k: int = 5,
                   filter_docs: Optional[List[int]] = None, db_path: str = None) -> List[Dict]:
    """Search for similar chunks"""
    global _index, _index_to_chunk_id

    if faiss is None:
        raise Exception("FAISS not installed")

    try:
        if not isinstance(query_embedding, np.ndarray):
            raise TypeError("Query embedding must be numpy array")
        if query_embedding.ndim != 1:
            raise ValueError("Query embedding must be 1D")

        if _index is None:
            from services.embeddings import get_embedding_dimension
            initialize_index(db_path, get_embedding_dimension())

        if _index.ntotal == 0:
            print("[WARN] Index is empty")
            return []

        if len(query_embedding) != _index.d:
            raise ValueError(f"Dimension mismatch: {len(query_embedding)} vs {_index.d}")

        query_embedding = query_embedding.astype(np.float32)
        query_array = np.array([query_embedding], dtype=np.float32)
        query_array = np.ascontiguousarray(query_array)

        search_k = min(max(top_k * 3, 10), _index.ntotal)
        distances, indices = _index.search(query_array, search_k)

        from flask import current_app
        conn = sqlite3.connect(current_app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue

            chunk_id = _index_to_chunk_id.get(int(idx))
            if not chunk_id:
                continue

            cursor.execute('''
                SELECT c.*, d.filename
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                WHERE c.chunk_id = ?
            ''', (chunk_id,))

            row = cursor.fetchone()
            if row:
                doc_id = row['document_id']
                if filter_docs and doc_id not in filter_docs:
                    continue

                distance = distances[0][i]
                similarity = 1.0 / (1.0 + distance)

                results.append({
                    'chunk_id': chunk_id,
                    'document_id': doc_id,
                    'filename': row['filename'],
                    'content': row['content'],
                    'chunk_index': row['chunk_index'],
                    'similarity': float(similarity)
                })

                if len(results) >= top_k:
                    break

        conn.close()
        return results

    except Exception as e:
        print(f"[ERROR] Search failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Error searching: {str(e)}")


def delete_document_embeddings(document_id: int, db_path: str):
    """Delete embeddings for a document"""
    global _index, _index_to_chunk_id

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE chunks SET embedding = NULL WHERE document_id = ?', (document_id,))
        conn.commit()
        conn.close()

        _index = None
        _index_to_chunk_id.clear()

        from services.embeddings import get_embedding_dimension
        initialize_index(db_path, get_embedding_dimension())

        print(f"Removed embeddings for document {document_id}")

    except Exception as e:
        print(f"[WARN] Could not delete embeddings: {e}")


def get_vector_db_stats(db_path: str) -> Dict:
    """Get vector database statistics"""
    global _index

    print(f"[DEBUG] get_vector_db_stats called, _index is {_index}")

    try:
        if _index is not None:
            print(f"[DEBUG] Index exists, trying to access properties...")
            try:
                total = _index.ntotal
                dim = _index.d
                print(f"[DEBUG] Successfully got stats: total={total}, dim={dim}")
                return {
                    'total_vectors': int(total),
                    'dimension': int(dim),
                    'index_type': 'FAISS IndexFlatL2 (in-memory)'
                }
            except Exception as e:
                print(f"[ERROR] Could not access index: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[DEBUG] Index is None, returning defaults")

    except Exception as e:
        print(f"[ERROR] Error in get_vector_db_stats: {e}")
        import traceback
        traceback.print_exc()

    return {
        'total_vectors': 0,
        'dimension': 0,
        'index_type': 'Not initialized'
    }


def clear_vector_db(db_path: str):
    """Clear all vectors"""
    global _index, _index_to_chunk_id

    if faiss is None:
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE chunks SET embedding = NULL')
        conn.commit()
        conn.close()

        from services.embeddings import get_embedding_dimension
        dimension = get_embedding_dimension()
        _index = faiss.IndexFlatL2(dimension)
        _index_to_chunk_id.clear()

        print("Vector database cleared")
    except Exception as e:
        print(f"[WARN] Could not clear vector database: {e}")
