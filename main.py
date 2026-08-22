import os
import cv2
import pandas as pd
import numpy as np
import random
import logging
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.utils.class_weight import compute_class_weight

# ========================
# SETUP & CONFIGURATION
# ========================

# Set random seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DATADIR = "dataset"
CATEGORIES = ["glioma", "meningioma", "pituitary", "notumor"]
IMG_SIZE = 128
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.0001

logger.info(f"Configuration: IMG_SIZE={IMG_SIZE}, BATCH_SIZE={BATCH_SIZE}, EPOCHS={EPOCHS}")

# ========================
# DATA LOADING
# ========================

def create_training_data():
    """Load and preprocess training data from disk."""
    training_data = []
    
    for category in CATEGORIES:
        path = os.path.join(DATADIR, category)
        
        if not os.path.exists(path):
            logger.warning(f"Directory not found: {path}")
            continue
        
        class_num = CATEGORIES.index(category)
        images = os.listdir(path)
        logger.info(f"Loading {len(images)} images from {category}...")
        
        failed_count = 0
        for img_name in images:
            try:
                img_path = os.path.join(path, img_name)
                img_array = cv2.imread(img_path)
                
                # Validate image loaded correctly
                if img_array is None:
                    logger.warning(f"Failed to load (None): {img_name}")
                    failed_count += 1
                    continue
                
                # Resize and add to training data
                img_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
                training_data.append([img_array, class_num])
                
            except Exception as e:
                logger.error(f"Error loading {img_name}: {e}")
                failed_count += 1
        
        loaded = len(images) - failed_count
        logger.info(f"✓ {category}: Loaded {loaded}/{len(images)} images (Failed: {failed_count})")
    
    logger.info(f"Total images loaded: {len(training_data)}")
    return training_data

# Load and shuffle data
logger.info("Loading dataset...")
training_data = create_training_data()

if not training_data:
    raise ValueError("No training data loaded! Check dataset directory.")

random.shuffle(training_data)
logger.info("Data shuffled")

# ========================
# DATA PREPARATION
# ========================

# Split features and labels
X = np.array([features for features, label in training_data])
y = np.array([label for features, label in training_data])

# Reshape and normalize
X = X.reshape(-1, IMG_SIZE, IMG_SIZE, 3).astype("float32") / 255.0

# Print class distribution (IMPORTANT for medical AI)
logger.info("\n=== CLASS DISTRIBUTION ===")
class_counts = np.bincount(y)
for category, count in zip(CATEGORIES, class_counts):
    percentage = 100 * count / len(y)
    logger.info(f"{category:12s}: {count:4d} samples ({percentage:5.1f}%)")

# Check for class imbalance
if max(class_counts) / min(class_counts) > 2:
    logger.warning("⚠️  Class imbalance detected! Consider using class weights.")

# Compute class weights
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y),
    y=y
)
class_weight_dict = dict(enumerate(class_weights))

# ========================
# TRAIN/VAL/TEST SPLIT
# ========================

# 70% train, 15% validation, 15% test
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.15, random_state=SEED
)

X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.176, random_state=SEED  # ~15% of original
)

logger.info("\n=== DATA SPLIT ===")
logger.info(f"Train: {len(X_train)} samples")
logger.info(f"Val:   {len(X_val)} samples")
logger.info(f"Test:  {len(X_test)} samples")

# ========================
# DATA AUGMENTATION
# ========================
datagen = ImageDataGenerator(
    rotation_range=15,
    zoom_range=0.1,
    width_shift_range=0.05,
    height_shift_range=0.05,
    brightness_range=[0.9, 1.1]
)

datagen.fit(X_train)
logger.info("Data augmentation configured")

# ========================
# BUILD MODEL
# ========================

model = Sequential([
    Input(shape=(IMG_SIZE, IMG_SIZE, 3)),
    Conv2D(32, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    
    Conv2D(64, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    
    Conv2D(128, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(4, activation='softmax')
])

# Compile model
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

logger.info("\n=== MODEL SUMMARY ===")
model.summary()

# ========================
# TRAINING WITH CALLBACKS
# ========================

# Early stopping: stop if validation loss doesn't improve for 5 epochs
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True,
    verbose=1
)

# Save best model
os.makedirs("models", exist_ok=True)

checkpoint = ModelCheckpoint(
    'models/best_model.h5',
    monitor='val_accuracy',
    save_best_only=True,
    verbose=1
)

logger.info("\nTraining model...")
history = model.fit(
    datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    callbacks=[early_stopping, checkpoint],
    class_weight=class_weight_dict,
    verbose=1
)

# ========================
# EVALUATION
# ========================

logger.info("\n=== EVALUATION ON TEST SET ===")
eval_results = model.evaluate(X_test, y_test, verbose=0)
loss = eval_results[0]
accuracy = eval_results[1]
precision_val = eval_results[2] if len(eval_results) > 2 else 0.0
recall_val = eval_results[3] if len(eval_results) > 3 else 0.0
logger.info(f"Test Loss: {loss:.4f}")
logger.info(f"Test Accuracy: {accuracy:.4f} ({100*accuracy:.2f}%)")
logger.info(f"Test Precision: {precision_val:.4f}")
logger.info(f"Test Recall: {recall_val:.4f}")

# Get predictions for detailed metrics
y_pred = model.predict(X_test, verbose=0).argmax(axis=1)

# Classification report
logger.info("\n=== CLASSIFICATION REPORT ===")
report = classification_report(y_test, y_pred, target_names=CATEGORIES)
logger.info(report)

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
logger.info("\n=== CONFUSION MATRIX ===")
logger.info(cm)

# ========================
# VISUALIZATIONS
# ========================

# 1. Training history
fig, axes = plt.subplots(1, 2, figsize=(14, 4))

axes[0].plot(history.history['accuracy'], label='Train Accuracy', linewidth=2)
axes[0].plot(history.history['val_accuracy'], label='Val Accuracy', linewidth=2)
axes[0].set_xlabel('Epoch', fontsize=12)
axes[0].set_ylabel('Accuracy', fontsize=12)
axes[0].set_title('Model Accuracy', fontsize=14, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3)

axes[1].plot(history.history['loss'], label='Train Loss', linewidth=2)
axes[1].plot(history.history['val_loss'], label='Val Loss', linewidth=2)
axes[1].set_xlabel('Epoch', fontsize=12)
axes[1].set_ylabel('Loss', fontsize=12)
axes[1].set_title('Model Loss', fontsize=14, fontweight='bold')
axes[1].legend(fontsize=10)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('models/training_history.png', dpi=300, bbox_inches='tight')
logger.info("✓ Saved: training_history.png")
plt.close()

# 2. Confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(
    cm, 
    annot=True, 
    fmt='d', 
    cmap='Blues',
    xticklabels=CATEGORIES,
    yticklabels=CATEGORIES,
    cbar_kws={'label': 'Count'}
)
plt.title('Confusion Matrix - Test Set', fontsize=14, fontweight='bold')
plt.ylabel('True Label', fontsize=12)
plt.xlabel('Predicted Label', fontsize=12)
plt.tight_layout()
plt.savefig('models/confusion_matrix.png', dpi=300, bbox_inches='tight')
logger.info("✓ Saved: confusion_matrix.png")
plt.close()

# ========================
# SAVE MODEL
# ========================

# Save final model
model.save("models/brain_tumor_model.h5")
logger.info("✓ Saved: brain_tumor_model.h5")

# Save model info
model_info = {
    "accuracy": float(accuracy),
    "loss": float(loss),
    "categories": CATEGORIES,
    "img_size": IMG_SIZE,
    "epochs_trained": len(history.history['loss'])
}

import json
with open("models/model_info.json", "w") as f:
    json.dump(model_info, f, indent=2)
logger.info("✓ Saved: model_info.json")



pd.DataFrame(history.history).to_csv(
    "models/training_history.csv",
    index=False
)

logger.info("✓ Saved: training_history.csv")
logger.info("\n✅ Training complete!")

