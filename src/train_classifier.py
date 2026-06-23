import os
import joblib
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

import tensorflow as tf

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Dense,
    Dropout,
    BatchNormalization
)

from tensorflow.keras.callbacks import (
    EarlyStopping,
    ReduceLROnPlateau
)

# --------------------------------------------------

EMBEDDINGS_FILE = "../embeddings/embeddings.pkl"

MODEL_PATH = "../models/classifier.h5"

LABEL_ENCODER_PATH = "../models/label_encoder.pkl"

# --------------------------------------------------

print("Loading embeddings...")

data = joblib.load(EMBEDDINGS_FILE)

X = data["embeddings"]
y = data["labels"]

print(f"Embeddings Shape : {X.shape}")
print(f"Labels Shape     : {y.shape}")

embedding_dim = X.shape[1]

print(f"Embedding Dimension : {embedding_dim}")

# --------------------------------------------------
# Encode Labels
# --------------------------------------------------

encoder = LabelEncoder()

y_encoded = encoder.fit_transform(y)

joblib.dump(
    encoder,
    LABEL_ENCODER_PATH
)

num_classes = len(encoder.classes_)

print(f"Classes Found : {num_classes}")
print("Students      :", encoder.classes_)

# Save original labels for stratify

y_labels = y_encoded.copy()

# One-hot encoding

y_encoded = tf.keras.utils.to_categorical(
    y_encoded,
    num_classes=num_classes
)

# --------------------------------------------------
# Train/Test Split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_labels
)

print("\nTraining Samples :", len(X_train))
print("Testing Samples  :", len(X_test))

# --------------------------------------------------
# Build Model
# --------------------------------------------------

model = Sequential([

    Dense(
        128,
        activation='relu',
        input_shape=(embedding_dim,)
    ),

    BatchNormalization(),

    Dropout(0.3),

    Dense(
        64,
        activation='relu'
    ),

    Dropout(0.3),

    Dense(
        num_classes,
        activation='softmax'
    )

])

# --------------------------------------------------
# Compile
# --------------------------------------------------

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# --------------------------------------------------
# Callbacks
# --------------------------------------------------

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=5,
    verbose=1
)

# --------------------------------------------------
# Train
# --------------------------------------------------

history = model.fit(

    X_train,
    y_train,

    validation_data=(
        X_test,
        y_test
    ),

    epochs=50,

    batch_size=8,

    callbacks=[
        early_stopping,
        reduce_lr
    ],

    verbose=1
)

# --------------------------------------------------
# Evaluate
# --------------------------------------------------

loss, accuracy = model.evaluate(
    X_test,
    y_test,
    verbose=0
)

print(
    f"\nTest Accuracy: {accuracy * 100:.2f}%"
)

# --------------------------------------------------
# Save Model
# --------------------------------------------------

os.makedirs(
    "../models",
    exist_ok=True
)

model.save(MODEL_PATH)

print("\nModel Saved Successfully")

# --------------------------------------------------
# Reports Folder
# --------------------------------------------------

os.makedirs(
    "../reports",
    exist_ok=True
)

# --------------------------------------------------
# Accuracy Plot
# --------------------------------------------------

plt.figure(figsize=(10, 5))

plt.plot(
    history.history['accuracy'],
    label='Train Accuracy'
)

plt.plot(
    history.history['val_accuracy'],
    label='Validation Accuracy'
)

plt.title("Model Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()

plt.savefig(
    "../reports/accuracy.png"
)

plt.close()

# --------------------------------------------------
# Loss Plot
# --------------------------------------------------

plt.figure(figsize=(10, 5))

plt.plot(
    history.history['loss'],
    label='Train Loss'
)

plt.plot(
    history.history['val_loss'],
    label='Validation Loss'
)

plt.title("Model Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()

plt.savefig(
    "../reports/loss.png"
)

plt.close()

print("\nAccuracy graph saved.")
print("Loss graph saved.")