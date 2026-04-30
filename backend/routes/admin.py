"""
Admin route for managing documents and system
"""
import os
import sys
import sqlite3
from pathlib import Path

from flask import Blueprint, jsonify, current_app

# Ensure services can be imported
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.vectordb import delete_document_embeddings, get_vector_db_stats

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/documents', methods=['GET'])
def list_documents():
    """Get list of all documents in the system"""
    try:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, file_type, upload_date, file_size, num_chunks, status
            FROM documents
            ORDER BY upload_date DESC
        ''')
        
        documents = []
        for row in cursor.fetchall():
            documents.append({
                'id': row['id'],
                'filename': row['filename'],
                'file_type': row['file_type'],
                'upload_date': row['upload_date'],
                'file_size': row['file_size'],
                'num_chunks': row['num_chunks'],
                'status': row['status']
            })
        
        conn.close()
        
        return jsonify({
            'documents': documents,
            'total': len(documents)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/documents/<int:document_id>', methods=['GET'])
def get_document_details(document_id):
    """Get detailed information about a specific document"""
    try:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get document info
        cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
        doc = cursor.fetchone()
        
        if not doc:
            conn.close()
            return jsonify({'error': 'Document not found'}), 404
        
        # Get chunks info
        cursor.execute('''
            SELECT chunk_id, chunk_index, LENGTH(content) as content_length
            FROM chunks
            WHERE document_id = ?
            ORDER BY chunk_index
        ''', (document_id,))
        
        chunks = []
        for row in cursor.fetchall():
            chunks.append({
                'chunk_id': row['chunk_id'],
                'chunk_index': row['chunk_index'],
                'content_length': row['content_length']
            })
        
        conn.close()
        
        return jsonify({
            'id': doc['id'],
            'filename': doc['filename'],
            'file_type': doc['file_type'],
            'upload_date': doc['upload_date'],
            'file_size': doc['file_size'],
            'num_chunks': doc['num_chunks'],
            'status': doc['status'],
            'chunks': chunks
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/documents/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document and all its chunks"""
    try:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        cursor = conn.cursor()
        
        # Check if document exists
        cursor.execute('SELECT file_path FROM documents WHERE id = ?', (document_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'Document not found'}), 404
        
        file_path = result[0]
        
        # Delete from vector database
        delete_document_embeddings(document_id)
        
        # Delete chunks from database
        cursor.execute('DELETE FROM chunks WHERE document_id = ?', (document_id,))
        
        # Delete document from database
        cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
        
        conn.commit()
        conn.close()
        
        # Delete physical file if it exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not delete file {file_path}: {e}")
        
        return jsonify({
            'success': True,
            'message': f'Document {document_id} deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    try:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        cursor = conn.cursor()
        
        # Count total documents
        cursor.execute('SELECT COUNT(*) FROM documents')
        total_docs = cursor.fetchone()[0]
        
        # Count by status
        cursor.execute('SELECT status, COUNT(*) FROM documents GROUP BY status')
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Count total chunks
        cursor.execute('SELECT COUNT(*) FROM chunks')
        total_chunks = cursor.fetchone()[0]
        
        # Get total storage used
        cursor.execute('SELECT SUM(file_size) FROM documents')
        total_size = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Get vector DB stats
        vector_stats = get_vector_db_stats()
        
        return jsonify({
            'total_documents': total_docs,
            'status_breakdown': status_counts,
            'total_chunks': total_chunks,
            'total_storage_bytes': total_size,
            'total_storage_mb': round(total_size / (1024 * 1024), 2),
            'vector_db': vector_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/clear', methods=['POST'])
def clear_all_data():
    """Clear all documents and reset the system (use with caution)"""
    try:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        cursor = conn.cursor()
        
        # Get all file paths
        cursor.execute('SELECT file_path FROM documents')
        file_paths = [row[0] for row in cursor.fetchall() if row[0]]
        
        # Delete all chunks
        cursor.execute('DELETE FROM chunks')
        
        # Delete all documents
        cursor.execute('DELETE FROM documents')
        
        conn.commit()
        conn.close()
        
        # Delete physical files
        deleted_files = 0
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_files += 1
                except Exception as e:
                    print(f"Warning: Could not delete file {file_path}: {e}")
        
        # Clear vector database (if implemented)
        try:
            from services.vectordb import clear_vector_db
            clear_vector_db()
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': f'All data cleared. Deleted {deleted_files} files.'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
