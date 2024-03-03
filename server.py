from flask import Flask, render_template, Response
import cv2
import threading
from queue import Queue
from utils import *
import mediapipe as mp
from body_part_angle import BodyPartAngle
from types_of_exercise import TypeOfExercise

app = Flask(__name__)

cap = cv2.VideoCapture(0)
cap.set(3, 800)  # width
cap.set(4, 480)  # height

video_queue = Queue()

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

counter = 0
status = True
selected_exercise = "pull-up"  # Default exercise type

def generate_frames():
    global counter, status
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame.flags.writeable = False

        # Make detection
        results = pose.process(frame)

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark
            counter, status = TypeOfExercise(landmarks).calculate_exercise(selected_exercise, counter, status)
        except:
            pass

        frame = score_table(selected_exercise, frame, counter, status)

        # render detections (for landmarks)
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(174, 139, 45), thickness=2, circle_radius=2),
        )

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        video_queue.put(frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    threading.Thread(target=generate_frames).start()

    @app.route('/')
    def index():
        return render_template('index.html')

    def generate():
        while True:
            frame = video_queue.get()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    @app.route('/video')
    def video():
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    app.run(debug=True)
