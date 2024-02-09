from server import ElmoServer
from simon_says import SimonSays

import PySimpleGUI as sg
import threading
import cv2
import sys

elmo = None
elmoIp = None
window = None
simonSays = None

def create_layout():

    sg.theme('LightBlue3')

    layout = [   
        [sg.Text('', size=(1, 1))],
        [sg.Text('', size=(1, 1)),sg.Button("Toggle Behaviour", size=(15, 1), button_color=('white', 'red')), sg.Button("Toggle Motors", size=(15, 1), button_color=('white', 'red')), sg.Text("", size=(10, 1)), sg.Text("Speakers", size=(10, 1)), sg.Text("", size=(6, 1)), sg.Button("Player 1", size=(15, 1)), sg.Text("", size=(1, 1)), sg.Text("0", key="player1_points", size=(10, 1))],
        [sg.Text('', size=(1, 1)),sg.Text("Pan", size=(3, 1)), sg.InputText(key="pan_value", size=(18, 1)), sg.Button("Set", key="SetPan", size=(8, 1)), sg.Text("", size=(10, 1)), sg.Button("⬆", size=(5, 1)), sg.Text('', size=(10, 1)), sg.Button("Player 2", size=(15, 1)), sg.Text("", size=(1, 1)), sg.Text("0", key="player2_points", size=(10, 1))],
        [sg.Text('', size=(1, 1)),sg.Text("Tilt", size=(3, 1)), sg.InputText(key="tilt_value", size=(18, 1)), sg.Button("Set", key="SetTilt", size=(8, 1)),  sg.Text("", size=(10, 1)), sg.Button("⬇", size=(5, 1)), sg.Text('', size=(10, 1)), sg.Button("Full Attention", size=(15, 1), button_color=('white', 'green'))],
        [sg.Text('', size=(1, 2))], 
        [sg.Text('', size=(1, 1)), sg.Button("Play", size=(24, 1)), sg.Text('', size=(5, 1)), sg.Button("Restart", size=(24, 1)), sg.Text('', size=(5, 1)), sg.Button("Close All", size=(24, 1))],
        [sg.Text('', size=(1, 1))], 
        [sg.Image(filename="", key="image")]  
    ]

    return layout

def handle_events():
    event, values = window.read(timeout = 1)

    print("[EVENT]: ", event, values)

    # lets update the image
    img = elmo.grabImage()
    imgbytes = cv2.imencode(".png", img)[1].tobytes()
    window['image'].update(data=imgbytes)

    if event == "Toggle Behaviour":
        print("Toggling Behaviour")
        elmo.toggleBehaviour()
        # change the color of the button
        if elmo.activeBehaviour:
            window['Toggle Behaviour'].update(button_color=('white', 'green'))
        else:
            window['Toggle Behaviour'].update(button_color=('white', 'red'))
    
    if event == "Toggle Motors":
        print("Toggling Motors")
        elmo.toggleMotors()
        # change the color of the button
        if elmo.activeMotors:
            window['Toggle Motors'].update(button_color=('white', 'green'))
        else:
            window['Toggle Motors'].update(button_color=('white', 'red'))
    
    if event == "SetPan":
        value = values["pan_value"]
        if value: 
            elmo.movePan(value)
            default_pan = int(value)
            elmo.setDefaultPan(default_pan)

    if event == "SetTilt":
        value = values["tilt_value"]
        if value:
            elmo.moveTilt(value)
            default_tilt = int(value)
            elmo.setDefaultTilt(default_tilt)

    if event == "⬆":
        elmo.increaseVolume()
    
    if event == "⬇":
        elmo.decreaseVolume()

    if event == "Player1":
        print("Looking at player 1")
        elmo.moveLeft()
    
    if event == "Player2":
        elmo.moveRight()
        print("Looking at player 2")

    if event == "Full Attention":
        simonSays.setAttention()
        if simonSays.getAttention() == 0: # equal attention
            window['Full Attention'].update(button_color=('white', 'green'))
        else: # unequal attention
            window['Full Attention'].update(button_color=('white', 'red'))
   
    if event == "Play":
        simonSays.setStatus(1) # playing game
        if simonSays.game_thread is None or not simonSays.game_thread.is_alive():
            simonSays.game_thread = threading.Thread(target=simonSays.play_game)
            simonSays.game_thread.start()

    if event == "Restart":
        simonSays.stop_game()
        simonSays.restart_game()
        
        window['player1_points'].update(0)
        window['player2_points'].update(0)
        window['player_accuracy'].update(0)
        elmo.setImage("normal")
        elmo.sendMessage("icon::elmo_idm.png")
        elmo.movePan(0)

    if event == sg.WIN_CLOSED or event == "Close All": # if user closes window or clicks cancel
        print("Closing all...")
        elmo.closeAll()
        window.close()

def main():
    global elmo, elmoIp, window, simonSays

    # Parse arguments
    if len(sys.argv) == 1:
        elmoIp = ""
        elmoPort = 0
        clientIp = ""
        debug_mode = True  # running in debug mode

    elif len(sys.argv) == 4:
        elmoIp, elmoPort, clientIp = sys.argv[1:4]
        debug_mode = False

    # Start server
    elmo = ElmoServer(elmoIp, int(elmoPort), clientIp, debug_mode)

    # Start Simon Says game
    simonSays = SimonSays(elmo) # default: equal attention

    # Create window
    layout = create_layout()

    # Create the Window
    title = 'Simon Says'
    if (len(elmoIp) > 0): title += '  ' + 'idmind@' + elmoIp
    window = sg.Window(title, layout, finalize=True)

    print("window created")

    # Initial image update
    img = elmo.grabImage()
    imgbytes = cv2.imencode(".png", img)[1].tobytes()
    window['image'].update(data=imgbytes)

    # Event loop
    while True:
        handle_events()
        
if __name__ == "__main__":
    main()
