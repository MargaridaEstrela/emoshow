import time
import socket
import requests
import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


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

    # grab the image from the camera
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


def connectElmo(address="192.168.0.102", port="4000", client_ip="192.168.0.114"):
    # this will start the socket used to communicate with elmo
    elmoSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    elmoSocket.bind((client_ip,port))

    return elmoSocket


def sendMessage(message, elmoSocket, server):
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
    """
    This will show the image with the faces
    """
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

    # angle = input("Enter angle: ")
    # sendMessage("pan::" + str(angle), elmoSocket, (elmoIp, elmoPort))
    data = sendMessage("getImage::off", elmoSocket, (elmoIp, elmoPort))
    imageList = eval(data)

    counter = 0
    while True:
        print("sending this image: ", imageList[counter])
        data = sendMessage(f"image::{imageList[counter]}", elmoSocket, (elmoIp, elmoPort))
        counter +=1
        if counter > len(imageList)-1:
            counter = 0
        time.sleep(1)






if __name__=='__main__':

    elmoIp = "192.168.0.102"
    elmoPort = 4000
    clientIp = "192.168.0.114"


    elmoSocket = connectElmo(elmoIp, elmoPort, clientIp)
    elmoSocket.settimeout(1) # not sure what this is doing


    while True:
        # loop()
        userLoop()
    # sendMessage("pan::0", elmoSocket, (elmoIp, elmoPort))
    



# action::value


# pan::30
# tilt::0

# image::image.png
