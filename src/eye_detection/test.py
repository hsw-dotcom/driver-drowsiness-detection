import cv2
import dlib
from functools import wraps
from scipy.spatial import distance
from numpy import mean
from picamera2 import Picamera2, Preview

# 카메라 셋팅
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

# dlib 인식 모델 정의
hog_face_detector = dlib.get_frontal_face_detector()
dlib_facelandmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


# 눈 거리 계산
def calculate_EAR(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear_aspect_ratio = (A + B) / (2.0 * C)
    return ear_aspect_ratio


def get_EAR(face_landmarks, frame):
    leftEye = []
    rightEye = []

    for n in range(36, 42):  # 오른쪽 눈 감지
        x = face_landmarks.part(n).x
        y = face_landmarks.part(n).y
        leftEye.append((x, y))
        next_point = n + 1
        if n == 41:
            next_point = 36
        x2 = face_landmarks.part(next_point).x
        y2 = face_landmarks.part(next_point).y
        cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

    for n in range(42, 48):  # 왼쪽 눈 감지
        x = face_landmarks.part(n).x
        y = face_landmarks.part(n).y
        rightEye.append((x, y))
        next_point = n + 1
        if n == 47:
            next_point = 42
        x2 = face_landmarks.part(next_point).x
        y2 = face_landmarks.part(next_point).y
        cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

    left_ear = calculate_EAR(leftEye)
    right_ear = calculate_EAR(rightEye)

    EAR = (left_ear + right_ear) / 2
    EAR = round(EAR, 3)

    return EAR, rightEye, leftEye

def main():
    avg_eye_data = []
    avg_EAR_data = []
    avg_count = 1
    avg_EAR = 0
    avg_eye_level = 0
    closed_count = 0
    start_detection = False

    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = hog_face_detector(gray)

        for face in faces:
            face_landmarks = dlib_facelandmark(gray, face)
            EAR, right_eye, left_eye = get_EAR(face_landmarks, frame)

            eye_level = int((right_eye[0][1] + left_eye[3][1]) / 2)
            x_pos1 = left_eye[0][0]
            x_pos2 = right_eye[3][0]

            # 600프레임 => 50~60초
            if avg_count < 300:
                avg_eye_data.append(eye_level)
                avg_EAR_data.append(EAR)
                avg_eye_level = mean(avg_eye_data)
                avg_EAR = mean(avg_EAR_data)
                avg_count += 1
                cv2.putText(frame, str(avg_count), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                start_detection = True
                cv2.putText(frame, "start", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.putText(frame, "EAR: " + str(EAR) + "/ avg_EAR:" + str(round(avg_EAR, 3)), (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, "eye_level: " + str(eye_level) + "/ avg_eye_level:" + str(round(avg_eye_level, 3)), (20, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            # cv2.putText(frame, "Counter:" + str(closed_count), (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.line(frame,(x_pos1,eye_level), (x_pos2,eye_level), (0, 255, 0), 1)
            cv2.line(frame,(x_pos1,int(avg_eye_level)), (x_pos2,int(avg_eye_level)), (0, 0, 255), 1)

            if start_detection:
                if EAR < avg_EAR * 0.8:
                    closed_count += 1
                    cv2.putText(frame, "count: " + str(closed_count), (20, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else: closed_count = 0

                # 졸음 운전중
                if (closed_count >= 10) or (eye_level - avg_eye_level > 20):
                    cv2.putText(frame, "detected", (20, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


        cv2.imshow("Camera", frame)

        key = cv2.waitKey(30)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
