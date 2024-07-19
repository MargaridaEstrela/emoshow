import sys
import threading

import cv2
import PySimpleGUI as sg

from server import ElmoServer
from emoshow import EmoShow
from emoshow_logger import EmoShowLogger

elmo = None
elmo_ip = None
window = None
logger = None
emoshow = None
debug_mode = False
connect_mode = False


def create_layout():
    """
    Creates the layout for the Emo-Show game interface.

    Returns:
        list: The layout of the interface as a list of elements.
    """

    sg.theme("LightBlue3")

    settings_layout = [
        [sg.Text("", size=(1, 1))],
        [
            sg.Text("", size=(8, 1)),
            sg.Button("Toggle Behaviour", size=(15, 1), button_color=("white", "red")),
            sg.Button("Toggle Motors", size=(15, 1), button_color=("white", "green")),
            sg.Text("", size=(9, 1)),
            sg.Text("Speakers", size=(10, 1)),
            sg.Text("", size=(11, 1)),
            sg.Button("Center Player", size=(15, 1)),
        ],
        [
            sg.Text("", size=(8, 1)),
            sg.Text("Pan", size=(3, 1)),
            sg.InputText(key="pan_value", size=(18, 1)),
            sg.Button("Set", key="SetPan", size=(8, 1)),
            sg.Text("", size=(9, 1)),
            sg.Button("⬆", size=(5, 1)),
            sg.Text("", size=(15, 1)),
            sg.Button("Default Screen", size=(15, 1)),
        ],
        [
            sg.Text("", size=(8, 1)),
            sg.Text("Tilt", size=(3, 1)),
            sg.InputText(key="tilt_value", size=(18, 1)),
            sg.Button("Set", key="SetTilt", size=(8, 1)),
            sg.Text("", size=(9, 1)),
            sg.Button("⬇", size=(5, 1)),
            sg.Text("", size=(15, 1)),
            sg.Button("Default Icon", size=(15, 1)),
        ],
        [
            sg.Text("", size=(8, 1)),
            sg.Button("Toggle Blush", size=(15, 1), button_color=("white", "red")),
            sg.Button("Check Speakers", size=(15, 1)),
            sg.Text("", size=(35, 1)),
            sg.Button("Feedback", size=(15, 1), button_color=("white", "green")),
        ],
        [sg.Text("", size=(1, 2))],
        [
            sg.Text("", size=(9, 1)),
            sg.Button("Play", size=(22, 1)),
            sg.Text("", size=(5, 1)),
            sg.Button("Restart", size=(22, 1)),
            sg.Text("", size=(5, 1)),
            sg.Button("Close All", size=(22, 1)),
            sg.Text("", size=(1, 1)),
        ],
        [sg.Text("", size=(1, 1))],
        [sg.Text("", size=(2, 1)), sg.Image(filename="", key="image")],
        [sg.Text("", size=(1, 1))],
    ]

    game_layout = [
        [sg.Text("", size=(1, 1))],
        [
            sg.Text("", size=(1, 1)),
            sg.Text("Log filename:"),
            sg.Input(key="-FILENAME-"),
            sg.Button("Ok", size=(5, 1)),
        ],
        [sg.Text("", size=(1, 1))],
        [
            sg.Text("", size=(1, 1)),
            sg.Text("Move: ", size=(9, 1)),
            sg.Text("", size=(5, 1), key="move"),
            sg.Text("", size=(30, 1)),
            sg.Text("Emotion: ", size=(9, 1)),
            sg.Text("", size=(11, 1), key="emotion"),
        ],
        [
            sg.Text("", size=(1, 1)),
            sg.Text("Player 1: ", size=(9, 1)),
            sg.Text("", size=(15, 1), key="player1"),
        ],
        [
            sg.Text("", size=(1, 1)),
            sg.Text("Player 2: ", size=(9, 1)),
            sg.Text("", size=(15, 1), key="player2"),
        ],
        [sg.Text("", size=(1, 1))],
        [
            sg.Text("", size=(1, 1)),
            sg.Text("Emotions 1:", size=(9, 1)),
            sg.Text("", size=(100, 1), key="emotions1"),
        ],
        [
            sg.Text("", size=(1, 1)),
            sg.Text("Emotions 2:", size=(9, 1)),
            sg.Text("", size=(100, 1), key="emotions2"),
        ],
        [sg.Text("", size=(1, 2))],
        [
            sg.Text("", size=(1, 1)),
            sg.Text("First Player:", size=(9, 1)),
            sg.Text("", size=(5, 1), key="first"),
        ],
        [
            sg.Text("", size=(1, 1)),
            sg.Text("Excluded Player:", size=(13, 1)),
            sg.Text("", size=(5, 1), key="excluded"),
        ],
        [sg.Text("", size=(1, 2))],
    ]

    layout = [
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab("Settings", settings_layout),
                        sg.Tab("Game", game_layout),
                    ]
                ],
                key="-TAB GROUP-",
                expand_x=True,
                expand_y=True,
            ),
        ]
    ]

    return layout


def handle_events():
    """
    Handle events from the GUI window.

    This function reads events from the GUI window and performs corresponding
    actions based on the event type.
    It updates the image displayed in the window, toggles Elmo's behavior and
    motors, sets the pan and tilt values, adjusts the volume, moves Elmo left or
    right, toggles feedback mode, starts or restarts the game, and handles
    window close event.
    """
    event, values = window.read(timeout=1)

    window["move"].update(emoshow.get_move())
    window["emotion"].update(emoshow.get_emotion())
    window["player1"].update(emoshow.get_points()["1"])
    window["player2"].update(emoshow.get_points()["2"])
    window["emotions1"].update(emoshow.get_shuffled_emotions()["1"])
    window["emotions2"].update(emoshow.get_shuffled_emotions()["2"])
    window["first"].update(emoshow.get_first_player())
    window["excluded"].update(emoshow.get_excluded_player())

    if not debug_mode and not connect_mode:
        img = elmo.grab_image()
        img_bytes = cv2.imencode(".png", img)[1].tobytes()
        window["image"].update(data=img_bytes)

    if event == "Ok":
        logger.set_filename(values["-FILENAME-"])

    if event == "Toggle Behaviour":
        elmo.toggle_behaviour()
        # Change the color of the button
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
            elmo.set_default_pan_left(-default_pan)
            elmo.set_default_pan_right(default_pan)

    if event == "SetTilt":
        value = values["tilt_value"]
        if value:
            elmo.move_tilt(value)
            default_tilt = int(value)
            elmo.set_default_tilt_left(default_tilt)
            elmo.set_default_tilt_right(default_tilt)

    if event == "Toggle Blush":
        elmo.toggle_blush()
        # Change the color of the button
        if elmo.get_control_blush():
            window["Toggle Blush"].update(button_color=("white", "green"))
        else:
            window["Toggle Blush"].update(button_color=("white", "red"))

    if event == "Check Speakers":
        elmo.play_sound("picture.wav")

    if event == "⬆":
        elmo.increase_volume()

    if event == "⬇":
        elmo.decrease_volume()

    if event == "Center Player":
        emoshow.center_player()

    if event == "Default Screen":
        elmo.set_image("normal.png")

    if event == "Default Icon":
        elmo.set_icon("elmo_idm.png")

    if event == "Feedback":
        emoshow.toggle_feedback()
        # Change the color of the button
        if emoshow.get_feedback():  # Feedback for both players
            window["Feedback"].update(button_color=("white", "green"))
        else:  # Player 2 doesn't receive feedback
            window["Feedback"].update(button_color=("white", "red"))

    if event == "Play":
        emoshow.set_status(1)  # Playing games
        if emoshow.game_thread is None or not emoshow.game_thread.is_alive():
            emoshow.game_thread = threading.Thread(target=emoshow.play_game)
            emoshow.game_thread.start()

    if event == "Restart":
        emoshow.stop_game()
        emoshow.restart_game()

    if (
        event == sg.WIN_CLOSED or event == "Close All"
    ):  # If user closes window or clicks cancel
        print("Closing all...")
        elmo.close_all()
        logger.close()
        window.close()


def main():
    """
    The main function of the Emo-Show game interface.

    This function parses command line arguments, initializes the logger, starts the server,
    creates the game window, and enters the event loop to handle user interactions.
    """
    global elmo, elmo_ip, window, emoshow, debug_mode, connect_mode, logger

    # Parse arguments
    if len(sys.argv) == 1:
        elmo_ip = ""
        elmo_port = 0
        client_ip = ""
        debug_mode = True  # Running in debug mode (just gui)

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
    logger = EmoShowLogger()
    logger.set_window(window)

    # Start server
    elmo = ElmoServer(
        elmo_ip, int(elmo_port), client_ip, logger, debug_mode, connect_mode
    )

    # Start Emo-Show game
    emoshow = EmoShow(elmo, logger)

    layout = create_layout()

    # Create window
    title = "Emo-Show"
    if len(elmo_ip) > 0:
        title += "  " + "idmind@" + elmo_ip
    window = sg.Window(title, layout, finalize=True)

    if not debug_mode and not connect_mode:
        # Initial image update
        img = elmo.grab_image()
        img_bytes = cv2.imencode(".png", img)[1].tobytes()
        window["image"].update(data=img_bytes)

    # Event loop
    while True:
        handle_events()


if __name__ == "__main__":
    main()
