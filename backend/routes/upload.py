"""
Upload route for handling document uploads
"""
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import uuid


from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

# Ensure services can be imported
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.extractor import extract_text
from services.chunker import chunk_text
from services.embeddings import generate_embeddings
from services.vectordb import store_embeddings

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'md'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/', methods=['POST'])
def upload_document():
    """
    Upload and process a document
    Accepts: multipart/form-data with 'file' field
    Returns: JSON with upload status and document ID
    """
    try:
        print(f"[INFO] Upload request received")
        print(f"[DEBUG] Request files: {request.files}")
        print(f"[DEBUG] Request content type: {request.content_type}")
        
        # Check if file is present
        if 'file' not in request.files:
            print(f"[ERROR] No file in request")
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        print(f"[INFO] File received: {file.filename}")
        
        if file.filename == '':
            print(f"[ERROR] Empty filename")
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            print(f"[ERROR] File type not allowed: {file.filename}")
            return jsonify({
                'success': False, 
                'message': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        print(f"[INFO] File validation passed")
        
        # Secure the filename and save
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # Ensure upload folder exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file with error handling
        try:
            print(f"[INFO] Saving file to: {filepath}")
            file.save(filepath)
            print(f"[INFO] File saved successfully")
        except Exception as e:
            print(f"[ERROR] Failed to save file: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Failed to save file: {str(e)}'
            }), 500
        
        file_size = os.path.getsize(filepath)
        file_type = filename.rsplit('.', 1)[1].lower()
        print(f"[INFO] File size: {file_size} bytes, type: {file_type}")
        
        # Insert document metadata into database
        conn = sqlite3.connect(current_app.config['DATABASE'])
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents (filename, file_type, file_size, status, file_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, file_type, file_size, 'processing', filepath))
        
        document_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Process the document
        try:
            # Step 1: Extract text
            print(f"[INFO] Extracting text from document...")
            text_content = extract_text(filepath, file_type)
            
            if not text_content or len(text_content.strip()) == 0:
                raise ValueError("No text content extracted from file")
            
            print(f"[INFO] Extracted {len(text_content)} characters")
            
            # Step 2: Chunk the text
            print(f"[INFO] Chunking text...")
            chunks = chunk_text(text_content)
            print(f"[INFO] Created {len(chunks)} chunks")
            
            # Step 3: Generate embeddings
            print(f"[INFO] Generating embeddings...")
            try:
                embeddings = generate_embeddings(chunks)
                print(f"[INFO] Generated {len(embeddings)} embeddings")
                
                if len(embeddings) != len(chunks):
                    raise ValueError(f"Embedding count mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks")
                    
            except Exception as embed_error:
                print(f"[ERROR] Embedding generation failed: {str(embed_error)}")
                raise ValueError(f"Failed to generate embeddings: {str(embed_error)}")
            
            # Step 4: Store in vector database
            print(f"[INFO] Storing in database...")
            chunk_ids = []
            conn = sqlite3.connect(current_app.config['DATABASE'])
            cursor = conn.cursor()
            
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{document_id}_{idx}_{uuid.uuid4().hex[:8]}"
                chunk_ids.append(chunk_id)
                
                # Store chunk metadata in SQLite
                cursor.execute('''
                    INSERT INTO chunks (chunk_id, document_id, content, chunk_index, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (chunk_id, document_id, chunk, idx, '{}'))
            
            # Update document status
            cursor.execute('''
                UPDATE documents 
                SET status = ?, num_chunks = ?
                WHERE id = ?
            ''', ('processed', len(chunks), document_id))
            
            conn.commit()
            conn.close()
            
            # Store embeddings in vector database
            store_embeddings(chunk_ids, embeddings, chunks, document_id, current_app.config['DATABASE'])
            
            print(f"[SUCCESS] Document processed successfully: ID={document_id}, chunks={len(chunks)}")
            
            return jsonify({
                'success': True,
                'message': 'Document uploaded and processed successfully',
                'document_id': document_id,
                'filename': filename,
                'num_chunks': len(chunks)
            }), 200
            
        except Exception as e:
            print(f"[ERROR] Processing failed: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Update status to failed
            try:
                conn = sqlite3.connect(current_app.config['DATABASE'])
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE documents 
                    SET status = ?
                    WHERE id = ?
                ''', ('failed', document_id))
                conn.commit()
                conn.close()
            except Exception as db_error:
                print(f"[ERROR] Failed to update document status: {str(db_error)}")
            
            # Return error response instead of raising
            return jsonify({
                'success': False,
                'message': f'Error processing document: {str(e)}'
            }), 500
    
    except Exception as e:
        print(f"[ERROR] Upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error processing document: {str(e)}'
        }), 500


@upload_bp.route('/status/<int:document_id>', methods=['GET'])
def get_upload_status(document_id):
    """Get the processing status of an uploaded document"""
    try:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
        doc = cursor.fetchone()
        conn.close()
        
        if not doc:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'id': doc['id'],
            'filename': doc['filename'],
            'status': doc['status'],
            'num_chunks': doc['num_chunks'],
            'upload_date': doc['upload_date']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
