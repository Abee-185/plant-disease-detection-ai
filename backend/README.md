# Biological Sprinkler - Backend API

AI-Based Plant Disease Detection Engine

## 🎯 Overview

This backend provides AI-powered plant disease detection for Tomato and Potato plants using deep learning (MobileNetV2).

## 📋 Features

- ✅ MobileNetV2 CNN model with transfer learning
- ✅ Support for 6 disease classes (Tomato & Potato)
- ✅ REST API with Flask
- ✅ SQLite database for analysis history
- ✅ Confidence to severity conversion
- ✅ CORS enabled for web integration

## 🔬 Supported Diseases

### Tomato
- Healthy
- Early Blight
- Late Blight

### Potato
- Healthy
- Early Blight
- Late Blight

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Train the model** (or use demo mode):
```bash
python model_training.py
```

This will:
- Create a MobileNetV2 model
- Train with dataset if available
- Or create a demo model for testing

3. **Start the API server**:
```bash
python app.py
```

Server will run at: `http://localhost:5000`

## 🚀 API Endpoints

### 1. Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-02-04T16:15:30"
}
```

### 2. Analyze Leaf Image (Main Endpoint)
```http
POST /analyze-leaf
Content-Type: multipart/form-data

image: [file]
```

Response:
```json
{
  "success": true,
  "crop": "Tomato",
  "disease": "Early Blight",
  "severity": 68,
  "confidence": 0.9234,
  "timestamp": "2026-02-04T16:15:30",
  "record_id": 1
}
```

### 3. Get Analysis History
```http
GET /history?limit=10
```

Response:
```json
{
  "success": true,
  "count": 10,
  "history": [...]
}
```

### 4. Get Statistics
```http
GET /stats
```

Response:
```json
{
  "success": true,
  "statistics": {
    "total_analyses": 25,
    "healthy_count": 10,
    "diseased_count": 15,
    "average_severity": 54.2
  }
}
```

## 🧪 Testing

### Using cURL

```bash
# Test with an image
curl -X POST -F "image=@test_leaf.jpg" http://localhost:5000/analyze-leaf

# Check health
curl http://localhost:5000/health

# Get statistics
curl http://localhost:5000/stats
```

### Using Python

```python
import requests

# Upload and analyze image
url = 'http://localhost:5000/analyze-leaf'
files = {'image': open('test_leaf.jpg', 'rb')}
response = requests.post(url, files=files)
result = response.json()

print(f"Crop: {result['crop']}")
print(f"Disease: {result['disease']}")
print(f"Severity: {result['severity']}%")
```

## 📊 Model Training (Advanced)

### With PlantVillage Dataset

1. **Download Dataset**:
   - Get PlantVillage dataset from Kaggle
   - Extract to `dataset/` folder
   - Organize as:
     ```
     dataset/
     ├── train/
     │   ├── Tomato___healthy/
     │   ├── Tomato___Early_blight/
     │   ├── Tomato___Late_blight/
     │   ├── Potato___healthy/
     │   ├── Potato___Early_blight/
     │   └── Potato___Late_blight/
     └── val/
         └── [same structure]
     ```

2. **Train Model**:
```bash
python model_training.py
```

Training will:
- Load MobileNetV2 pre-trained on ImageNet
- Fine-tune on plant disease data
- Save model to `models/plant_disease_model.h5`
- Expected accuracy: 85-95%

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Image size
IMAGE_SIZE = (224, 224)

# API settings
API_PORT = 5000

# Severity calculation
def calculate_severity(disease_class, confidence):
    # Custom logic here
    pass
```

## 🗃️ Database

SQLite database stores:
- Image name
- Crop type
- Disease name
- Severity percentage
- Confidence score
- Timestamp

Location: `backend/database/analysis_history.db`

## 🌐 Frontend Integration

Update `frontend/app.js` to use real API:

```javascript
// In analyzeImage() function
async function analyzeImage() {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch('http://localhost:5000/analyze-leaf', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    
    if (result.success) {
        displayAnalysisResults({
            crop: result.crop,
            disease: result.disease,
            severity: result.severity,
            // ...
        });
    }
}
```

## 📈 Performance

- **Inference Time**: ~100-300ms per image (CPU)
- **Model Size**: ~15MB
- **Accuracy**: 85-95% (depending on training)

## 🚢 Deployment

### Local Development
```bash
python app.py
```

### Production Options

1. **Heroku**:
```bash
heroku create biological-sprinkler-api
git push heroku main
```

2. **Docker**:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

3. **Render/Railway**: Push to Git and connect

## 🐛 Troubleshooting

### Model not found
```
Error: Model not found at backend/models/plant_disease_model.h5
Solution: Run python model_training.py
```

### CORS errors
```
Solution: Check CORS_ORIGINS in config.py includes your frontend URL
```

### Low accuracy
```
Solution: Train with more data or increase epochs
```

## 📝 File Structure

```
backend/
├── app.py                    # Flask API server
├── config.py                 # Configuration
├── database.py               # Database operations
├── model_training.py         # Model training script
├── model_inference.py        # Inference logic
├── requirements.txt          # Dependencies
├── README.md                 # This file
├── models/                   # Trained models
│   └── plant_disease_model.h5
├── uploads/                  # Temporary uploads
└── database/                 # SQLite database
    └── analysis_history.db
```

## 🎓 For College Projects

This backend is suitable for:
- ✅ Smart India Hackathon
- ✅ College mini projects
- ✅ Research presentations
- ✅ Product demonstrations

## 📄 License

For educational and demonstration purposes.

## 🤝 Support

For issues or questions, check:
1. API health: http://localhost:5000/health
2. Console logs for errors
3. Database records for history

---

**🌱 Built for Biological Sprinkler - Smart Agriculture System**
