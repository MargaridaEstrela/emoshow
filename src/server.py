from deepface import DeepFace

import numpy as np
import requests
import socket
import time
import cv2

class ElmoServer:

    def __init__(self, elmoIp, elmoPort, clientIp, logger, debug=False, connect_mode=False):
        self.elmoIp = elmoIp
        self.elmoPort = elmoPort
        self.clientIp = clientIp

        self.connect_mode = connect_mode
        self.logger = logger

        self.default_pan = 0
        self.default_tilt = 0

        # Set the motors and behaviour to false
        self.activeBehaviour = False
        self.activeMotors = False
        
        self.sendRequestCommand("enable_behaviour", name="look_around", control=False)
        self.sendRequestCommand("set_tilt_torque", control=False)
        self.sendRequestCommand("set_pan_torque", control=False)

        if not debug:
            self.connectElmo()
            self.debug = False
        else:
            print("Debug mode has been activated")
            self.debug = True

        self.sendMessage("image::normal")
        self.sendMessage("icon::elmo_idm.png") 
    
    def connectElmo(self):
        # this will start the socket used to communicate with elmo
        self.elmoSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.elmoSocket.bind((self.clientIp,self.elmoPort))
        print("Successful connection!")

    def sendMessage(self, message):
        # log message
        self.logger.log_message(message)
        # this will send a message to elmo
        if self.debug == True:
            # means that I am in debug mode and do not want to send the message
            print("[DEBUG]: " + message)
            return "debug"
            
        print("Sending message: " + message)
        self.elmoSocket.sendto(message.encode('utf-8'), (self.elmoIp, self.elmoPort))
        data, addr = self.elmoSocket.recvfrom(1024)     # wait for the response from elmo
        data = data.decode('utf-8')
        print("Received from server: " + data)
        return data
    
    def getImageList(self):
        # this will grab the list of images from elmo
        data = self.sendMessage("getImage::none")
        self.imageList = eval(data)
        return self.imageList

    def setImage(self, image_name):
        # this will set the image on elmo
        self.sendMessage(f"image::{image_name}")

    def increaseVolume(self):
        self.sendMessage("speakers::increaseVolume")

    def decreaseVolume(self):
        self.sendMessage("speakers::decreaseVolume")

    def setDefaultPan(self, default_pan):
        self.default_pan = default_pan

    def setDefaultTilt(self, default_tilt):
        self.default_tilt = default_tilt

    def movePan(self, angle):
        # this will move elmo's pan
        data = self.sendMessage(f"pan::{angle}")

    def moveTilt(self, angle):
        # this will move elmo's tilt
        data = self.sendMessage(f"tilt::{angle}")

    def moveLeft(self):
        # this will move elmo left
        pan = -self.default_pan
        self.sendMessage(f"pan::{pan}")
        self.sendMessage(f"tilt::{self.default_tilt}")

    def moveRight(self):
        self.sendMessage(f"pan::{self.default_pan}")
        self.sendMessage(f"tilt::{self.default_tilt}")

    def grabImage(self):
        # grab the image from the camera
        if not self.connect_mode:
            url = f"http://{self.elmoIp}:8080/stream.mjpg"
            response = requests.get(url, stream=True)

            if response.status_code == 200:
                # maens that it is a valid response
                stream = response.iter_content(chunk_size=1024)
                bytes_ = b''
                for chunk in stream:
                    bytes_ += chunk
                    a = bytes_.find(b'\xff\xd8')
                    b = bytes_.find(b'\xff\xd9')
                    if a != -1 and b != -1:
                        jpg = bytes_[a:b+2]
                        bytes_ = bytes_[b+2:]
                        frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        break
                
                # resize the image to 480, 640
                frame = cv2.resize(frame, (640, 480))
                return frame
            
        return np.full((480, 640, 3), 26, dtype=np.uint8)

    def introduceGame(self):
        self.sendMessage("sound::introGame.wav")

    def playGame(self):
        self.sendMessage("game::on")

    def sayEmotion(self, emotion):
        self.sendMessage(f"sound::{emotion}.wav")

    def endGame(self):
        self.sendMessage("sound::end_game.wav")

    def congratsWinner(self):
        self.sendMessage("sound::winner.wav")

    def closeAll(self):
        # this will end the game
        self.sendMessage("game::off")

        time.sleep(1)
        if self.debug == False:
            self.elmoSocket.shutdown(socket.SHUT_RDWR)
            self.elmoSocket.close()
            return 
        return

    def playSound(self, sound):
        self.sendMessage(f"sound::{sound}")

    def takePicture(self):
        self.sendMessage("sound::takePicture.wav")

        # show 3, 2, 1 and take a picture
        self.sendMessage("icon::3.jpeg")
        time.sleep(1)

        self.sendMessage("icon::2.jpeg")
        time.sleep(0.5)

        self.sendMessage("icon::1.jpeg")
        time.sleep(0.7)

        self.sendMessage("icon::camera.jpeg")

        return self.grabImage()

    def analysePicture(self, frame, emotion):
        try:
            face_analysis = DeepFace.analyze(frame)
        except Exception as e:
            print(e)
            return None
        print(face_analysis[0]["emotion"][emotion])
        return face_analysis[0]["emotion"][emotion]

    def toggleMotors(self):
        # this will enable elmo's motors
        self.activeMotors = not self.activeMotors
        self.sendMessage(f"motors::{self.activeMotors}")
        self.sendRequestCommand("set_tilt_torque", control=self.activeMotors)
        self.sendRequestCommand("set_pan_torque", control=self.activeMotors)

    def toggleBehaviour(self):
        self.activeBehaviour = not self.activeBehaviour
        self.sendMessage(f"behaviour::{self.activeBehaviour}") 
        self.sendRequestCommand("enable_behaviour", name="look_around", control=self.activeBehaviour)
        print("Behaviour: ", self.activeBehaviour)
    
    def sendRequestCommand(self, command, **kwargs):
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