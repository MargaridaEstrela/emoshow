from deepface import DeepFace

import time
import socket
import requests
import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

default_pan = 30
default_tilt = 0

#list with all the emotions we will ask
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

#dictionary with all the emotions possible to the respective accuracy
accuracy_dict = {50: "thinking", 80: "normal", 95: "love"}

points = {"0": 0, "1": 0}


def detect_faces(frame):
    """
    Detect faces in a given frame using OpenCV.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    #filter out faces smaller than x pixels by y pixels
    faces = list(filter(lambda face: face[2] > 300 and face[3] > 300, faces))
    
    return faces


def grabImage(url="http://192.168.0.103:8080/stream.mjpg"):
    """
    Grab the image from the camera
    """
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


def connectElmo(elmo_ip="192.168.0.102", port=4000, client_ip="192.168.0.114"):
    """
    This will start the socket used to communicate with elmo
    """
    elmoSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    elmoSocket.bind((client_ip,port))

    return elmoSocket


def getAction():
    """
    This will request a command to the user
    """
    command = input("Comand: ")
    value = input("Value: ")

    action =f"{command}::{value}"
    print("[REQUEST]: ", action)

    return action


def getAction(command, value):
    """
    This will return a request
    """
    action =f"{command}::{value}"
    print("[REQUEST]: ", action)

    return action


def sendMessage(message):
    """
    This will send a message to elmo
    """
    print("Sending message: " + message)
    elmoSocket.sendto(message.encode('utf-8'), server)
    data, addr = elmoSocket.recvfrom(1024)     # wait for the response from elmo
    data = data.decode('utf-8')
    print("  Received from server: " + data)
    return data


def showImage(image, faces):
    # this will show the image with the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x,y), (x+w, y+h), (255, 0, 0), 2)
    
    # downscale the image by 0.5
    show_image = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
    cv2.imshow('image', show_image)
    key = cv2.waitKey(1)
    if key == ord('q'):
        exit()


def loop():
    
    image = grabImage()
    faces = detect_faces(image)

    # show the image with rectanges on the faces
    showImage(image, faces)


def userLoop():
    data = sendMessage("getImage::off")
    imageList = eval(data)

    counter = 0
    while True:
        print("sending this image: ", imageList[counter])
        data = sendMessage(f"image::{imageList[counter]}")
        counter +=1
        if counter > len(imageList)-1:
            counter = 0
        time.sleep(1)


def setDefaultAngles():   
    # set default pan
    pan_message = getAction("pan", default_pan)
    sendMessage(pan_message)

    params["pan"] = default_pan
   
    # set default tilt
    tilt_message = getAction("tilt", default_tilt)
    sendMessage(tilt_message)

    params["tilt"] = default_tilt


def adjusParameters():

    while True:
        try:
            command = input("Command: ")

        except KeyboardInterrupt:
            print("\nCtrl+C detected. Exiting ...")
            elmoSocket.close()
            exit()
            
        if command == 'game':
            print("All params set!")
            break

        if command == "pan" or command == "tilt":
            value = input("Value: ")
            param_message = getAction(command, value)
            sendMessage(param_message)
            params[command] = int(value)


def introduceGame():
    intro_message = getAction("sound", "intro.m4a")
    sendMessage(intro_message)
    time.sleep(0.5)
    rules_message = getAction("sound", "rules.m4a")
    sendMessage(rules_message)
    time.sleep(0.5)
    ready_message = getAction("sound", "ready.m4a")
    sendMessage(ready_message)
    time.sleep(0.5)


def takePictureSequence():
    # show 3, 2, 1, picture
    icon_3 = getAction("icon", "cal.png")
    sendMessage(icon_3)
    time.sleep(0.5)
    icon_2 = getAction("icon", "music.png")
    sendMessage(icon_2)
    time.sleep(0.5)
    icon_1 = getAction("icon", "cal.png")
    sendMessage(icon_1)
    time.sleep(0.5)
    camera = getAction("icon", "elmo_idm.png")
    sendMessage(camera)


def play_game():

    setDefaultAngles()
    adjusParameters()

    print("Starting game...")

    # introduce game
    introduceGame()

    play = 1

    # start game
    for emotion in emotions:
        emotion_request = getAction("sound", f"{emotion}.m4a")
        sendMessage(emotion_request)

        # show 3, 2, 1, take a picture
        takePictureSequence()
        frame = grabImage()
        face_analysis = DeepFace.analyze(frame)
        
        # show feedback
        accuracy = face_analysis["emotion"][emotion]
        if (accuracy < 80):
            image = accuracy_dict[50]
        elif (accuracy < 95):
            image = accuracy_dict[80]
        else:
            image = accuracy_dict[95]

        image_display = getAction("image", image)
        sendMessage(image_display)

        # points
        points[str(play%2)] += accuracy

        # play sound randomly
        feedback_sound = getAction("sound", "correct.wav")
        sendMessage(feedback_sound)

        time.sleep(1)

        # change player
        params["pan"] = -params["pan"]
        pan_message = getAction("pan", params["pan"])
        sendMessage(pan_message)
        play += 1

    # end game sound
    print("Ending game...")
    final_sound = getAction("sound", "end_game.mp3")
    sendMessage(final_sound)

    time.sleep(1)

    # congrats the winer
    winner = max(points, key=points.get)
    params["pan"] = abs(params["pan"])

    if winner == "0":
        params["pan"] = - params["pan"]

    pan_message = getAction("pan", params["pan"])
    sendMessage(pan_message)

    winner_sound = getAction("sound", "winner.mp3")
    sendMessage(winner_sound) 


if __name__=='__main__':

    elmoIp = "192.168.0.102"
    elmoPort = 4000
    clientIp = "192.168.0.114"
    server = (elmoIp, elmoPort)

    elmoSocket = connectElmo(elmoIp, elmoPort, clientIp)
    elmoSocket.settimeout(1) # not sure what this is doing

    params = {"pan": 0, "tilt": 0}

    play_game()

    # send message to indicate the game is over
    end_game_message = getAction("game", "off")
    sendMessage(end_game_message)

    # closing socket
    elmoSocket.close()