"""
Embedding generation service using sentence transformers
"""
from typing import List
import numpy as np


# Global model instance
_model = None


def get_model():
    """
    Load and cache the embedding model
    Using sentence-transformers for high-quality embeddings
    """
    global _model
    
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use a lightweight but effective model
            # Options: 'all-MiniLM-L6-v2' (fast), 'all-mpnet-base-v2' (better quality)
            model_name = 'all-MiniLM-L6-v2'
            print(f"Loading embedding model: {model_name}")
            _model = SentenceTransformer(model_name)
            print("Model loaded successfully")
        except Exception as e:
            raise Exception(f"Error loading embedding model: {str(e)}")
    
    return _model


def generate_embeddings(texts: List[str]) -> List[np.ndarray]:
    """
    Generate embeddings for a list of texts

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors (numpy arrays)
    """
    if not texts:
        return []

    try:
        model = get_model()
        print(f"[INFO] Generating embeddings for {len(texts)} texts...")

        # Process in batches to avoid memory issues
        batch_size = 32
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size
            print(f"[INFO] Processing batch {batch_num}/{total_batches}")

            # Generate embeddings for batch
            batch_embeddings = model.encode(batch, show_progress_bar=False, convert_to_numpy=True)

            # batch_embeddings is always 2D: (batch_size, embedding_dim)
            # Convert to list of 1D arrays
            if isinstance(batch_embeddings, np.ndarray):
                if len(batch_embeddings.shape) == 1:
                    # Single embedding case, reshape to 2D then back to list
                    all_embeddings.append(batch_embeddings)
                else:
                    # Multiple embeddings, convert each row to a 1D array
                    all_embeddings.extend([batch_embeddings[j] for j in range(batch_embeddings.shape[0])])
            else:
                raise TypeError(f"Expected numpy array, got {type(batch_embeddings)}")

        print(f"[INFO] Generated {len(all_embeddings)} embeddings with dimension {len(all_embeddings[0]) if all_embeddings else 0}")
        return all_embeddings

    except Exception as e:
        print(f"[ERROR] Embedding generation failed: {str(e)}")
        raise Exception(f"Error generating embeddings: {str(e)}")


def compute_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embeddings
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Similarity score between 0 and 1
    """
    try:
        # Cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Ensure it's between 0 and 1
        similarity = max(0.0, min(1.0, similarity))
        
        return float(similarity)
    
    except Exception as e:
        raise Exception(f"Error computing similarity: {str(e)}")


def batch_generate_embeddings(texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
    """
    Generate embeddings in batches for large datasets
    
    Args:
        texts: List of texts to embed
        batch_size: Number of texts to process at once
    
    Returns:
        List of embeddings
    """
    if not texts:
        return []
    
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = generate_embeddings(batch)
        all_embeddings.extend(embeddings)
    
    return all_embeddings


def get_embedding_dimension() -> int:
    """
    Get the dimension of the embedding vectors
    
    Returns:
        Dimension size (e.g., 384 for all-MiniLM-L6-v2)
    """
    model = get_model()
    return model.get_sentence_embedding_dimension()
