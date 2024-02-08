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
        self.attention = 0 # 0: both players receive feedback, 1: just player 1 receive feedback

        # Game thread
        self.game_thread = None
        self.restart_flag = False

    def setStatus(self, status):
        self.status = status

    def setAttention(self):
        self.attention = not self.attention

    def getAttention(self):
        return self.attention

    def change_player(self):
        self.player = self.move % 2 + 1
        if (self.player == 1):
            self.elmo.moveLeft()
        else:
            self.elmo.moveRight()

    def analyse_emotion(self):
        frame = self.elmo.takePicture()
        emotion = emotions[self.move]
        accuracy = self.elmo.analysePicture(frame, emotion)
        accuracy = round(accuracy) if accuracy else 0

        return accuracy
    
    def give_feedback(self, accuracy):
        if accuracy < 50:
            face = random.choice(bad_face)
        elif accuracy < 80:
            face = random.choice(good_face)
        else:
            face = random.choice(awesome_face)

        self.elmo.setImage(face)
        self.elmo.playSound(feedback_sounds[face])

    def player_move(self):
        global status

        if move > len(emotions):
            self.elmo.movePan(0)
            self.elmo.endGame()
            status = 2 # end game
        
        else:
            self.change_player()

            time.sleep(3)

            emotion = emotions[move]
            self.elmo.sayEmotion(emotion)

            time.sleep(2)

            accuracy = self.analyse_emotion()

            if self.player == 1 or (self.player == 2 and self.attention):
                self.give_feedback(accuracy)

            move += 1

    def play_game(self):
        self.elmo.movePan(0) # look to the center
        self.elmo.introduceGame()
        self.elmo.playGame() # log message to start the game
    
        while self.status == 1 and not self.restart_flag:
            self.player_move()
            time.sleep(2)

        if self.status == 2:
            self.elmo.movePan(0) # look to the center
            self.elmo.endGame()

            # select winner and congrats
            winner = max(self.points, key=self.points.get)
            if winner == "1":
                self.elmo.moveLeft()
            else:
                self.elmo.moveRight()
            
            time.sleep(2)
            self.elmo.congratsWinner()

        if self.restart_flag:
            self.restart_flag = False
            return  # Exit the function if restart flag is set

    def stop_game(self):
        self.restart_flag = True

    def restart_game(self):
        self.move = 0
        self.player = 1
        self.points = {"1": 0, "2": 0}
        self.status = 0