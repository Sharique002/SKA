"""
RAG (Retrieval Augmented Generation) service for generating answers
"""
from typing import List, Dict, Tuple


def generate_answer(query: str, similar_chunks: List[Dict]) -> Tuple[str, float]:
    """
    Generate an answer based on the query and retrieved chunks

    Args:
        query: User's query
        similar_chunks: List of similar chunks retrieved from vector DB

    Returns:
        Tuple of (answer, confidence_score)
    """
    if not similar_chunks:
        return "I couldn't find relevant information to answer your query.", 0.0

    try:
        # Generate answer from chunks
        answer = generate_answer_from_context(query, similar_chunks)

        # Calculate confidence based on similarity scores
        avg_similarity = sum(chunk.get('similarity', 0) for chunk in similar_chunks) / len(similar_chunks)
        confidence = min(avg_similarity * 1.2, 1.0)  # Scale up slightly

        print(f"[INFO] Generated answer with confidence: {confidence:.2f}")
        return answer, confidence

    except Exception as e:
        print(f"[ERROR] Error generating answer: {str(e)}")
        return f"Error generating answer: {str(e)}", 0.0


def generate_answer_from_context(query: str, similar_chunks: List[Dict]) -> str:
    """
    Generate a concise, professional answer by synthesizing information from retrieved chunks.
    Mimics behavior of trained LLM RAG systems - short, direct, and well-synthesized.

    Args:
        query: User's question
        similar_chunks: List of relevant chunks

    Returns:
        Professional, synthesized answer based on context
    """
    if not similar_chunks:
        return "No relevant information found to answer the query."

    # Extract and clean content from top chunks
    cleaned_chunks = []
    for chunk in similar_chunks[:4]:  # Use top 4 most relevant chunks
        content = chunk['content'].strip()
        # Clean up excessive whitespace and remove URLs for cleaner output
        content = ' '.join(content.split())

        cleaned_chunks.append({
            'content': content,
            'filename': chunk.get('filename', 'Unknown'),
            'similarity': chunk.get('similarity', 0)
        })

    # Synthesize answer from chunks - extract key information
    answer_text = synthesize_answer(query, cleaned_chunks)

    # Build final answer with clean source attribution
    answer_parts = [answer_text]

    # Add concise source information
    source_list = []
    for chunk in cleaned_chunks[:3]:  # Show top 3 sources
        if chunk['similarity'] > 0.3:  # Only show relevant sources
            source_list.append(f"{chunk['filename']} ({chunk['similarity']:.0%})")

    if source_list:
        answer_parts.append(f"\n\n**Sources:** {', '.join(source_list)}")

    return "".join(answer_parts)


def synthesize_answer(query: str, chunks: List[Dict]) -> str:
    """
    Synthesize a concise, professional answer from retrieved chunks.
    Extracts key information and creates a natural, well-formed response.

    Args:
        query: User's question
        chunks: Cleaned and relevant chunks

    Returns:
        Synthesized answer (2-3 sentences)
    """
    if not chunks:
        return "I couldn't find relevant information to answer your question."

    # Extract key information from chunks
    combined_text = " ".join([chunk['content'] for chunk in chunks])

    # Remove excessive length and create a summary-like answer
    # Split into sentences for better processing
    sentences = combined_text.replace('  ', ' ').split('. ')

    # Take most relevant sentences (those that likely answer the query)
    query_words = set(query.lower().split())
    scored_sentences = []

    for sentence in sentences:
        if not sentence.strip():
            continue
        # Score sentence relevance to query
        sentence_lower = sentence.lower()
        relevance = sum(1 for word in query_words if word in sentence_lower)
        scored_sentences.append((sentence.strip(), relevance))

    # Sort by relevance and take top sentences
    scored_sentences.sort(key=lambda x: x[1], reverse=True)

    # Build answer from top 2-3 most relevant sentences
    answer_sentences = []
    for sentence, _ in scored_sentences[:3]:
        if sentence and len(answer_sentences) < 3:
            # Clean up the sentence
            sentence = sentence.replace('  ', ' ').strip()
            if sentence and not sentence.endswith('.'):
                sentence += '.'
            answer_sentences.append(sentence)

    if answer_sentences:
        answer = " ".join(answer_sentences[:2])  # Keep to 2 sentences max
        # Limit to ~300 characters for conciseness
        if len(answer) > 300:
            answer = answer[:297] + "..."
        return answer
    else:
        # Fallback: return first 200 chars of combined text
        text = combined_text[:200].strip()
        if not text.endswith('.'):
            text += '.'
        return text




