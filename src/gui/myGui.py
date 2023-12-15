import PySimpleGUI as sg
from server import ElmoServer
import random


elmoIp = "192.168.0.101"
elmoPort = 4000
clientIp = "192.168.0.119"

myElmo = ElmoServer(elmoIp, elmoPort, clientIp)
imageList = myElmo.getImageList()
print("this is the image list: ", imageList)    
sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.

lst = sg.Combo(imageList, font=('Arial Bold', 14),  expand_x=True, enable_events=True,  readonly=False, key='-COMBO-')
layout = [  [sg.Button("LookPlayer1"), sg.Button("LookPlayer2")],
            [lst, sg.Button("SetImage")],
            [sg.Button("Toggle Behaviour"), sg.Button("Toggle Motors")],
            [sg.Button('Ok'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Elmo Wizard of OZ', layout)
# Event Loop to process "events" and get the "values" of the inputs


while True:
    event, values = window.read()

    print(event, values)

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
    if event == "LookPlayer1":
        print("Looking at player 1")
        myElmo.moveLeft()
    elif event == "LookPlayer2":
        myElmo.moveRight()
        print("Looking at player 2")
    elif event == "SetImage":
        print("Setting Image")
        # myElmo.setImage(values['-COMBO-'])    # this is to set the image based on the dopdown list
        myElmo.setImage(random.choice(imageList))       # this is to set the image randomly

    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        print("Windows is going to close")
        break

window.close()