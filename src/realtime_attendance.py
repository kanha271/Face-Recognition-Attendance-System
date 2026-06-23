import cv2
import joblib
import numpy as np
import tensorflow as tf
import mediapipe as mp
import time
from datetime import datetime
from keras_facenet import FaceNet

from attendance_manager import AttendanceManager
from database_manager import DatabaseManager

# =====================================================
# CONFIG
# =====================================================
cv2.setUseOptimized(True)
cv2.setNumThreads(8)
MODEL_PATH = "../models/classifier.h5"
LABEL_ENCODER_PATH = "../models/label_encoder.pkl"

CONFIDENCE_THRESHOLD = 0.80

FRAME_SKIP = 10

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# =====================================================
# LOAD MODELS
# =====================================================

print("Loading TensorFlow classifier...")

classifier = tf.keras.models.load_model(
    MODEL_PATH,
    compile=False
)

encoder = joblib.load(
    LABEL_ENCODER_PATH
)

print("Loading FaceNet...")

facenet = FaceNet()

print("Loading MediaPipe Face Detector...")

mp_face_detection = mp.solutions.face_detection

face_detector = mp_face_detection.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.6
)

print("Models Loaded Successfully")

# =====================================================
# ATTENDANCE + DATABASE
# =====================================================

attendance = AttendanceManager()

db = DatabaseManager()

for student in encoder.classes_:
    db.add_student(student)

# =====================================================
# CAMERA
# =====================================================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# =====================================================
# FPS
# =====================================================

fps = 0
fps_counter = 0
fps_start = time.time()

# =====================================================
# CACHE
# =====================================================

frame_count = 0
recognized_faces = []

# =====================================================
# MAIN LOOP
# =====================================================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    fps_counter += 1

    if fps_counter >= 30:

        fps = 30 / (
            time.time() - fps_start
        )

        fps_counter = 0
        fps_start = time.time()

    frame_count += 1

    # ----------------------------------------
    # RUN DETECTION EVERY N FRAMES
    # ----------------------------------------

    if frame_count % FRAME_SKIP == 0:

        recognized_faces = []

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = face_detector.process(rgb)

        if results.detections:

            h, w, _ = frame.shape

            for detection in results.detections:

                bbox = detection.location_data.relative_bounding_box

                x1 = int(bbox.xmin * w)
                y1 = int(bbox.ymin * h)

                bw = int(bbox.width * w)
                bh = int(bbox.height * h)

                x2 = x1 + bw
                y2 = y1 + bh

                x1 = max(0, x1)
                y1 = max(0, y1)

                x2 = min(w, x2)
                y2 = min(h, y2)

                face_crop = frame[
                    y1:y2,
                    x1:x2
                ]

                if face_crop.size == 0:
                    continue

                try:

                    face_rgb = cv2.cvtColor(
                        face_crop,
                        cv2.COLOR_BGR2RGB
                    )

                    face_rgb = cv2.resize(
                        face_rgb,
                        (160, 160),
                        interpolation=cv2.INTER_AREA
                    )

                    embedding = facenet.embeddings(
                        np.expand_dims(
                            face_rgb,
                            axis=0
                        )
                    )[0]

                    prediction = classifier.predict(
                        np.expand_dims(
                            embedding,
                            axis=0
                        ),
                        verbose=0
                    )[0]

                    confidence = float(
                        np.max(prediction)
                    )

                    class_id = np.argmax(
                        prediction
                    )

                    if confidence >= CONFIDENCE_THRESHOLD:

                        name = encoder.inverse_transform(
                            [class_id]
                        )[0]

                        attendance.student_seen(
                            name
                        )

                    else:

                        name = "Unknown"

                    recognized_faces.append({

                        "name": name,

                        "confidence": confidence,

                        "bbox": (
                            x1,
                            y1,
                            x2,
                            y2
                        )

                    })

                except Exception as e:

                    print(
                        "Face Processing Error:",
                        e
                    )

    # ----------------------------------------
    # EXIT HANDLING
    # ----------------------------------------

    exited_students = attendance.update()

    for student in exited_students:

        db.save_session(

            student_name=
                student["name"],

            entry_time=
                student["entry_time"].strftime(
                    "%H:%M:%S"
                ),

            exit_time=
                student["exit_time"].strftime(
                    "%H:%M:%S"
                ),

            duration_seconds=
                student["duration"]

        )
        

    # ----------------------------------------
    # DRAW
    # ----------------------------------------

    for face in recognized_faces:

        x1, y1, x2, y2 = face["bbox"]

        name = face["name"]

        confidence = face["confidence"]

        if name == "Unknown":

            color = (0, 0, 255)

        else:

            color = (0, 255, 0)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        cv2.putText(
            frame,
            name,
            (x1, y1 - 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

        cv2.putText(
            frame,
            f"{confidence*100:.1f}%",
            (x1, y1 - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

        if name != "Unknown":
            arrival = attendance.get_entry_time(
                name
            )
            duration = attendance.get_duration_string(
                name
            )
            cv2.putText(
                frame,
                f"In: {arrival}",
                (x1, y1 - 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )
            cv2.putText(
                frame,
                duration,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

    # ----------------------------------------
    # STATUS
    # ----------------------------------------

    active = len(
        attendance.get_active_students()
    )

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Active Students: {active}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )
    now = datetime.now()

    cv2.putText(
        frame,
        now.strftime("%d-%m-%Y %H:%M:%S"),
        (10, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Press esc to Quit",
        (10, 150),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )
    cv2.imshow(
        "Face Attendance System",
        frame
    )

    key = cv2.waitKey(1)

    if key == 27:
        break

# =====================================================
# CLEANUP
# =====================================================

cap.release()

cv2.destroyAllWindows()

db.close()

print("Application Closed")