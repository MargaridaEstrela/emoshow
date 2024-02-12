from simon_says_logger import SimonSaysLogger
from simon_says import SimonSays
from server import ElmoServer

import PySimpleGUI as sg
import threading
import cv2
import sys

elmo = None
elmo_ip = None
window = None
simon_says = None
debug_mode = False
logger = None


def create_layout():

    sg.theme("LightBlue3")

    layout = [
        [sg.Text("", size=(1, 1))],
        [
            sg.Text("", size=(1, 1)),
            sg.Button("Toggle Behaviour", size=(15, 1), button_color=("white", "red")),
            sg.Button("Toggle Motors", size=(15, 1), button_color=("white", "red")),
            sg.Text("", size=(10, 1)),
            sg.Text("Speakers", size=(10, 1)),
            sg.Text("", size=(6, 1)),
            sg.Button("Player 1", size=(15, 1)),
            sg.Text("", size=(1, 1)),
            sg.Text("0", key="player1_points", size=(10, 1)),
        ],
        [
            sg.Text("", size=(1, 1)),
            sg.Text("Pan", size=(3, 1)),
            sg.InputText(key="pan_value", size=(18, 1)),
            sg.Button("Set", key="SetPan", size=(8, 1)),
            sg.Text("", size=(10, 1)),
            sg.Button("⬆", size=(5, 1)),
            sg.Text("", size=(10, 1)),
            sg.Button("Player 2", size=(15, 1)),
            sg.Text("", size=(1, 1)),
            sg.Text("0", key="player2_points", size=(10, 1)),
        ],
        [
            sg.Text("", size=(1, 1)),
            sg.Text("Tilt", size=(3, 1)),
            sg.InputText(key="tilt_value", size=(18, 1)),
            sg.Button("Set", key="SetTilt", size=(8, 1)),
            sg.Text("", size=(10, 1)),
            sg.Button("⬇", size=(5, 1)),
            sg.Text("", size=(10, 1)),
            sg.Button("Full Attention", size=(15, 1), button_color=("white", "green")),
        ],
        [sg.Text("", size=(1, 2))],
        [
            sg.Text("", size=(1, 1)),
            sg.Button("Play", size=(24, 1)),
            sg.Text("", size=(5, 1)),
            sg.Button("Restart", size=(24, 1)),
            sg.Text("", size=(5, 1)),
            sg.Button("Close All", size=(24, 1)),
        ],
        [sg.Text("", size=(1, 1))],
        [sg.Image(filename="", key="image")],
    ]

    return layout


def handle_events():
    event, values = window.read(timeout=1)

    print("[EVENT]: ", event, values)

    if not debug_mode:
        # lets update the image
        img = elmo.grab_image()
        img_bytes = cv2.imencode(".png", img)[1].tobytes()
        window["image"].update(data=img_bytes)

    if event == "Toggle Behaviour":
        elmo.toggle_behaviour()
        # change the color of the button
        if elmo.get_control_behaviour():
            window["Toggle Behaviour"].update(button_color=("white", "green"))
        else:
            window["Toggle Behaviour"].update(button_color=("white", "red"))

    if event == "Toggle Motors":
        elmo.toggle_motors()
        # Change the color of the button
        if elmo.get_control_motors():
            window["Toggle Motors"].update(button_color=("white", "green"))
        else:
            window["Toggle Motors"].update(button_color=("white", "red"))

    if event == "SetPan":
        value = values["pan_value"]
        if value:
            elmo.move_pan(value)
            default_pan = int(value)
            elmo.set_default_pan(default_pan)

    if event == "SetTilt":
        value = values["tilt_value"]
        if value:
            elmo.move_tilt(value)
            default_tilt = int(value)
            elmo.set_default_tilt(default_tilt)

    if event == "⬆":
        elmo.increase_volume()

    if event == "⬇":
        elmo.decrease_volume()

    if event == "Player 1":
        print("Looking at player 1")
        elmo.move_left()

    if event == "Player 2":
        elmo.move_right()
        print("Looking at player 2")

    if event == "Full Attention":
        simon_says.toggle_attention()
        if simon_says.get_attention():  # equal attention
            window["Full Attention"].update(button_color=("white", "green"))
        else:  # unequal attention
            window["Full Attention"].update(button_color=("white", "red"))

    if event == "Play":
        simon_says.set_status(1)  # playing game
        elmo.send_message(f"status::{simon_says.get_status()}")
        if simon_says.game_thread is None or not simon_says.game_thread.is_alive():
            simon_says.game_thread = threading.Thread(target=simon_says.play_game)
            simon_says.game_thread.start()

    if event == "Restart":
        simon_says.stop_game()
        simon_says.restart_game()

        window["player1_points"].update(0)
        window["player2_points"].update(0)
        elmo.set_image("normal")
        elmo.send_message("icon::elmo_idm.png")
        elmo.move_pan(0)

    if (
        event == sg.WIN_CLOSED or event == "Close All"
    ):  # if user closes window or clicks cancel
        print("Closing all...")
        elmo.close_all()
        logger.close()
        window.close()


def main():
    global elmo, elmo_ip, window, simon_says, debug_mode, logger

    # Parse arguments
    if len(sys.argv) == 1:
        elmo_ip = ""
        elmo_port = 0
        client_ip = ""
        debug_mode = True  # running in debug mode (just gui)

    elif len(sys.argv) == 4:
        elmo_ip, elmo_port, client_ip = sys.argv[1:4]
        debug_mode = False

    elif len(sys.argv) == 5:
        elmo_ip, elmo_port, client_ip = sys.argv[1:4]
        if sys.argv[4] == "--connect":
            connect_mode = True

    else:
        print("Usage: python3 interface.py <elmo_ip> <elmo_port> <client_ip>")
        return

    # Start logger
    logger = SimonSaysLogger()

    # Start server
    elmo = ElmoServer(
        elmo_ip, int(elmo_port), client_ip, logger, debug_mode, connect_mode
    )

    # Start Simon Says game
    simon_says = SimonSays(elmo)  # default: equal attention

    # Create window
    layout = create_layout()

    # Create the Window
    title = "Simon Says"
    if len(elmo_ip) > 0:
        title += "  " + "idmind@" + elmo_ip
    window = sg.Window(title, layout, finalize=True)

    print("window created")

    if not debug_mode:
        # Initial image update
        img = elmo.grab_image()
        img_bytes = cv2.imencode(".png", img)[1].tobytes()
        window["image"].update(data=img_bytes)

    # Event loop
    while True:
        handle_events()


if __name__ == "__main__":
    main()
