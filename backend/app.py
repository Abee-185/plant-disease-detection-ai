"""
Flask API for Biological Sprinkler
Plant Disease Detection Backend
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import traceback

# Import local modules
from config import (
    API_HOST, API_PORT, DEBUG_MODE, CORS_ORIGINS,
    UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
)
from model_inference import predictor
from database import db

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Enable CORS
CORS(app, resources={r"/*": {"origins": CORS_ORIGINS}})

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        'message': 'Biological Sprinkler API',
        'version': '1.0',
        'status': 'running',
        'endpoints': {
            '/health': 'Health check',
            '/analyze-leaf': 'POST - Analyze plant leaf image',
            '/stats': 'GET - Get analysis statistics',
            '/history': 'GET - Get recent analysis history'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check if model is loaded
        if predictor.model is None:
            predictor.load_model()
        
        return jsonify({
            'status': 'healthy',
            'model_loaded': True,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'model_loaded': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/analyze-leaf', methods=['POST'])
def analyze_leaf():
    """
    Main endpoint for plant disease detection
    
    Expects:
        - multipart/form-data with 'image' file
    
    Returns:
        JSON with crop type, disease name, and severity
    """
    try:
        # Check if image file is in request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"✓ Image uploaded: {filename}")
        
        # Load model if not loaded
        if predictor.model is None:
            print("Loading model...")
            predictor.load_model()
        
        # Run inference
        print("Running inference...")
        result = predictor.predict(filepath)
        
        print(f"✓ Prediction: {result['crop']} - {result['disease']} ({result['severity']}%)")
        
        # Store in database
        db_record_id = db.insert_analysis(
            image_name=filename,
            crop_type=result['crop'],
            disease_name=result['disease'],
            severity=result['severity'],
            confidence=result['confidence']
        )
        
        print(f"✓ Saved to database (ID: {db_record_id})")
        
        # Prepare response
        response = {
            'success': True,
            'crop': result['crop'],
            'disease': result['disease'],
            'severity': result['severity'],
            'confidence': result['confidence'],
            'timestamp': datetime.now().isoformat(),
            'record_id': db_record_id
        }
        
        # Optional: Delete uploaded file after processing to save space
        # os.remove(filepath)
        
        return jsonify(response)
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/history', methods=['GET'])
def get_history():
    """
    Get recent analysis history
    
    Query params:
        - limit: Number of records (default: 10)
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 100)  # Max 100 records
        
        records = db.get_recent_analyses(limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(records),
            'history': records
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def get_statistics():
    """Get overall analysis statistics"""
    try:
        stats = db.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🌱 BIOLOGICAL SPRINKLER API SERVER")
    print("=" * 50)
    print(f"Host: {API_HOST}")
    print(f"Port: {API_PORT}")
    print(f"Debug: {DEBUG_MODE}")
    print("=" * 50)
    
    # Try to load model on startup
    try:
        print("\n📦 Loading AI model...")
        predictor.load_model()
        print("✓ Model loaded successfully\n")
    except FileNotFoundError:
        print("⚠ Model not found. Please train the model first.")
        print("  Run: python model_training.py\n")
    except Exception as e:
        print(f"⚠ Error loading model: {e}\n")
    
    # Initialize database
    print("💾 Initializing database...")
    db.init_database()
    print()
    
    print("🚀 Starting server...")
    print(f"   API available at: http://localhost:{API_PORT}")
    print(f"   Test endpoint: http://localhost:{API_PORT}/health")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run Flask app
    port = int(os.environ.get("PORT", API_PORT))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=DEBUG_MODE
    )
