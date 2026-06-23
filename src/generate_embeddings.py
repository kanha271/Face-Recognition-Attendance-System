import os
import cv2
import joblib
import numpy as np
from tqdm import tqdm
from keras_facenet import FaceNet
# -----------------------------
DATASET_PATH = "../dataset"
OUTPUT_FILE = "../embeddings/embeddings.pkl"
# -----------------------------
embedder = FaceNet()
embeddings = []
labels = []
print("Generating Face Embeddings...\n")
students = os.listdir(DATASET_PATH)
for student in students:
    student_folder = os.path.join(
        DATASET_PATH,
        student
    )
    if not os.path.isdir(student_folder):
        continue
    images = os.listdir(student_folder)
    print(f"Processing {student}")
    for image_name in tqdm(images):
        image_path = os.path.join(
            student_folder,
            image_name
        )
        image = cv2.imread(image_path)
        if image is None:
            continue
        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )
        image = cv2.resize(
            image,
            (160,160)
        )
        image = np.expand_dims(
            image,
            axis=0
        )
        embedding = embedder.embeddings(
            image
        )[0]
        embeddings.append(
            embedding
        )
        labels.append(
            student
        )
os.makedirs(
    "../embeddings",
    exist_ok=True
)
joblib.dump(
    {
        "embeddings": np.array(
            embeddings
        ),
        "labels": np.array(
            labels
        )
    },
    OUTPUT_FILE
)
print("\nEmbeddings Saved Successfully.")
print(
    f"Total Samples: {len(embeddings)}"
)
