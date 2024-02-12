from deepface import DeepFace

import numpy as np
import requests
import socket
import time
import cv2


class ElmoServer:

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
        self.control_motors = False
        self.control_behaviour = False

        self.send_request_command("enable_behaviour", name="look_around", control=False)
        self.send_request_command("set_tilt_torque", control=False)
        self.send_request_command("set_pan_torque", control=False)

        if not debug:
            self.connect_elmo()
            self.debug = False
        else:
            print("Debug mode has been activated")
            self.debug = True

        self.send_message("image::normal")
        self.send_message("icon::elmo_idm.png")

    def set_default_pan(self, default_pan):
        self.default_pan = default_pan

    def set_default_tilt(self, default_tilt):
        self.default_tilt = default_tilt

    def get_control_motors(self):
        return self.control_motors

    def get_control_behaviour(self):
        return self.control_behaviour

    def connect_elmo(self):
        self.elmo_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket created!")

    def send_message(self, message):
        self.logger.log_message(message)

        if self.debug == True:
            print("[DEBUG]: " + message)
            return "debug"

        print("Sending message: " + message)
        self.elmo_socket.sendto(message.encode("utf-8"), (self.elmo_ip, self.elmo_port))

    def send_request_command(self, command, **kwargs):
        if not self.connect_mode:
            try:
                url = "http://" + self.elmoIp + ":8001/command"
                kwargs["op"] = command
                print(kwargs)
                res = requests.post(url, json=kwargs, timeout=1).json()
                if not res["success"]:
                    self.on_error(res["message"])
            except Exception as e:
                print(e)

    def toggle_motors(self):
        self.control_motors = not self.control_motors
        self.send_message(f"motors::{self.control_motors}")
        self.send_request_command("set_tilt_torque", control=self.control_motors)
        self.send_request_command("set_pan_torque", control=self.control_motors)

    def toggle_behaviour(self):
        self.control_behaviour = not self.control_behaviour
        self.send_message(f"behaviour::{self.control_behaviour}")
        self.send_request_command(
            "enable_behaviour", name="look_around", control=self.control_behaviour
        )
        print("Behaviour: ", self.control_behaviour)

    def move_pan(self, angle):
        self.send_message(f"pan::{angle}")

    def move_tilt(self, angle):
        self.send_message(f"tilt::{angle}")

    def move_left(self):
        pan_value = -self.default_pan
        self.send_message(f"pan::{pan_value}")
        self.send_message(f"tilt::{self.default_tilt}")

    def move_right(self):
        self.send_message(f"pan::{self.default_pan}")
        self.send_message(f"tilt::{self.default_tilt}")

    def increase_volume(self):
        self.send_message("speakers::increaseVolume")

    def decrease_volume(self):
        self.send_message("speakers::decreaseVolume")

    def grab_image(self):
        if not self.connect_mode:
            url = f"http://{self.elmoIp}:8080/stream.mjpg"
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
            
        return np.full((480, 640, 3), 26, dtype=np.uint8)

    def set_image(self, image_name):
        self.send_message(f"image::{image_name}")

    def play_game(self):
        self.send_message("game::on")

    def introduce_game(self):
        self.send_message("sound::introGame.wav")

    def say_emotion(self, emotion):
        self.send_message(f"sound::{emotion}.wav")

    def take_picture(self):
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
        try:
            face_analysis = DeepFace.analyze(frame)
        except Exception as e:
            self.logger.log_message(e)
            return None
        return face_analysis[0]["emotion"][emotion]

    def play_sound(self, sound):
        self.send_message(f"sound::{sound}")

    def end_game(self):
        self.send_message("sound::end_game.wav")

    def congrats_winner(self):
        self.send_message("sound::winner.wav")

    def close_all(self):
        self.send_message("game::off")

        if self.debug == False:
            self.elmo_socket.shutdown(socket.SHUT_RDWR)
            self.elmo_socket.close()
            return
        return
