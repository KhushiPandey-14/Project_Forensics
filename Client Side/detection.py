from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import cv2
from ultralytics import YOLO
import numpy as np
import time
import os
import requests

# Handles the YOLOv8 detection algorithm, saves detected frames and sends alert to the server-side application
class Detection(QThread):

    def __init__(self, token, location, receiver):
        super(Detection, self).__init__()
        self.token = token
        self.location = location
        self.receiver = receiver

    changePixmap = pyqtSignal(QImage)

    # Runs the detection model, evaluates detections and draws boxes around detected objects
    def run(self):

        # Load YOLOv8 model
        model = YOLO("weights/best.pt")  # Replace with the path to your YOLOv8 model file
        
        self.running = True
        self.starting_time = time.time()  # Initialize starting_time
        # Starts camera
        cap = cv2.VideoCapture(0)

        # Detection while loop
        while self.running:
            ret, frame = cap.read()
            if ret:
                # Perform YOLOv8 inference
                results = model(frame)  # Run inference directly on the frame
                annotated_frame = results[0].plot()  # Annotate the frame with bounding boxes, labels, etc.

                # Filter detections based on confidence > 70% and matching classes
                detections = results[0].boxes  # Access the boxes
                for box in detections:
                    confidence = box.conf[0]  # Get confidence score for each detection
                    class_id = int(box.cls[0])  # Get the class ID for each detection

                    # Define the class IDs your model was trained on (e.g., 0, 1, 2, 3)
                    # Update this with your specific class IDs based on the model's training
                    target_classes = [0, 1, 2, 3]  # Example class IDs, change according to your classes

                    #if confidence > 0.7 and class_id in target_classes:
                        # Save detected frame if it meets the criteria
                    if class_id in target_classes:
                        self.save_detection(annotated_frame)

                # Showing final result
                height, width, channels = annotated_frame.shape
                rgbImage = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                bytesPerLine = channels * width
                convertToQtFormat = QImage(rgbImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

    # Saves detected frame as a .jpg within the saved_alert folder
    '''def save_detection(self, frame):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"detected_frame_{timestamp}.jpg"
        cv2.imwrite(f'./saved_alert/{filename}', frame)  # Save in 'saved_alert' folder
        print('Frame Saved')
        '''
 
    # Saves detected frame as a .jpg within the saved_frame folder
    def save_detection(self, frame):
        # Ensure the folder exists
        folder_path = './saved_frame/'
        os.makedirs(folder_path, exist_ok=True)

        # Save the frame
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{folder_path}detected_frame_{timestamp}.jpg"
        success = cv2.imwrite(filename, frame)
        if success:
            print(f"Frame Saved: {filename}")
            self.post_detection(filename)
        else:
            print("Failed to save frame!")

        #self.post_detection()

    # Sends alert to the server
    '''
    def post_detection(self):
        try:
            #url = 'https://domjur-weapon-detection.herokuapp.com/api/images/'
            url = 'http://127.0.0.1:8000/api/images/'
            headers = {'Authorization': 'Token ' + self.token}
            files = {'image': open('saved_frame/frame.jpg', 'rb')}
            data = {'user_ID': self.token, 'location': self.location, 'alert_receiver': self.receiver}
            response = requests.post(url, files=files, headers=headers, data=data)

            # HTTP 200
            if response.ok:
                print('Alert was sent to the server')
            # Bad response
            else:
                print('Unable to send alert to the server')

        except:
            print('Unable to access server')
'''

    def post_detection(self, filename):
        try:
            with open(filename, 'rb') as image_file:
                files = {'image': image_file}
                data = {'user_ID': self.token, 'location': self.location, 'alert_receiver': self.receiver}
                headers = {'Authorization': 'Token ' + self.token}
                url = 'http://127.0.0.1:8000/api/images/'  # Update with your server URL

                # Send the POST request
                response = requests.post(url, files=files, headers=headers, data=data)

                if response.ok:
                    print('Alert was sent to the server')
                else:
                    print(f'Failed to send alert to server. HTTP Status Code: {response.status_code}')

        except Exception as e:
            print(f'Unable to access server: {e}')
