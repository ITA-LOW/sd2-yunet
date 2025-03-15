import cv2 as cv
import RPi.GPIO as GPIO
import time

# Configuração dos servos
GPIO.setmode(GPIO.BCM)
SERVO_X_PIN = 17  # Defina o pino GPIO para o servo de movimento horizontal
SERVO_Y_PIN = 27  # Defina o pino GPIO para o servo de movimento vertical
GPIO.setup(SERVO_X_PIN, GPIO.OUT)
GPIO.setup(SERVO_Y_PIN, GPIO.OUT)

# Configuração do PWM para os servos
servo_x = GPIO.PWM(SERVO_X_PIN, 50)  # 50 Hz
servo_y = GPIO.PWM(SERVO_Y_PIN, 50)
servo_x.start(7.5)  # Posição neutra
servo_y.start(7.5)

def set_servo_angle(servo, angle):
    duty = (angle / 18) + 2.5
    servo.ChangeDutyCycle(duty)
    time.sleep(0.2)

model = 'face_detection_yunet_2023mar.onnx'
input_size = (640, 640)

face_detector = cv.FaceDetectorYN.create(
    model, "", input_size, score_threshold=0.8, nms_threshold=0.3,
    top_k=5000, backend_id=cv.dnn.DNN_BACKEND_OPENCV, target_id=cv.dnn.DNN_TARGET_CPU
)

ip = 'http://192.168.0.126'
stream_url = f"{ip}:81/stream"

video_path = "sora.mp4"
cap = cv.VideoCapture(stream_url)

def get_position(row, col):
    switch = {
        (1, 1): "position(top_left)",
        (1, 2): "position(top_center)",
        (1, 3): "position(top_right)",
        (2, 1): "position(middle_left)",
        (2, 2): "position(middle_center)",
        (2, 3): "position(middle_right)",
        (3, 1): "position(bottom_left)",
        (3, 2): "position(bottom_center)",
        (3, 3): "position(bottom_right)"
    }
    return switch.get((row, col), "position(unknown)")

position_to_angle = {
    "position(top_left)": (45, 45),
    "position(top_center)": (90, 45),
    "position(top_right)": (135, 45),
    "position(middle_left)": (45, 90),
    "position(middle_center)": (90, 90),
    "position(middle_right)": (135, 90),
    "position(bottom_left)": (45, 135),
    "position(bottom_center)": (90, 135),
    "position(bottom_right)": (135, 135),
}

if not cap.isOpened():
    print(f"Erro ao abrir o vídeo {video_path}")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        height, width = frame.shape[:2]
        resized_frame = cv.resize(frame, input_size)
        faces = face_detector.detect(resized_frame)

        if faces[1] is not None:
            cell_width = width / 3
            cell_height = height / 3

            for face in faces[1]:
                face = face.astype(int)
                x, y, w, h = face[:4]
                x = int(x * width / input_size[0])
                y = int(y * height / input_size[1])
                w = int(w * width / input_size[0])
                h = int(h * height / input_size[1])

                face_center_x = x + w / 2
                face_center_y = y + h / 2
                col = int(face_center_x // cell_width) + 1
                row = int(face_center_y // cell_height) + 1
                col = min(col, 3)
                row = min(row, 3)

                position = get_position(row, col)
                print(f"Rosto localizado na célula da matriz: {position}")

                if position in position_to_angle:
                    angle_x, angle_y = position_to_angle[position]
                    set_servo_angle(servo_x, angle_x)
                    set_servo_angle(servo_y, angle_y)

    cap.release()
    servo_x.stop()
    servo_y.stop()
    GPIO.cleanup()
