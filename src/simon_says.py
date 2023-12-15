#! /usr/bin/env python

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
mySpeakers = mw.Speakers()
myLeds = mw.Leds()

myPan.enable = True
myTilt.enable = True

print(os.getcwd())
print("chaging image")
myOnboard.image = "images/simon_images/angry.png"
print("image was changed")

image_path = "images/simon_images/"
sound_path = "sounds/simon_sounds/"
icon_path = "icons/simon_icons/"


def parseMessage(message):

    mw.Pan.enable = True
    mw.Tilt.enable = True
    splitMessage = message.split("::")

    if len(splitMessage) != 2:
        print("Invalid message")

    command = splitMessage[0]
    value = splitMessage[1]

    if command == "pan":
       print("[PAN] setting...")
       myPan.angle = int(value)
       print("[PAN] value: ", value)

    elif command == "tilt":
        print("[TILT] setting...")
        myTilt.angle = int(value)
        print("[TILT] value: ", value)

    elif command == "image":
        print("[IMAGE] setting...")
        image_src = os.path.join(image_path, f"{value}.png")
        myOnboard.image = image_src      
        print("[IMAGE] src: ", image_src)

    elif command == "getImage":
        print("Getting all images...")
        # returns the path to the images
        # get a list of all the images in the folder
        images = [os.path.join("images/simon_images", x) for x in os.listdir("static/images/simon_images")]
        return images

    elif command == "sound":
        print("[SOUND] setting...")
        sound_src = os.path.join(sound_path, f"{value}")
        mySpeakers.url = sound_src    
        print("[SOUND] src: ", sound_src)

    elif command == "icon":
        print("[ICON] setting...")
        icon_src = os.path.join(icon_path, f"{value}.png")
        myLeds.load_from_url(icon_src)    
        print("[ICON] src: ", icon_src) 

    elif command == "game":
        if value == "on":
            print("[GAME] starting...")
        elif value == "off":
            print("[GAME] ending...")
            s.close()
            exit()
        

if __name__=='__main__':

    print("Starting connection...")
    elmo_ip = '192.168.0.102' #Server ip
    port = 4000

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((elmo_ip, port))


    print("Server Started")
    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        print("Message from: " + str(addr))
        print("From connected user: " + data)

        returnMsg = parseMessage(data)

        print("Sending: " + data)
        s.sendto(str(returnMsg).encode('utf-8'), addr)
