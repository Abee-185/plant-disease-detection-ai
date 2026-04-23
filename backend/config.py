"""
Configuration settings for Biological Sprinkler AI Backend
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model configuration
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'plant_disease_model.h5')
IMAGE_SIZE = (224, 224)
INPUT_SHAPE = (224, 224, 3)

# Class labels - 6 classes total
# NOTE: These must match the exact folder names in the dataset
CLASS_LABELS = [
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Tomato_Early_blight',      # Note: Single underscore (not triple)
    'Tomato_Late_blight',        # Note: Single underscore (not triple)
    'Tomato_healthy'             # Note: Single underscore (not triple)
]

# Class mapping for display
DISEASE_DISPLAY_NAMES = {
    'Potato___Early_blight': 'Early Blight',
    'Potato___Late_blight': 'Late Blight',
    'Potato___healthy': 'Healthy',
    'Tomato_Early_blight': 'Early Blight',
    'Tomato_Late_blight': 'Late Blight',
    'Tomato_healthy': 'Healthy'
}

# Extract crop type from class name
def get_crop_type(class_name):
    """Extract crop type from class label"""
    # Handle both formats (triple and single underscore)
    if '___' in class_name:
        return class_name.split('___')[0]
    else:
        return class_name.split('_')[0]

def get_disease_name(class_name):
    """Get display name for disease"""
    return DISEASE_DISPLAY_NAMES.get(class_name, 'Unknown')

# Upload configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'analysis_history.db')

# API configuration
API_HOST = '0.0.0.0'
API_PORT = 5000
DEBUG_MODE = True

# CORS settings
CORS_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Severity calculation parameters
def calculate_severity(disease_class, confidence):
    """
    Convert model confidence to severity percentage
    
    Args:
        disease_class: Predicted class name
        confidence: Model confidence score (0-1)
    
    Returns:
        Severity percentage (0-100)
    """
    disease_lower = disease_class.lower()
    
    if 'healthy' in disease_lower:
        # Healthy plants have low severity
        # Higher confidence in healthy = lower severity
        severity = max(0, 20 - (confidence * 20))
    else:
        # Diseased plants: higher confidence = higher severity
        if 'early' in disease_lower:
            # Early blight: moderate severity range
            severity = 40 + (confidence * 40)  # 40-80%
        elif 'late' in disease_lower:
            # Late blight: high severity range
            severity = 60 + (confidence * 40)  # 60-100%
        else:
            # Other diseases
            severity = 50 + (confidence * 50)  # 50-100%
    
    return min(100, max(0, int(severity)))
