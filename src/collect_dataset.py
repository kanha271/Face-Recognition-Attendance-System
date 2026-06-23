import cv2
import os
import numpy as np
from mtcnn import MTCNN

# ---------- CONFIG ----------

DATASET_DIR = "../dataset"
TARGET_IMAGES = 200

# ----------------------------

detector = MTCNN()

student_name = input("Enter Student Name: ").strip()

student_folder = os.path.join(DATASET_DIR, student_name)

os.makedirs(student_folder, exist_ok=True)

cap = cv2.VideoCapture(0)

count = len(os.listdir(student_folder))

print(f"\nCollecting images for: {student_name}")
print("Press Q to stop.\n")

def is_blurry(image, threshold=100):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return score < threshold

while True:

    ret, frame = cap.read()

    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    faces = detector.detect_faces(rgb)

    for face in faces:

        x, y, w, h = face['box']

        x = max(0, x)
        y = max(0, y)

        face_crop = frame[y:y+h, x:x+w]

        if face_crop.size == 0:
            continue

        if is_blurry(face_crop):
            continue

        count += 1

        face_crop = cv2.resize(face_crop, (160, 160))

        filename = os.path.join(
            student_folder,
            f"{count}.jpg"
        )

        cv2.imwrite(filename, face_crop)

        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Saved: {count}",
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,255,0),
            2
        )

        if count >= TARGET_IMAGES:
            break

    cv2.imshow("Dataset Collection", frame)

    key = cv2.waitKey(1)

    if key == ord('q'):
        break

    if count >= TARGET_IMAGES:
        break

cap.release()
cv2.destroyAllWindows()

print(f"\nDataset Collection Complete.")
print(f"Total Images: {count}")