import cv2
import dlib
import numpy as np
from imutils import face_utils

# EAR -> Eye Aspect ratio
def ear(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def yawn(mouth):
    A = np.linalg.norm(mouth[13] - mouth[19])
    B = np.linalg.norm(mouth[14] - mouth[18])
    C = np.linalg.norm(mouth[15] - mouth[17])
    avg = (A + B + C) / 3.0
    D = np.linalg.norm(mouth[12] - mouth[16])
    mar = avg / D
    return mar

def get_driver_distance(face, frame):
    face_width_px = np.linalg.norm(face[0] - face[1]) 
    known_width = 14.0 
    fov = 60.0 
    image_width_px = frame.shape[1] 
    distance = (known_width * image_width_px) / (2 * face_width_px * np.tan(fov/2))
    return distance

capture = cv2.VideoCapture('far.mp4') # Provide path to your video file
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

(leStart, leEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(reStart, reEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

EAR_THRESHOLD = 0.2
EAR_CONSEC_FRAMES = 48
MAR_THRESHOLD = 0.5
COUNTER_THRESHOLD = 3
NEAR_DISTANCE_THRESHOLD = -32.0
counter = 0

while True:
    ret, frame = capture.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    for rect in rects:
        shape = face_utils.shape_to_np(predictor(gray, rect))
        leftEye = shape[leStart:leEnd]
        rightEye = shape[reStart:reEnd]
        mouth = shape[mStart:mEnd]
        leftEAR = ear(leftEye)
        rightEAR = ear(rightEye)
        mar = yawn(mouth)
        avgEAR = (leftEAR + rightEAR) / 2.0

        if avgEAR < EAR_THRESHOLD:
            counter += 1
        else:
            if counter >= EAR_CONSEC_FRAMES:
                cv2.putText(frame, "Drowsy", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            elif counter >= COUNTER_THRESHOLD:
                cv2.putText(frame, "Alert", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            counter = 0

        if mar > MAR_THRESHOLD:
            cv2.putText(frame, "Yawn Detected", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        driver_distance = get_driver_distance(shape, frame)
        distance_status = "Near" if driver_distance >  NEAR_DISTANCE_THRESHOLD else "Far"
        if driver_distance > NEAR_DISTANCE_THRESHOLD:
            print("near")
        else:
            print("far")
        cv2.putText(frame, f"Distance: {distance_status}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        print(driver_distance)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) == 27:
        break

capture.release()
cv2.destroyAllWindows()
