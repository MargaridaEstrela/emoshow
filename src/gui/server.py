from deepface import DeepFace

import time
import socket
import requests
import cv2
import numpy as np
import time 


class ElmoServer:

    def __init__(self, elmoIp="192.168.1.92", elmoPort=4000, clientIp="192.168.1.84"):
        self.elmoIp = elmoIp
        self.elmoPort = elmoPort
        self.clientIp = clientIp

        # set the motors and behaviour to false
        self.activeBehaviour = False
        self.activeMotors = False
        #self.sendRequestCommand("enable_behaviour", name="look_around", control=False)
        #self.sendRequestCommand("set_tilt_torque", control=False)
        #self.sendRequestCommand("set_pan_torque", control=False)

        self.connectElmo()

    def connectElmo(self):
        # this will start the socket used to communicate with elmo
        self.elmoSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.elmoSocket.bind((self.clientIp,self.elmoPort))
        print("Connecting as okay")


    def sendMessage(self, message):
        """
        This will send a message to elmo
        """
        print("Sending message: " + message)
        self.elmoSocket.sendto(message.encode('utf-8'), (self.elmoIp, self.elmoPort))
        data, addr = self.elmoSocket.recvfrom(1024)     # wait for the response from elmo
        data = data.decode('utf-8')
        print("  Received from server: " + data)
        return data
    

    def getImageList(self):
        # this will grab the list of images from elmo
        data = self.sendMessage("getImage::none")
        self.imageList = eval(data)
        return self.imageList


    def setImage(self, image_name):
        # this will set the image on elmo
        data = self.sendMessage(f"image::{image_name}")


    def movePan(self, angle):
        # this will move elmo's pan
        data = self.sendMessage(f"pan::{angle}")


    def moveTilt(self, angle):
        # this will move elmo's tilt
        data = self.sendMessage(f"tilt::{angle}")


    def moveLeft(self):
        # this will move elmo left
        data = self.sendMessage(f"pan::-30")


    def moveRight(self):
        # this will move elmo left
        data = self.sendMessage(f"pan::30")

    def grabImage(self):
        # grab the image from the camera
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

            return frame
        return None


    def introduceGame(self):
        data = self.sendMessage(f"sound::intro.wav")
        time.sleep(6)

        data = self.sendMessage(f"sound::rules.wav")
        time.sleep(6)

        data = self.sendMessage(f"sound::ready.wav")
        time.sleep(6)


    def playGame(self):
        # this will start the game
        data = self.sendMessage(f"game::on")
    

    def sayEmotion(self, emotion):
        data = self.sendMessage(f"sound::{emotion}.wav")


    def endGame(self):
        data = self.sendMessage(f"sound::end_game.wav")


    def congratsWinner(self):
        data = self.sendMessage(f"sound::winner.wav")


    def closeAll(self):
        # this will end the game
        data = self.sendMessage(f"game::off")

        time.sleep(1)

        # close all
        self.elmoSocket.close()


    def takePicture(self):
        # show 3, 2, 1 and take a picture
        data = self.sendMessage(f"icon::call.png")
        time.sleep(1)

        data = self.sendMessage(f"icon::music.png")
        time.sleep(1)

        data = self.sendMessage(f"icon::call.png")
        time.sleep(1)

        data = self.sendMessage(f"icon::elmo_idm.png")
        time.sleep(1)

        return self.grabImage()


    def analysePicture(self, frame, emotion):
        face_analysis = DeepFace.analyze(frame)
        return face_analysis["emotion"][emotion]


    def toggleMotors(self):
        # this will enable elmo's motors
        data = self.sendMessage(f"motors::enable")
        self.activeMotors = not self.activeMotors
        print("Motors are now: ", self.activeMotors)
        self.sendRequestCommand("set_tilt_torque", control=self.activeMotors)
        self.sendRequestCommand("set_pan_torque", control=self.activeMotors)


    def toggleBehaviour(self):
        # self.sendRequestCommand("disable_behaviour", name=name)
        self.activeBehaviour = not self.activeBehaviour
        self.sendRequestCommand("enable_behaviour", name="look_around", control=self.activeBehaviour)
        print("toggleBehaviour")
    

    def sendRequestCommand(self, command, **kwargs):
        try:
            url = "http://" + self.elmoIp + ":8001/command"
            kwargs["op"] = command
            print(kwargs)
            res = requests.post(url, json=kwargs, timeout=1).json()
            if not res["success"]:
                self.on_error(res["message"])
        except Exception as e:
            print(e)


if __name__=='__main__':

    elmoIp = "192.168.1.92"
    elmoPort = 4000
    clientIp = "192.168.1.84"

    myElmo = ElmoServer(elmoIp, elmoPort, clientIp)
