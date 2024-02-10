import threading
import random
import time

# List of emotions to analyse
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise"]

# Feedback reactions
bad_face = ["cry", "confused", "anger"]  # the list of faces containing the necessary sounds for the bad button
good_face = ["normal", "rolling_eyes", "thinking"]  # the list of faces containing the necessary faces for the good button
awesome_face = ["lovely", "images/simon_images/stars.gif", "blush"]  # the list of faces containing the necessary faces for the awesome button

# Feedback sounds for each reaction
feedback_sounds = {"cry": "cry.wav", 
                   "confused": "confused.wav", 
                   "anger": "anger.wav", 
                   "normal": "normal.wav", 
                   "rolling_eyes": "rolling_eyes.wav", 
                   "thinking": "thinking.wav", 
                   "lovely": "lovely.wav", 
                   "images/simon_images/stars.gif": "stars.wav", 
                   "blush": "blush.wav"}

class SimonSays:

    def __init__(self, elmo):
        self.elmo = elmo
        self.move = 0
        self.player = 1
        self.points = {"1": 0, "2": 0} # points of each player
        self.status = 0 # 0: reset, 1: playing, 2: end game
        self.attention = 1 # 0: just player 1 receive feedback, 1: both players receive feedback

        # Game thread
        self.game_thread = None
        self.restart_flag = False

    def setStatus(self, status):
        self.status = status

    def setAttention(self):
        self.attention = not self.attention
        self.elmo.sendMessage(f"attention::{self.attention}")

    def getStatus(self):
        return self.status

    def getAttention(self):
        return self.attention

    def changePlayer(self):
        self.player = self.move % 2 + 1
        self.elmo.sendMessage(f"player::{self.player}")
        self.elmo.sendMessage(f"move::{self.move}") 
        if (self.player == 1):
            self.elmo.moveLeft()
        else:
            self.elmo.moveRight()

    def analyseEmotion(self):
        frame = self.elmo.takePicture()
        emotion = emotions[self.move]
        accuracy = self.elmo.analysePicture(frame, emotion)
        accuracy = round(accuracy) if accuracy else 0

        return accuracy
    
    def giveFeedback(self, accuracy):
        if accuracy < 50:
            face = random.choice(bad_face)
        elif accuracy < 80:
            face = random.choice(good_face)
        else:
            face = random.choice(awesome_face)

        self.elmo.setImage(face)
        self.elmo.playSound(feedback_sounds[face])

    def playerMove(self):
        if self.move == len(emotions):
            self.status = 2 # end game
            self.elmo.sendMessage(f"game::end")
        
        else:
            self.changePlayer()

            time.sleep(3)

            emotion = emotions[self.move]
            self.elmo.sayEmotion(emotion)

            time.sleep(2)

            accuracy = self.analyseEmotion()
            self.elmo.sendMessage(f"accuracy::{accuracy}")

            time.sleep(1)

            if self.player == 1 or (self.player == 2 and not self.attention):
                self.giveFeedback(accuracy)

            self.move += 1

    def playGame(self):
        self.elmo.playGame() # log message to start the game
        self.elmo.movePan(0) # look to the center
        self.elmo.introduceGame()

        time.sleep(16)

        while self.status == 1 and not self.restart_flag:
            self.elmo.sendMessage("game::loop")
            time.sleep(4)
            self.playerMove()

        if self.status == 2:
            self.elmo.movePan(0) # look to the center
            self.elmo.endGame()

            # select winner and congrats
            winner = max(self.points, key=self.points.get)
            self.elmo.sendMessage(f"winner::{winner}")
            if winner == "1":
                self.elmo.moveLeft()
            else:
                self.elmo.moveRight()
            
            time.sleep(2)

            self.elmo.congratsWinner()

        if self.restart_flag:
            self.restart_flag = False
            return  # Exit the function if restart flag is set

    def stopGame(self):
        self.restart_flag = True

    def restartGame(self):
        self.move = 0
        self.player = 1
        self.points = {"1": 0, "2": 0}
        self.status = 0
        self.restart_flag = False 