#! /usr/bin/env python

# from driver_camera import DriverCamera
from behaviour_look_around import BehaviourLookAround
import time
import cv2
import numpy as np
import requests
import socket

import middleware as mw
import os

myPan = mw.Pan()
myTilt = mw.Tilt()
myOnboard = mw.Onboard()

myPan.enable = True
myTilt.enable = True

print(os.getcwd())
print("chaging image")
myOnboard.image = "images/simon_images/angry.png"
print("image was changed")

#list with all the emotions we will ask
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

#dictionary with all the emotions possible to the respective accuracy
accuracy_dict = {50: "/static/images/thinking.png", 80: "/static/images/normal.png", 95: "/static/images/love.png"}



def parseMessage(message):

    mw.Pan.enable = True
    mw.Tilt.enable = True
    splitMessage = message.split("::")

    if len(splitMessage) != 2:
        print("Invalid message")

    command = splitMessage[0]
    value = splitMessage[1]

    if (command == "pan"):
       print("setting pan")
       myPan.angle = int(value)
    elif (command == "tilt"):
        print("setting tilt")
        myTilt.angle = int(value)
    elif (command == "image"):
        print("setting this image: ", value)
        myOnboard.image = value        
        print("setting image")
    elif (command == "getImage"):
        # returns the path to the images
        # get a list of all the images in the folder
        images = [os.path.join("images/simon_images", x) for x in os.listdir("static/images/simon_images")]
        return images


print("Starting things")
host = '192.168.0.102' #Server ip
port = 4000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))



print("Server Started")
while True:
    data, addr = s.recvfrom(1024)
    data = data.decode('utf-8')
    print("Message from: " + str(addr))
    print("From connected user: " + data)

    returnMsg = parseMessage(data)

    print("Sending: " + data)
    s.sendto(str(returnMsg).encode('utf-8'), addr)
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