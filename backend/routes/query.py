"""
Query route for handling knowledge queries
"""
import sys
import time
import traceback
from pathlib import Path

from flask import Blueprint, request, jsonify, current_app

# Ensure services can be imported
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

query_bp = Blueprint('query', __name__)


@query_bp.route('/', methods=['POST'])
def query_knowledge():
    """
    Query the knowledge base
    Accepts: JSON with 'query' field
    Returns: JSON with answer, sources, and confidence
    """
    try:
        start_time = time.time()

        # Get query from request
        data = request.get_json()

        if not data or 'query' not in data:
            print("[ERROR] No query provided in request")
            return jsonify({'error': 'No query provided'}), 400

        query_text = data['query'].strip()
        top_k = data.get('top_k', 5)
        filter_docs = data.get('filter_docs', None)

        if not query_text or len(query_text) == 0:
            print("[ERROR] Query is empty")
            return jsonify({'error': 'Query cannot be empty'}), 400

        # Validate top_k
        if not isinstance(top_k, int) or top_k < 1 or top_k > 50:
            print(f"[WARN] Invalid top_k value: {top_k}, using default 5")
            top_k = 5

        print(f"[INFO] Processing query: '{query_text[:100]}...' with top_k={top_k}")

        try:
            # Step 1: Generate embedding for the query
            print(f"[INFO] Generating embedding for query...")
            from services.embeddings import generate_embeddings
            query_embeddings = generate_embeddings([query_text])

            if not query_embeddings or len(query_embeddings) == 0:
                print("[ERROR] Failed to generate query embedding")
                return jsonify({
                    'error': 'Failed to generate query embedding',
                    'processing_time': time.time() - start_time
                }), 500

            query_embedding = query_embeddings[0]
            print(f"[INFO] Query embedding shape: {query_embedding.shape}")

        except Exception as e:
            print(f"[ERROR] Embedding generation failed: {str(e)}")
            traceback.print_exc()
            return jsonify({
                'error': f'Embedding generation failed: {str(e)}',
                'processing_time': time.time() - start_time
            }), 500

        try:
            # Step 2: Search for similar chunks
            print(f"[INFO] Searching for similar chunks...")
            from services.vectordb import search_similar
            similar_chunks = search_similar(query_embedding, top_k=top_k, filter_docs=filter_docs, db_path=current_app.config['DATABASE'])
            print(f"[INFO] Found {len(similar_chunks)} similar chunks")

        except Exception as e:
            print(f"[ERROR] Search failed: {str(e)}")
            traceback.print_exc()
            return jsonify({
                'error': f'Vector search failed: {str(e)}',
                'processing_time': time.time() - start_time
            }), 500

        if not similar_chunks:
            print("[INFO] No similar chunks found")
            return jsonify({
                'answer': 'I could not find relevant information to answer your query. Please try rephrasing or upload more documents.',
                'sources': [],
                'confidence': 0.0,
                'processing_time': time.time() - start_time
            }), 200

        try:
            # Step 3: Generate answer using RAG
            print(f"[INFO] Generating answer from {len(similar_chunks)} chunks...")
            from services.rag import generate_answer
            answer, confidence = generate_answer(query_text, similar_chunks)
            print(f"[INFO] Answer generated with confidence: {confidence:.2f}")

        except Exception as e:
            print(f"[ERROR] Answer generation failed: {str(e)}")
            traceback.print_exc()
            return jsonify({
                'error': f'Answer generation failed: {str(e)}',
                'processing_time': time.time() - start_time
            }), 500

        # Prepare sources with safety checks
        sources = []
        for chunk in similar_chunks:
            try:
                source_item = {
                    'document_id': chunk.get('document_id'),
                    'filename': chunk.get('filename', 'Unknown'),
                    'content': chunk['content'][:300] + '...' if len(chunk.get('content', '')) > 300 else chunk.get('content', ''),
                    'similarity': float(chunk.get('similarity', 0.0))
                }
                sources.append(source_item)
            except Exception as e:
                print(f"[WARN] Error processing source: {str(e)}")
                continue

        processing_time = time.time() - start_time
        print(f"[INFO] Query processing completed in {processing_time:.2f}s")

        return jsonify({
            'answer': answer,
            'sources': sources,
            'confidence': float(confidence),
            'processing_time': processing_time,
            'num_sources': len(similar_chunks)
        }), 200

    except Exception as e:
        print(f"[ERROR] Query processing failed: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': f'Unexpected error: {str(e)}',
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0
        }), 500


@query_bp.route('/search', methods=['POST'])
def search_documents():
    """
    Search for documents containing specific keywords
    Accepts: JSON with 'keywords' field
    Returns: JSON with matching documents
    """
    try:
        data = request.get_json()
        
        if not data or 'keywords' not in data:
            return jsonify({'error': 'No keywords provided'}), 400
        
        keywords = data['keywords']

        # Generate embedding for keywords
        from services.embeddings import generate_embeddings
        keyword_embedding = generate_embeddings([keywords])[0]

        # Search for similar content
        from services.vectordb import search_similar
        results = search_similar(keyword_embedding, top_k=10, db_path=current_app.config['DATABASE'])
        
        # Group by document
        doc_results = {}
        for result in results:
            doc_id = result['document_id']
            if doc_id not in doc_results:
                doc_results[doc_id] = {
                    'document_id': doc_id,
                    'filename': result.get('filename', 'Unknown'),
                    'matches': []
                }
            doc_results[doc_id]['matches'].append({
                'content': result['content'][:150] + '...' if len(result['content']) > 150 else result['content'],
                'similarity': result.get('similarity', 0.0)
            })
        
        return jsonify({
            'results': list(doc_results.values()),
            'total_documents': len(doc_results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
