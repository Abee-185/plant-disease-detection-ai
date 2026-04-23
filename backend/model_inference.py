"""
Model Inference Module
Handles image preprocessing and disease prediction
"""
import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image
import cv2
import os
from config import MODEL_PATH, IMAGE_SIZE, CLASS_LABELS, get_crop_type, get_disease_name, calculate_severity

class DiseasePredictor:
    def __init__(self):
        """Initialize the predictor"""
        self.model = None
        self.image_size = IMAGE_SIZE
        self.class_labels = CLASS_LABELS
    
    def load_model(self):
        """Load the trained model"""
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Please train the model first by running model_training.py"
            )
        
        self.model = keras.models.load_model(MODEL_PATH)
        print(f"✓ Model loaded from {MODEL_PATH}")
    
    def preprocess_image(self, image_path):
        """
        Preprocess image using OpenCV for model input
        
        Args:
            image_path: Path to image file
        
        Returns:
            Preprocessed image array ready for model
        """
        # 1. Load image using OpenCV
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError(f"Could not read image at {image_path}")
            
        # 2. OpenCV loads in BGR, convert to RGB for the AI model
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 3. Resize to model input size (224, 224)
        img = cv2.resize(img, self.image_size)
        
        # 5. Add batch dimension
        img_array = np.expand_dims(img, axis=0)
        
        # 6. Normalize pixel values (0-255 to 0-1)
        img_array = img_array.astype('float32') / 255.0
        
        return img_array
    
    def predict(self, image_path):
        """
        Predict disease from image
        
        Args:
            image_path: Path to leaf image
        
        Returns:
            Dictionary with prediction results
        """
        if self.model is None:
            self.load_model()
        
        # Preprocess image
        img_array = self.preprocess_image(image_path)
        
        # Make prediction
        predictions = self.model.predict(img_array, verbose=0)
        
        # Get predicted class
        predicted_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_idx])
        predicted_class = self.class_labels[predicted_idx]
        
        # Extract crop type and disease name
        crop_type = get_crop_type(predicted_class)
        disease_name = get_disease_name(predicted_class)
        
        # Calculate severity
        severity = calculate_severity(predicted_class, confidence)
        
        # Prepare result
        result = {
            'crop': crop_type,
            'disease': disease_name,
            'severity': severity,
            'confidence': round(confidence, 4),
            'predicted_class': predicted_class,
            'all_predictions': {
                self.class_labels[i]: float(predictions[0][i])
                for i in range(len(self.class_labels))
            }
        }
        
        return result
    
    def predict_batch(self, image_paths):
        """
        Predict diseases for multiple images
        
        Args:
            image_paths: List of image paths
        
        Returns:
            List of prediction dictionaries
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(image_path)
                results.append(result)
            except Exception as e:
                results.append({
                    'error': str(e),
                    'image_path': image_path
                })
        
        return results

# Create global predictor instance
predictor = DiseasePredictor()

# Test function
def test_prediction(image_path):
    """
    Test prediction on a single image
    
    Args:
        image_path: Path to test image
    """
    print(f"Testing prediction on: {image_path}")
    
    try:
        result = predictor.predict(image_path)
        
        print("\n" + "=" * 50)
        print("PREDICTION RESULTS")
        print("=" * 50)
        print(f"Crop Type:    {result['crop']}")
        print(f"Disease:      {result['disease']}")
        print(f"Severity:     {result['severity']}%")
        print(f"Confidence:   {result['confidence']:.2%}")
        print("=" * 50)
        
        print("\nAll Class Predictions:")
        for class_name, score in result['all_predictions'].items():
            print(f"  {class_name}: {score:.2%}")
        
        return result
    
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    import sys
    
    print("Plant Disease Predictor - Test Mode")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Test with provided image
        test_image = sys.argv[1]
        test_prediction(test_image)
    else:
        print("\nUsage: python model_inference.py <image_path>")
        print("Example: python model_inference.py test_leaf.jpg")
