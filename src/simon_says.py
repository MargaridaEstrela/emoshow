#! /usr/bin/env python

from driver_camera import DriverCamera
from behaviour_look_around import BehaviourLookAround
import time

# Instantiate the camera driver and behavior
camera_driver = DriverCamera()
look_around_behavior = BehaviourLookAround()

#list with all the emotions we will ask
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

#dictionary with all the emotions possible to the respective accuracy
accuracy_dict = {50: "/static/images/thinking.png", 80: "/static/images/normal.png", 95: "/static/images/love.png"}

while True:
    faces = look_around_behavior.detect_faces()

    if (faces):
        frame = camera_driver.capture_frame()
        face_analysis = camera_driver.frame_analysis(frame)

        # see accuracy and return an emotion as feedback
        if (accuracy < 80)
            display = accuracy_dict[50];
        else if (accuracy < 95)
            display = accuracy_dict[80]; 
        else:
            display = accuracy_dict[95];

    look_around_behavior.pan = -look_around_behavior.pan
    print("Change player\n")

    time.sleep(1)    