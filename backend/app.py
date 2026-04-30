"""
Main Flask application for SKA backend
"""
import os
import sys
import sqlite3
from flask import Flask, jsonify
from flask_cors import CORS

# Add backend directory to path for proper imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import routes
from routes.upload import upload_bp
from routes.query import query_bp
from routes.admin import admin_bp

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "send_wildcard": True, "max_age": 3600}})

# Configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['DATABASE'] = os.getenv('DATABASE_PATH', 'db/metadata.db')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TIMEOUT'] = 300  # 5 minutes timeout
app.config['MAX_CONTENT_PATH'] = None  # Allow large uploads

# Ensure necessary directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('db', exist_ok=True)

print("[INFO] Flask app initialized")
print(f"[INFO] Upload folder: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")
print(f"[INFO] Database: {os.path.abspath(app.config['DATABASE'])}")


def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()

    # Create documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER NOT NULL,
            num_chunks INTEGER DEFAULT 0,
            status TEXT DEFAULT 'processing',
            file_path TEXT
        )
    ''')

    # Create chunks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            document_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            metadata TEXT,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("[INFO] Database initialized")


# Initialize database on startup
with app.app_context():
    init_database()


# Register blueprints
app.register_blueprint(upload_bp, url_prefix='/api/upload')
app.register_blueprint(query_bp, url_prefix='/api/query')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

print("[INFO] Blueprints registered")


@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'SKA Backend',
        'version': '1.0.0'
    })


@app.route('/api/health')
def health():
    """Detailed health check"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'upload_folder': os.path.exists(app.config['UPLOAD_FOLDER'])
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    print(f"[INFO] Starting SKA Backend server on port {port}...")
    app.run(debug=debug, host='0.0.0.0', port=port)

