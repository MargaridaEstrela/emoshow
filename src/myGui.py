import PySimpleGUI as sg
from server import ElmoServer
import random
import numpy as np
import cv2
import math
import sys
import time

# list of emotions for facial expression analysis
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

# variables to control the game
play = 1  # play number in the game (incremented with each play)
player = 1  # current player
points = {"1": 0, "2": 0}  # points of each player (initially set to 0)

# when the respective buttons are clicked, one of the faces in the list will be played at random
bad_face = ["cry", "confused", "anger"]  # the list of faces containing the necessary sounds for the bad button
good_face = ["normal", "rolling_eyes", "thinking"]  # the list of faces containing the necessary faces for the good button
awesome_face = ["love", "images/simon_images/stars.gif", "blush"]  # the list of faces containing the necessary faces for the awesome button

# default angles
default_pan = 0
default_tilt = 0

# when the respective buttons are clicked, one of the sounds in the list will be played accordingly with the random face shown
feedback_sounds = {"cry": "lagrimas.wav", 
                   "confused": "question.wav", 
                   "anger": "virgulas.wav", 
                   "normal": "normal.wav", 
                   "rolling_eyes": "olharCima.wav", 
                   "thinking": "normal.wav", 
                   "love": "coracoes.wav", 
                   "images/simon_images/stars.gif": "estrelas.wav", 
                   "blush": "smillingEyes.wav"}

# start with debug mode to run as fake
debug_mode = "--debug" in sys.argv

# setting up IP addresses for communication with Elmo
elmoIp = input("ElmoIP: ")  # get elmoIp from command line (if --debug, press enter)
elmoPort = input("Port: ")  # get elmoPort from command line (if --debug, press enter)
clientIp = input("ClientIp: ")  # get clientIp from command line (if --debug, press enter)

if (len(elmoPort) == 0): elmoPort = 0

# connection with Elmo 
myElmo = ElmoServer(str(elmoIp),int(elmoPort), clientIp, debug_mode)

sg.theme('DarkBlue')   # add a touch of color

# All the stuff inside your window.

#lst = sg.Combo(imageList, font=('Arial Bold', 14),  expand_x=True, enable_events=True,  readonly=False, key='-COMBO-')
layout = [   
    [sg.Text('ELMO', size=(5, 1)), sg.Text('', size=(80, 1)), sg.Text("GAME", size=(5, 1))],
    [sg.Button("Look Player1", size=(15, 1)), sg.Button("Look Player2", size=(15, 1)), sg.Text('', size=(47, 1)), sg.Button("Intro", size=(10, 1))],
    [sg.Text("Pan", size=(3, 1)), sg.InputText(key="pan_value", size=(18, 1)), sg.Button("Set", key="SetPan", size=(8, 1)), sg.Text('', size=(5, 1)), sg.Button("Set Default", key="SetDefaultPan", size=(10, 1)), sg.Text('', size=(26, 1)), sg.Button("Play", size=(10, 1))],
    [sg.Text("Tilt", size=(3, 1)), sg.InputText(key="tilt_value", size=(18, 1)), sg.Button("Set", key="SetTilt", size=(8, 1)),  sg.Text('', size=(5, 1)), sg.Button("Set Default", key="SetDefaultTilt", size=(10, 1)), sg.Text('', size=(26, 1)), sg.Button("🔴", size=(10, 1))],
    [sg.Button("Toggle Behaviour", size=(15, 1)), sg.Button("Toggle Motors", size=(15, 1)), sg.Text('', size=(47, 1)), sg.Button("Next", size=(10, 1))],
    [sg.Text('', size=(1, 2))], 
    [sg.Text("Accuracy: "), sg.Text("0  ", key="player_accuracy"), sg.Text('', size=(46, 1)), sg.Text("Player1: "), sg.Text("0", key="player1_points", size=(10, 1))],
    [sg.Button("Bad", size=(10, 1)), sg.Button("Good", size=(10, 1)), sg.Button("Awesome", size=(10, 1)), sg.Text('', size=(20, 1)), sg.Text("Player2: "), sg.Text("0", key="player2_points", size=(10, 1))],
    [sg.Text('', size=(1, 2))], 
    [sg.Text('', size=(1, 1)), sg.Button("Winner", size=(24, 1)), sg.Text('', size=(5, 1)), sg.Button("Restart", size=(24, 1)), sg.Text('', size=(5, 1)), sg.Button("Close All", size=(24, 1))],
    [sg.Text('', size=(1, 1))], 
    [sg.Image(filename="", key="image")]  
]

# Create the Window
title = 'Elmo: WoZ'
if (len(elmoIp) > 0): title += '  ' + 'idmind@' + elmoIp
window = sg.Window(title, layout, finalize=True)

# Initial image update
img = myElmo.grabImage()
imgbytes = cv2.imencode(".png", img)[1].tobytes()
window['image'].update(data=imgbytes)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read(timeout = 5000)

    print("[EVENT]: ", event, values)

    # lets update the image
    img = myElmo.grabImage()
    imgbytes = cv2.imencode(".png", img)[1].tobytes()
    window['image'].update(data=imgbytes)

    if event == "Toggle Behaviour":
        print("Toggling Behaviour")
        myElmo.toggleBehaviour()
        # change the color of the button
        if myElmo.activeBehaviour:
            window['Toggle Behaviour'].update(button_color=('white', 'green'))
        else:
            window['Toggle Behaviour'].update(button_color=('white', 'red'))
    
    if event == "Toggle Motors":
        print("Toggling Motors")
        myElmo.toggleMotors()
        # change the color of the button
        if myElmo.activeMotors:
            window['Toggle Motors'].update(button_color=('white', 'green'))
        else:
            window['Toggle Motors'].update(button_color=('white', 'red'))
    
    if event == "Look Player1":
        print("Looking at player 1")
        myElmo.moveLeft(default_pan, default_tilt)
    
    elif event == "Look Player2":
        myElmo.moveRight(default_pan, default_tilt)
        print("Looking at player 2")
   
    if event == "SetPan":
        value = values["pan_value"]
        if value: 
            myElmo.movePan(value)
            default_pan = int(value)
    
    if event == "SetDefaultPan":
        value = values["pan_value"]
        # update value
        if (value):
            default_pan = int(value)
        else: 
            default_pan = 0
        myElmo.movePan(default_pan)

    if event == "SetTilt":
        value = values["tilt_value"]
        if value:
            myElmo.moveTilt(value)
            default_tilt = int(value)

    if event == "SetDefaultTilt":
        value = values["tilt_value"]
        # update value
        if (value):
            default_pan = int(value)
        else:
            default_tilt = 0
        myElmo.movePan(default_tilt)

    if event == "Intro":
        myElmo.introduceGame()
        myElmo.playGame()

    elif event == "Play":
        emotion = emotions[play-1]
        myElmo.sayEmotion(emotion)
    
    elif event == "🔴":
        frame = myElmo.takePicture()
        emotion = emotions[play-1]
        value = myElmo.analysePicture(frame, emotion)
        value = round(value)
        # update the text box with the result
        window['player_accuracy'].update(value)
        # update points and display
        points[str((play + 1) % 2 + 1)] += value
        window['player'+ str((play + 1) % 2 + 1)+"_points"].update(points[str((play + 1) % 2 + 1)])

    elif event == "Next":
        play += 1
        if play > len(emotions):
            myElmo.movePan(0)
            myElmo.endGame()
        else:
            emotion = emotions[play-1]
            # check each player is next
            player = (play + 1) % 2 + 1
            if (player == 1):
                myElmo.moveLeft(default_pan, default_tilt)
            else:
                myElmo.moveRight(default_pan, default_tilt)
            time.sleep(1)
            # say new emotion
            myElmo.sayEmotion(emotion)
    
    if event == "Bad":
        face = random.choice(bad_face)
        sound = feedback_sounds[face]
        myElmo.setImage(face)
        myElmo.playSound(sound)

    elif event == "Good":
        face = random.choice(good_face)
        sound = feedback_sounds[face]
        myElmo.setImage(face)
        myElmo.playSound(sound)

    elif event == "Awesome":
        face = random.choice(awesome_face)
        sound = feedback_sounds[face]
        myElmo.setImage(face)
        myElmo.playSound(sound)

    if event == "Normal":
        myElmo.setImage("normal")
        myElmo.sendMessage("icon::elmo_idm.png")

    if event == "Winner":
        winner = max(points, key=points.get)
        myElmo.congratsWinner()

    if event == "Restart":
        play = 1
        points["1"] = 0
        points["2"] = 0

    if event == sg.WIN_CLOSED or event == "Close All": # if user closes window or clicks cancel
        print("Windows is going to close")
        myElmo.closeAll()
        break

window.close()