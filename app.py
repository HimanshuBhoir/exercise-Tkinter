import tkinter as tk
from PIL import Image, ImageTk
import threading
import cv2
import argparse
from utils import *
import mediapipe as mp
from body_part_angle import BodyPartAngle
from types_of_exercise import TypeOfExercise
from queue import Queue

class ExerciseApp:
    def __init__(self, root, cap):
        self.root = root
        self.root.title("Exercise App")
        self.cap = cap
        self.queue = Queue()

        self.create_widgets()

        # Mediapipe setup
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

        self.counter = 0
        self.status = True
        self.selected_exercise = "pull-up"  # Default exercise type

        # Thread to run the exercise in the background
        self.exercise_thread = threading.Thread(target=self.run_exercise)
        self.exercise_thread.daemon = True  # Close the thread when the main application is closed
        self.exercise_thread.start()

        # Update frames in the main Tkinter thread
        self.root.after(10, self.update_frames)

    def create_widgets(self):
        exercise_label = tk.Label(self.root, text="Select Exercise Type:")
        exercise_label.pack(pady=10)

        pull_up_button = tk.Button(self.root, text="Pull-Up", command=lambda: self.start_exercise("pull-up"))
        pull_up_button.pack(side=tk.LEFT, padx=10)

        push_up_button = tk.Button(self.root, text="Push-Up", command=lambda: self.start_exercise("push-up"))
        push_up_button.pack(side=tk.LEFT, padx=10)

        sit_up_button = tk.Button(self.root, text="Sit-Up", command=lambda: self.start_exercise("sit-up"))
        sit_up_button.pack(side=tk.LEFT, padx=10)

        walking_button = tk.Button(self.root, text="Walking", command=lambda: self.start_exercise("walking"))
        walking_button.pack(side=tk.LEFT, padx=10)

        squat_button = tk.Button(self.root, text="Squat", command=lambda: self.start_exercise("squat"))
        squat_button.pack(side=tk.LEFT, padx=10)

        self.video_label = tk.Label(self.root)
        self.video_label.pack()

    def run_exercise(self):
        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while self.cap.isOpened():
                ret, frame = self.cap.read()

                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame.flags.writeable = False

                    # Make detection
                    results = pose.process(frame)

                    frame.flags.writeable = True
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    try:
                        landmarks = results.pose_landmarks.landmark
                        self.counter, self.status = TypeOfExercise(landmarks).calculate_exercise(
                            self.selected_exercise, self.counter, self.status)
                    except:
                        pass

                    frame = score_table(self.selected_exercise, frame, self.counter, self.status)

                    # render detections (for landmarks)
                    self.mp_drawing.draw_landmarks(
                        frame,
                        results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
                        self.mp_drawing.DrawingSpec(color=(174, 139, 45), thickness=2, circle_radius=2),
                    )

                    self.queue.put(frame)  # Put frame in the queue

                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        break

            self.cap.release()
            cv2.destroyAllWindows()

    def update_frames(self):
        while not self.queue.empty():
            frame = self.queue.get()
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = ImageTk.PhotoImage(img)
            self.video_label.img = img
            self.video_label.config(image=img)
        self.root.after(10, self.update_frames)  # Update every 10 milliseconds

    def start_exercise(self, exercise_type):
        self.selected_exercise = exercise_type
        self.counter = 0  # Reset counter to zero

if __name__ == "__main__":
    root = tk.Tk()
    cap = cv2.VideoCapture(0)
    cap.set(3, 800)  # width
    cap.set(4, 480)  # height
    app = ExerciseApp(root, cap)
    root.mainloop()
    cap.release()
