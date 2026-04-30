"""
Vector database service for storing and retrieving embeddings
Uses FAISS for efficient similarity search
"""
import numpy as np
import pickle
import os
from typing import List, Optional, Dict
import sqlite3


# Global FAISS index
_index = None
_index_to_chunk_id = {}
_index_path = 'db/faiss_index.pkl'
_mapping_path = 'db/index_mapping.pkl'


def initialize_index(dimension: int = 384):
    """
    Initialize or load the FAISS index
    
    Args:
        dimension: Dimension of the embedding vectors
    """
    global _index, _index_to_chunk_id
    
    try:
        import faiss
        
        # Try to load existing index
        if os.path.exists(_index_path) and os.path.exists(_mapping_path):
            print("Loading existing FAISS index...")
            with open(_index_path, 'rb') as f:
                _index = pickle.load(f)
            with open(_mapping_path, 'rb') as f:
                _index_to_chunk_id = pickle.load(f)
            print(f"Loaded index with {_index.ntotal} vectors")
        else:
            print("Creating new FAISS index...")
            # Create a new index (L2 distance)
            _index = faiss.IndexFlatL2(dimension)
            _index_to_chunk_id = {}
            save_index()
            print("New index created")
    
    except Exception as e:
        raise Exception(f"Error initializing FAISS index: {str(e)}")


def save_index():
    """Save the FAISS index and mapping to disk"""
    try:
        os.makedirs('db', exist_ok=True)
        
        with open(_index_path, 'wb') as f:
            pickle.dump(_index, f)
        
        with open(_mapping_path, 'wb') as f:
            pickle.dump(_index_to_chunk_id, f)
    
    except Exception as e:
        print(f"Warning: Could not save index: {e}")


def store_embeddings(chunk_ids: List[str], embeddings: List[np.ndarray],
                     chunks: List[str], document_id: int):
    """
    Store embeddings in the vector database

    Args:
        chunk_ids: List of chunk identifiers
        embeddings: List of embedding vectors
        chunks: List of chunk texts
        document_id: ID of the document
    """
    global _index, _index_to_chunk_id

    try:
        # Validate inputs
        if not chunk_ids or not embeddings or not chunks:
            raise ValueError("chunk_ids, embeddings, and chunks cannot be empty")

        if len(chunk_ids) != len(embeddings) or len(embeddings) != len(chunks):
            raise ValueError(f"Length mismatch: chunk_ids={len(chunk_ids)}, embeddings={len(embeddings)}, chunks={len(chunks)}")

        # Check embedding dimension consistency
        embedding_dim = None
        for i, emb in enumerate(embeddings):
            if not isinstance(emb, np.ndarray):
                raise TypeError(f"Embedding {i} is not a numpy array, got {type(emb)}")
            if emb.ndim != 1:
                raise ValueError(f"Embedding {i} is not 1D, shape={emb.shape}")
            if embedding_dim is None:
                embedding_dim = len(emb)
            elif len(emb) != embedding_dim:
                raise ValueError(f"Embedding dimension mismatch at index {i}: expected {embedding_dim}, got {len(emb)}")

        # Initialize index if needed
        if _index is None:
            initialize_index(embedding_dim)

        # Verify index dimension matches
        if _index.d != embedding_dim:
            raise ValueError(f"Index dimension {_index.d} does not match embedding dimension {embedding_dim}")

        # Convert embeddings to numpy array (float32)
        embeddings_array = np.array([e.astype('float32') if not e.dtype == np.float32 else e
                                     for e in embeddings], dtype='float32')

        print(f"[INFO] Embeddings array shape: {embeddings_array.shape}, dtype: {embeddings_array.dtype}")

        # Add to FAISS index
        start_idx = _index.ntotal
        _index.add(embeddings_array)

        # Update mapping
        for i, chunk_id in enumerate(chunk_ids):
            _index_to_chunk_id[start_idx + i] = chunk_id

        # Save the updated index
        save_index()

        print(f"[INFO] Stored {len(chunk_ids)} embeddings for document {document_id}. Index now has {_index.ntotal} vectors.")

    except Exception as e:
        print(f"[ERROR] Failed to store embeddings: {str(e)}")
        raise Exception(f"Error storing embeddings: {str(e)}")


def search_similar(query_embedding: np.ndarray, top_k: int = 5,
                   filter_docs: Optional[List[int]] = None) -> List[Dict]:
    """
    Search for similar chunks using the query embedding

    Args:
        query_embedding: Query embedding vector
        top_k: Number of results to return
        filter_docs: Optional list of document IDs to filter by

    Returns:
        List of similar chunks with metadata
    """
    global _index, _index_to_chunk_id

    try:
        # Validate query embedding
        if not isinstance(query_embedding, np.ndarray):
            raise TypeError(f"Query embedding must be numpy array, got {type(query_embedding)}")
        if query_embedding.ndim != 1:
            raise ValueError(f"Query embedding must be 1D, got shape {query_embedding.shape}")

        # Initialize index if needed
        if _index is None:
            print("[INFO] Index not initialized, initializing now...")
            from services.embeddings import get_embedding_dimension
            initialize_index(get_embedding_dimension())

        # Check if index is empty
        if _index.ntotal == 0:
            print("[WARN] Index is empty, returning no results")
            return []

        print(f"[INFO] Index has {_index.ntotal} vectors, dimension={_index.d}")

        # Verify query embedding dimension matches index
        if len(query_embedding) != _index.d:
            raise ValueError(f"Query embedding dimension {len(query_embedding)} does not match index dimension {_index.d}")

        # Prepare query - ensure float32
        query_embedding = query_embedding.astype('float32')
        query_array = np.array([query_embedding], dtype='float32')
        print(f"[INFO] Query array shape: {query_array.shape}, dtype: {query_array.dtype}")

        # Search for more results than needed (for filtering)
        search_k = min(max(top_k * 3, 10), _index.ntotal)
        print(f"[INFO] Searching for {search_k} neighbors (requesting top {top_k})")

        # FAISS search returns tuple: (distances, indices)
        distances, indices = _index.search(query_array, search_k)
        print(f"[INFO] Search results - distances shape: {distances.shape}, indices shape: {indices.shape}")

        # Get chunk information from database
        from flask import current_app
        conn = sqlite3.connect(current_app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:  # FAISS returns -1 for empty results
                continue

            chunk_id = _index_to_chunk_id.get(int(idx))
            if not chunk_id:
                print(f"[WARN] No chunk_id mapping for index {idx}")
                continue

            # Get chunk from database
            cursor.execute('''
                SELECT c.*, d.filename
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                WHERE c.chunk_id = ?
            ''', (chunk_id,))

            row = cursor.fetchone()
            if row:
                doc_id = row['document_id']

                # Apply document filter if provided
                if filter_docs and doc_id not in filter_docs:
                    continue

                # Convert L2 distance to similarity score (0-1)
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

        print(f"[INFO] Returning {len(results)} results")
        return results

    except Exception as e:
        print(f"[ERROR] Search failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Error searching similar chunks: {str(e)}")


def delete_document_embeddings(document_id: int):
    """
    Delete all embeddings for a document
    Note: FAISS doesn't support deletion, so we need to rebuild the index
    
    Args:
        document_id: ID of the document to delete
    """
    global _index, _index_to_chunk_id
    
    try:
        from flask import current_app
        import faiss
        
        # Get chunk IDs for this document
        conn = sqlite3.connect(current_app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute('SELECT chunk_id FROM chunks WHERE document_id = ?', (document_id,))
        chunk_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not chunk_ids:
            return
        
        # Find indices to remove
        indices_to_remove = set()
        for idx, chunk_id in _index_to_chunk_id.items():
            if chunk_id in chunk_ids:
                indices_to_remove.add(idx)
        
        if not indices_to_remove:
            return
        
        # Rebuild index without deleted vectors
        if _index and _index.ntotal > 0:
            # Get all vectors except those to delete
            all_vectors = []
            new_mapping = {}
            new_idx = 0
            
            for old_idx in range(_index.ntotal):
                if old_idx not in indices_to_remove:
                    vector = _index.reconstruct(int(old_idx))
                    all_vectors.append(vector)
                    new_mapping[new_idx] = _index_to_chunk_id[old_idx]
                    new_idx += 1
            
            # Create new index
            if all_vectors:
                dimension = len(all_vectors[0])
                _index = faiss.IndexFlatL2(dimension)
                vectors_array = np.array(all_vectors).astype('float32')
                _index.add(vectors_array)
                _index_to_chunk_id = new_mapping
            else:
                # No vectors left, create empty index
                dimension = _index.d
                _index = faiss.IndexFlatL2(dimension)
                _index_to_chunk_id = {}
            
            save_index()
            print(f"Removed {len(indices_to_remove)} vectors for document {document_id}")
    
    except Exception as e:
        print(f"Warning: Could not delete embeddings: {e}")


def get_vector_db_stats() -> Dict:
    """
    Get statistics about the vector database
    
    Returns:
        Dictionary with stats
    """
    global _index
    
    if _index is None:
        try:
            from services.embeddings import get_embedding_dimension
            initialize_index(get_embedding_dimension())
        except:
            pass
    
    if _index:
        return {
            'total_vectors': int(_index.ntotal),
            'dimension': int(_index.d),
            'index_type': 'FAISS IndexFlatL2'
        }
    else:
        return {
            'total_vectors': 0,
            'dimension': 0,
            'index_type': 'Not initialized'
        }


def clear_vector_db():
    """Clear all vectors from the database"""
    global _index, _index_to_chunk_id
    
    try:
        import faiss
        from services.embeddings import get_embedding_dimension
        
        dimension = get_embedding_dimension()
        _index = faiss.IndexFlatL2(dimension)
        _index_to_chunk_id = {}
        save_index()
        
        print("Vector database cleared")
    except Exception as e:
        print(f"Warning: Could not clear vector database: {e}")
