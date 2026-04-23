"""
Plant Disease Detection Model Training
Using MobileNetV2 with Transfer Learning
"""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import numpy as np
from config import IMAGE_SIZE, CLASS_LABELS, MODEL_PATH

class PlantDiseaseModel:
    def __init__(self):
        """Initialize the model trainer"""
        self.image_size = IMAGE_SIZE
        self.num_classes = len(CLASS_LABELS)
        self.model = None
    
    def create_model(self):
        """
        Create MobileNetV2 model with transfer learning
        
        Returns:
            Compiled Keras model
        """
        # Load pre-trained MobileNetV2 (without top classification layer)
        base_model = MobileNetV2(
            input_shape=(224, 224, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Add custom classification head
        inputs = keras.Input(shape=(224, 224, 3))
        
        # Preprocessing
        x = layers.Rescaling(1./255)(inputs)
        
        # Base model
        x = base_model(x, training=False)
        
        # Global pooling and classification
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.2)(x)
        outputs = layers.Dense(self.num_classes, activation='softmax')(x)
        
        # Create model
        model = keras.Model(inputs, outputs)
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        print("✓ Model created successfully")
        return model
    
    def create_demo_model(self):
        """
        Create a simple demo model without training
        This is used when dataset is not available
        """
        self.create_model()
        
        # Save untrained model (will give random predictions initially)
        # In production, this should be replaced with pre-trained weights
        print("✓ Demo model created (untrained)")
        return self.model
    
    def train_with_data_generator(self, train_dir, val_dir, epochs=10):
        """
        Train model using ImageDataGenerator
        
        Args:
            train_dir: Path to training data directory
            val_dir: Path to validation data directory
            epochs: Number of training epochs
        """
        if self.model is None:
            self.create_model()
        
        # Data augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            shear_range=0.2,
            fill_mode='nearest'
        )
        
        # Only rescaling for validation
        val_datagen = ImageDataGenerator(rescale=1./255)
        
        # Load training data
        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=self.image_size,
            batch_size=32,
            class_mode='categorical',
            classes=CLASS_LABELS
        )
        
        # Load validation data
        val_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=self.image_size,
            batch_size=32,
            class_mode='categorical',
            classes=CLASS_LABELS
        )
        
        # Train model
        history = self.model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=epochs,
            verbose=1
        )
        
        print("✓ Training completed")
        return history
    
    def fine_tune(self, train_dir, val_dir, epochs=5):
        """
        Fine-tune by unfreezing some base model layers
        
        Args:
            train_dir: Path to training data
            val_dir: Path to validation data
            epochs: Number of fine-tuning epochs
        """
        if self.model is None:
            raise ValueError("Model must be created and initially trained first")
        
        # Unfreeze the base model
        base_model = self.model.layers[2]  # MobileNetV2 base
        base_model.trainable = True
        
        # Freeze all layers except the last 20
        for layer in base_model.layers[:-20]:
            layer.trainable = False
        
        # Recompile with lower learning rate
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Continue training
        print("✓ Fine-tuning model...")
        history = self.train_with_data_generator(train_dir, val_dir, epochs)
        
        return history
    
    def save_model(self, path=None):
        """Save trained model to disk"""
        if self.model is None:
            raise ValueError("No model to save")
        
        save_path = path or MODEL_PATH
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        self.model.save(save_path)
        print(f"✓ Model saved to {save_path}")
    
    def load_model(self, path=None):
        """Load trained model from disk"""
        load_path = path or MODEL_PATH
        
        if not os.path.exists(load_path):
            raise FileNotFoundError(f"Model not found at {load_path}")
        
        self.model = keras.models.load_model(load_path)
        print(f"✓ Model loaded from {load_path}")
        return self.model
    
    def evaluate_model(self, test_dir):
        """
        Evaluate model on test data
        
        Args:
            test_dir: Path to test data directory
        
        Returns:
            Evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model must be loaded first")
        
        test_datagen = ImageDataGenerator(rescale=1./255)
        test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=self.image_size,
            batch_size=32,
            class_mode='categorical',
            classes=CLASS_LABELS
        )
        
        results = self.model.evaluate(test_generator)
        print(f"Test Loss: {results[0]:.4f}")
        print(f"Test Accuracy: {results[1]:.4f}")
        
        return results

# Quick training script
if __name__ == '__main__':
    print("=" * 50)
    print("Plant Disease Detection - Model Training")
    print("=" * 50)
    
    trainer = PlantDiseaseModel()
    
    # Check if dataset exists (checking both 'dataset' and 'Dataset')
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'Dataset')
    
    if not os.path.exists(dataset_path):
        dataset_path = os.path.join(os.path.dirname(__file__), '..', 'dataset')
    
    if os.path.exists(dataset_path):
        print(f"\n✓ Dataset found at: {dataset_path}")
        
        # Check if train/val folders exist
        train_dir = os.path.join(dataset_path, 'train')
        val_dir = os.path.join(dataset_path, 'val')
        
        if os.path.exists(train_dir) and os.path.exists(val_dir):
            print("✓ Train and validation folders found")
            print("\nStarting training...")
            
            # Create and train model
            trainer.create_model()
            trainer.train_with_data_generator(train_dir, val_dir, epochs=10)
            
            # Optional: Fine-tune
            # trainer.fine_tune(train_dir, val_dir, epochs=5)
            
            # Save model
            trainer.save_model()
            
            print("\n✓ Training complete! Model saved.")
        else:
            print("\n⚠ Dataset found but needs to be organized into train/val folders")
            print(f"   Dataset location: {dataset_path}")
            print("\n📋 Next steps:")
            print("   1. The dataset has all images in class folders")
            print("   2. We need to split them into train (80%) and val (20%)")
            print("   3. Run the prepare_dataset.py script to organize it")
            print(f"\n💡 Run: python prepare_dataset.py")
            
            # Create demo model for now
            print("\nCreating demo model for now...")
            trainer.create_demo_model()
            trainer.save_model()
            print("✓ Demo model created")
    else:
        print("\n⚠ Dataset not found. Creating demo model...")
        print("Note: This model needs to be trained with real data for production use.")
        
        # Create untrained model for demo
        trainer.create_demo_model()
        trainer.save_model()
        
        print("\n✓ Demo model created. To train with real data:")
        print("  1. Download PlantVillage dataset")
        print("  2. Organize in 'dataset/train' and 'dataset/val' folders")
        print("  3.Run this script again")
