#! /usr/bin/env python

# from driver_camera import DriverCamera
from behaviour_look_around import BehaviourLookAround
import time
import cv2
import numpy as np
import requests
import socket

import middleware as mw

HOST = "192.168.0.114"
PORT = 1234

# Instantiate the camera driver and behavior
print("Starting driver camera")
# camera_driver = DriverCamera()
print("Starting look around")
look_around_behavior = BehaviourLookAround()

#list with all the emotions we will ask
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

#dictionary with all the emotions possible to the respective accuracy
accuracy_dict = {50: "/static/images/thinking.png", 80: "/static/images/normal.png", 95: "/static/images/love.png"}

look_around_behavior.enabled = True
look_around_behavior.pan.enable = True
look_around_behavior.tilt.enable = True

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


def parseMessage(message):

    mw.Pan.enable = True
    mw.Tilt.enable = True
    splitMessage = message.split("::")

    if len(splitMessage) != 2:
        print("Invalid message")

    command = splitMessage[0]
    value = splitMessage[1]

    if (command == "pan"):
       print("setting pan: ", mw.Pan.angle)
       mw.Pan.angle = value
       print("setting pan: ", mw.Pan.angle)
    elif (command == "tilt"):
        print("setting tilt")
        mw.Tilt.angle = value
    elif (command == "image"):
        print("setting image")


print("Starting things")
host = '192.168.0.103' #Server ip
port = 4000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))


print("Before: ", look_around_behavior.pan.angle)

print("Server Started")
while True:
    data, addr = s.recvfrom(1024)
    data = data.decode('utf-8')
    print("Message from: " + str(addr))
    print("From connected user: " + data)

    parseMessage(data)

    data = data.upper()
    print("Sending: " + data)
    s.sendto(data.encode('utf-8'), addr)
c.close()


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

