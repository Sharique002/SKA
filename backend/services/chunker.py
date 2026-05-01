"""
Text chunking service for splitting documents into manageable pieces
"""
from typing import List
import re


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks

    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk in characters (default: 700, range 500-800)
        overlap: Number of characters to overlap between chunks (default: 100, range 50-100)

    Returns:
        List of text chunks
    """
    if not text or len(text.strip()) == 0:
        print("[WARN] Empty text provided for chunking")
        return []

    # Clean the text
    text = clean_text(text)

    # Try semantic chunking first (by paragraphs/sentences)
    chunks = semantic_chunking(text, chunk_size, overlap)

    # If semantic chunking produces too few chunks, fall back to simple chunking
    if len(chunks) < 2 and len(text) > chunk_size:
        print("[INFO] Semantic chunking produced too few chunks, using simple chunking")
        chunks = simple_chunking(text, chunk_size, overlap)

    print(f"[INFO] Created {len(chunks)} chunks from {len(text)} characters")
    return chunks


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove excessive newlines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    return text.strip()


def semantic_chunking(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Chunk text semantically by preserving paragraph and sentence boundaries
    """
    chunks = []
    
    # Split by paragraphs
    paragraphs = re.split(r'\n\n+', text)
    
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # If adding this paragraph exceeds chunk size
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Create overlap by taking last part of current chunk
            if overlap > 0 and len(current_chunk) > overlap:
                overlap_text = current_chunk[-overlap:]
                # Try to start overlap at a sentence boundary
                sentences = re.split(r'[.!?]+\s+', overlap_text)
                if len(sentences) > 1:
                    overlap_text = '. '.join(sentences[1:])
                current_chunk = overlap_text + " " + para
            else:
                current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def simple_chunking(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Simple character-based chunking with overlap
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # If not at the end, try to break at a space or punctuation
        if end < text_length:
            # Look for a good breaking point
            break_point = text.rfind(' ', start, end)
            if break_point > start:
                end = break_point
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap if end < text_length else text_length
        
        # Ensure we make progress (avoid infinite loop)
        if len(chunks) > 0 and start < text_length:
            # If we haven't moved forward enough, force progress
            prev_end = len(text[:end])
            if start >= prev_end - overlap:
                start = end
    
    return chunks



