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


def generate_answer_with_llm(query: str, similar_chunks: List[Dict]) -> Tuple[str, float]:
    """
    Generate answer using an LLM (OpenAI, Anthropic, etc.)
    This requires API keys to be configured

    IMPLEMENTATION OPTIONS:
    1. OpenAI GPT-4/GPT-3.5
    2. Anthropic Claude
    3. Local LLMs (Llama, Mistral via Ollama)
    4. Azure OpenAI
    """

    # Build context from chunks
    context = "\n\n".join([
        f"[Source {i+1} - {chunk['filename']}]:\n{chunk['content']}"
        for i, chunk in enumerate(similar_chunks[:5])
    ])

    # Create a strict prompt that prevents hallucination
    prompt = f"""You are a helpful AI assistant answering questions based ONLY on the provided document context.

IMPORTANT RULES:
1. Answer ONLY using information from the provided context
2. If the context doesn't contain relevant information, say "I cannot find this information in the provided documents"
3. Do NOT make up, infer, or use general knowledge beyond what's in the context
4. Quote relevant sections from the context to support your answer
5. Be concise and direct

Context:
{context}

Question: {query}

Answer:"""

    try:
        # OPTION 1: Using OpenAI (requires openai library and API key)
        # import openai
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant that answers questions based ONLY on provided context. Never use external knowledge. If answer is not in context, say 'Not found in documents'."},
        #         {"role": "user", "content": prompt}
        #     ],
        #     temperature=0.1,  # Low temperature to reduce hallucination
        #     max_tokens=500
        # )
        # answer = response.choices[0].message.content
        # confidence = 0.8

        # OPTION 2: Using Anthropic Claude
        # from anthropic import Anthropic
        # client = Anthropic()
        # response = client.messages.create(
        #     model="claude-3-sonnet-20240229",
        #     max_tokens=500,
        #     system="You are a helpful assistant that answers questions based ONLY on provided context. Never use external knowledge. If answer is not in context, say 'Not found in documents'.",
        #     messages=[
        #         {"role": "user", "content": prompt}
        #     ]
        # )
        # answer = response.content[0].text
        # confidence = 0.85

        # OPTION 3: Using local LLM via Ollama (requires ollama installed)
        # import requests
        # response = requests.post('http://localhost:11434/api/generate',
        #     json={
        #         'model': 'llama2',
        #         'prompt': prompt,
        #         'stream': False,
        #         'temperature': 0.1
        #     })
        # answer = response.json()['response']
        # confidence = 0.7

        # For now, return the context-based answer
        answer = generate_answer_from_context(query, similar_chunks)
        confidence = 0.6

        return answer, confidence

    except Exception as e:
        print(f"[ERROR] LLM error: {str(e)}")
        return f"Error calling LLM: {str(e)}", 0.0


def rank_chunks(chunks: List[Dict], query: str) -> List[Dict]:
    """
    Re-rank chunks based on relevance to query

    Args:
        chunks: List of chunks to rank
        query: User query

    Returns:
        Sorted list of chunks
    """
    # For now, chunks are already sorted by similarity from vector search
    # In production, you could use cross-encoders for better ranking
    return chunks


def extract_key_phrases(text: str) -> List[str]:
    """
    Extract key phrases from text for better context understanding
    """
    # Simple implementation - split by sentences and take first few
    sentences = text.split('.')
    return [s.strip() for s in sentences[:3] if s.strip()]


def calculate_answer_confidence(query: str, answer: str, chunks: List[Dict]) -> float:
    """
    Calculate confidence score for the generated answer

    Factors:
    - Average similarity of retrieved chunks
    - Number of relevant chunks found
    - Overlap between query terms and context
    """
    if not chunks:
        return 0.0

    # Average similarity score
    avg_similarity = sum(chunk.get('similarity', 0) for chunk in chunks) / len(chunks)

    # Bonus for having multiple relevant chunks
    chunk_bonus = min(len(chunks) / 10.0, 0.2)

    # Calculate confidence
    confidence = min(avg_similarity + chunk_bonus, 1.0)

    return confidence

