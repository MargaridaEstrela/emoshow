import socket
import time

import cv2
import numpy as np
import requests
from deepface import DeepFace


class ElmoServer:
    """
    Represents the server for controlling Elmo, a robotic toy.

    Args:
        elmo_ip (str): The IP address of the Elmo device.
        elmo_port (int): The port number for communication with the Elmo device.
        client_ip (str): The IP address of the client.
        logger (Logger): An instance of the logger for logging messages.
        debug (bool, optional): Specifies whether debug mode is enabled.
                                Defaults to False.
        connect_mode (bool, optional): Specifies whether the server is in
                                    connect mode. Defaults to False.

    Methods:
        set_default_pan(default_pan): Set the default pan angle
        set_default_tilt(default_tilt): Set the default tilt angle
        get_control_motors(): Get the status of the motor control
        get_control_behaviour(): Get the status of the behaviour control
        connect_elmo(): Connect to the Elmo robot
        send_message(message): Send a message to the Elmo robot
        send_request_command(command, **kwargs): Send a request command to the
                                                Elmo robot
        toggle_motors(): Toggle the motor control
        toggle_behaviour(): Toggle the behaviour control
        move_pan(angle): Pan move with a specific angle
        move_tilt(angle): Tilt move with a specific angle
        move_left(): Move to the left
        move_right(): Move to the right
        increase_volume(): Send message to increase the volume
        decrease_volume(): Send message to decrease the volume
        grab_image(): Capture an image
        set_image(image_name): Set the image
        play_game(): Send status message - game on
        introduce_game(): Introduce the game
        say_emotion(emotion): Say an emotion
        take_picture(): Take a picture
        analyse_picture(frame, emotion): Analyse the picture
        play_sound(sound): Play a sound
        end_game(): End the game
        congrats_winner(): Congratulate the winner
        close_all(): Close all connections

    """

    def __init__(
        self, elmo_ip, elmo_port, client_ip, logger, debug=False, connect_mode=False
    ):
        self.elmo_ip = elmo_ip
        self.elmo_port = elmo_port
        self.client_ip = client_ip
        self.elmo_socket = None

        self.connect_mode = connect_mode
        self.logger = logger

        self.default_pan = 0
        self.default_tilt = 0

        # For default, motors and behavior are disabled
        self.control_motors = True
        self.control_behaviour = False

        self.send_request_command("enable_behaviour", name="look_around", control=False)
        self.send_request_command("set_tilt_torque", control=True)
        self.send_request_command("set_pan_torque", control=True)

        if not debug:
            self.connect_elmo()
            self.debug = False
        else:
            print("Debug mode has been activated")
            self.debug = True

        self.send_message("image::normal")
        self.send_message("icon::elmo_idm.png")

    def set_default_pan(self, default_pan):
        """
        Sets the default pan angle.

        Args:
            default_pan (int): The default pan angle.
        """
        self.default_pan = default_pan

    def set_default_tilt(self, default_tilt):
        """
        Sets the default tilt angle.

        Args:
            default_tilt (int): The default tilt angle.
        """
        self.default_tilt = default_tilt

    def get_control_motors(self):
        """
        Returns the control motors object.

        Returns:
            bool: The control motors object.
        """
        return self.control_motors

    def get_control_behaviour(self):
        """
        Returns the control behaviour object.

        Returns:
            bool: The control behaviour object.
        """
        return self.control_behaviour

    def connect_elmo(self):
        """
        Connects to the Elmo robot.
        """
        self.elmo_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket created!")

    def send_message(self, message):
        """
        Sends a message to the Elmo robot.

        Args:
            message (str): The message to be sent.
        """
        self.logger.log_message(message)

        if self.debug == True:
            print("[DEBUG]: " + message)
            return "debug"

        print("Sending message: " + message)
        self.elmo_socket.sendto(message.encode("utf-8"), (self.elmo_ip, self.elmo_port))

    def send_request_command(self, command, **kwargs):
        """
        Sends a request command to the Elmo robot.

        Args:
            command (str): The command to be sent.
            **kwargs: Additional keyword arguments for the command.
        """
        if not self.connect_mode:
            try:
                url = "http://" + self.elmo_ip + ":8001/command"
                kwargs["op"] = command
                print(kwargs)
                res = requests.post(url, json=kwargs, timeout=1).json()
                if not res["success"]:
                    self.on_error(res["message"])
            except Exception as e:
                print(e)

    def toggle_motors(self):
        """
        Toggles the control of the motors and send a message and request command.
        """
        self.control_motors = not self.control_motors
        self.send_message(f"motors::{self.control_motors}")
        self.send_request_command("set_tilt_torque", control=self.control_motors)
        self.send_request_command("set_pan_torque", control=self.control_motors)

    def toggle_behaviour(self):
        """
        Toggles the control behaviour and send a message and request command.
        """
        self.control_behaviour = not self.control_behaviour
        self.send_message(f"behaviour::{self.control_behaviour}")
        self.send_request_command(
            "enable_behaviour", name="look_around", control=self.control_behaviour
        )
        print("Behaviour: ", self.control_behaviour)

    def move_pan(self, angle):
        """
        Moves the pan with a specific angle.

        Args:
            angle (int): The angle to move the pan.
        """
        self.send_message(f"pan::{angle}")

    def move_tilt(self, angle):
        """
        Moves the tilt with a specific angle.

        Args:
            angle (int): The angle to move the tilt.
        """
        self.send_message(f"tilt::{angle}")

    def move_left(self):
        """
        Moves the device to the left with a symmetrical default pan angle.

        This method adjusts the pan value to move the device to the left.
        The tilt value remains unchanged.
        """
        pan_value = -self.default_pan
        self.send_message(f"pan::{pan_value}")
        self.send_message(f"tilt::{self.default_tilt}")

    def move_right(self):
        """
        Moves the device to the right with a default pan angle.

        This method adjusts the pan value to move the device to the right.
        The tilt value remains unchanged.
        """
        self.send_message(f"pan::{self.default_pan}")
        self.send_message(f"tilt::{self.default_tilt}")

    def increase_volume(self):
        """
        Sends a message to increase the volume.
        """
        self.send_message("speakers::increaseVolume")

    def decrease_volume(self):
        """
        Sends a message to decrease the volume.
        """
        self.send_message("speakers::decreaseVolume")

    def grab_image(self):
        """
        Captures an image.

        Returns:
            np.ndarray: The captured image.
        """
        if self.debug:
            return

        if self.connect_mode:
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                self.logger.log_error("Failed to open camera")

            ret, frame = cap.read()  # Capture a frame

            if not ret:
                self.logger.log_error("Failed to capture frame")
                cap.release()
                return np.full((480, 640, 3), 26, dtype=np.uint8)

            cap.release()

        else:
            url = f"http://{self.elmo_ip}:8080/stream.mjpg"
            response = requests.get(url, stream=True)

            if response.status_code == 200:  # Is a valid response
                stream = response.iter_content(chunk_size=1024)
                bytes_ = b""
                for chunk in stream:
                    bytes_ += chunk
                    a = bytes_.find(b"\xff\xd8")
                    b = bytes_.find(b"\xff\xd9")
                    if a != -1 and b != -1:
                        jpg = bytes_[a : b + 2]
                        bytes_ = bytes_[b + 2 :]
                        frame = cv2.imdecode(
                            np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR
                        )
                        break

        # Resize the image to 480x640
        frame = cv2.resize(frame, (640, 480))
        return frame

    def set_image(self, image_name):
        """
        Sets the image.

        Args:
            image_name (str): The source name of the image.
        """
        self.send_message(f"image::{image_name}")

    def play_game(self):
        """
        Sends a status message to start the game.
        """
        self.send_message("game::on")

    def introduce_game(self):
        """
        Introduces the game.
        """
        self.send_message("sound::introGame.wav")

    def say_emotion(self, emotion):
        """
        Says an emotion.

        Args:
            emotion (str): The emotion to say.
        """
        self.send_message(f"sound::{emotion}.wav")

    def take_picture(self):
        """
        Sound and icons sequence to display when taking a picture.

        This method plays a sound, displays a countdown sequence of icons (3, 2, 1), and captures an image.

        Returns:
            np.ndarray: The captured picture.
        """
        self.send_message("sound::takePicture.wav")

        # show 3, 2, 1 and take a picture
        self.send_message("icon::3.jpeg")
        time.sleep(1)

        self.send_message("icon::2.jpeg")
        time.sleep(0.5)

        self.send_message("icon::1.jpeg")
        time.sleep(0.7)

        self.send_message("icon::camera.jpeg")

        return self.grab_image()

    def analyse_picture(self, frame, emotion):
        """
        Analyzes a picture frame and returns the specified emotion.

        Args:
            frame (numpy.ndarray): The picture frame to be analyzed.
            emotion (str): The emotion to be extracted from the analysis.

        Returns:
            float: The value of the specified emotion in the analysis.
        """
        try:
            face_analysis = DeepFace.analyze(frame)
        except Exception as e:
            self.logger.log_error(e)
            return None
        
        self.logger.log_message(face_analysis[0])
        return face_analysis[0]["emotion"][emotion]

    def play_sound(self, sound):
        """
        Plays the specified sound.

        Args:
            sound (str): The source name of the sound to be played.
        """
        self.send_message(f"sound::{sound}")

    def end_game(self):
        """
        Sends a message to the robot to play the end game sound.
        """
        self.send_message("sound::end_game.wav")

    def congrats_winner(self):
        """
        Sends a message to the robot to play the sound to congratulate the winner.
        """
        self.send_message("sound::winner.wav")

    def close_all(self):
        """
        Closes all connections and shuts down the server.

        Sends a "game::off" message to the robot.
        If the debug flag is set to False, it also shuts down the Elmo socket.

        """
        self.send_message("game::off")

        if self.debug == False:
            self.elmo_socket.shutdown(socket.SHUT_RDWR)
            self.elmo_socket.close()
            return
        return
