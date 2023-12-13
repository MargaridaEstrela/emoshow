#! /usr/bin/env python

from driver_camera import DriverCamera
from behaviour_look_around import BehaviourLookAround
import time
import cv2
import numpy as np
import requests

# Instantiate the camera driver and behavior
print("Starting driver camera")
# camera_driver = DriverCamera()
print("Starting look around")
look_around_behavior = BehaviourLookAround()

#list with all the emotions we will ask
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

#dictionary with all the emotions possible to the respective accuracy
accuracy_dict = {50: "/static/images/thinking.png", 80: "/static/images/normal.png", 95: "/static/images/love.png"}


look_around_behavior.pan.enable = True



def grabImage(url="http://localhost:8080/stream.mjpg"):

    # grab the image from the camera
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        # maens that it is a valid response
        stream = response.iter_content(chunk_size=1024)
        bytes_ = b''
        for chunk in stream:
            bytes_ += chunk
            a = bytes_.find(b'\xff\xd8')
            b = bytes_.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes_[a:b+2]
                bytes_ = bytes_[b+2:]
                frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                break

        return frame
    return None

def detect_faces(frame):
    """
    Detect faces in a given frame using OpenCV.
    """
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))


    #filter out faces smaller than x pixels by y pixels
    faces = list(filter(lambda face: face[2] > 300 and face[3] > 300, faces))
    
    return faces


def followFaces(faces, frame):
    """
    Simple function that given the recognized faces, it will pick the first
    """
    
    face = faces[-1]   # get the first face assuming that its one closest to hte left side
    x, y, w, h = face
    print("Following this face: ", face)

    angleInc = 20

    if x - 960 <  0: 
        # means that the face is on the left of the screen and need to turn right
        angle = look_around_behavior.pan.angle + angleInc if look_around_behavior.pan.angle + angleInc < 30 else 30
        look_around_behavior.pan.angle = angle
        print("going right: ", look_around_behavior.pan.angle)
    if x - 960 > 0:
        # means that the face is on the right of the screen and need to turn left
        angle = look_around_behavior.pan.angle - angleInc if look_around_behavior.pan.angle - angleInc > -30 else -30
        look_around_behavior.pan.angle = angle
        print("going left: ", look_around_behavior.pan.angle)





counter = 0

while True:
    
    frame = grabImage()
    faces = detect_faces(frame)

    if (len(faces) >= 1):
        followFaces(faces, frame)

        print(f"I have found {len(faces)} faces")

        # cut the faces out of the image and save it locally
        for i, (x, y, w, h) in enumerate(faces):
            face = frame[y:y+h, x:x+w]
            cv2.imwrite(f"{counter}_face_{i}.jpg", face)
            counter += 1

        # save the image with a rectangle on the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)
        cv2.imwrite(f"faces/{counter}_faces.jpg", frame)


    

    
    # faces = look_around_behavior.detect_faces()

    # if (faces and 1 != 1):
    #     frame = camera_driver.capture_frame()
    #     face_analysis = camera_driver.frame_analysis(frame)

    #     # see accuracy and return an emotion as feedback
    #     if (accuracy < 80):
    #         display = accuracy_dict[50]
    #     elif (accuracy < 95):
    #         display = accuracy_dict[80]
    #     else:
    #         display = accuracy_dict[95]


    # look_around_behavior.pan.angle = -look_around_behavior.pan.angle
    print("Change player\n")

