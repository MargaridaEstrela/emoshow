import threading
import random
import time

# List of emotions to analyse
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise"]

# Feedback reactions
bad_face = [
    "cry",
    "confused",
    "anger",
]
good_face = [
    "normal",
    "rolling_eyes",
    "thinking",
]
awesome_face = [
    "lovely",
    "images/simon_images/stars.gif",
    "blush",
]

# Feedback sounds for each reaction
feedback_sounds = {
    "cry": "cry.wav",
    "confused": "confused.wav",
    "anger": "anger.wav",
    "normal": "normal.wav",
    "rolling_eyes": "rolling_eyes.wav",
    "thinking": "thinking.wav",
    "lovely": "lovely.wav",
    "images/simon_images/stars.gif": "stars.wav",
    "blush": "blush.wav",
}


class SimonSays:

    def __init__(self, elmo):
        self.elmo = elmo  # Elmo robot
        self.move = 0  # Current move
        self.player = 1  # Current player
        self.points = {"1": 0, "2": 0}  # Points of each player
        self.status = 0  # 0: reset, 1: playing, 2: end game
        self.attention = 1  # 0: unequal attention, 1: equal attention

        # Game thread
        self.game_thread = None
        self.restart_flag = False

    def set_status(self, status):
        self.status = status

    def set_attention(self, attention):
        self.attention = attention

    def get_status(self):
        return self.status

    def get_attention(self):
        return self.attention

    def toggle_attention(self):
        self.set_attention(not self.attention)
        self.elmo.send_message(f"attention::{self.attention}")

    def change_player(self):
        self.player = self.move % 2 + 1
        self.elmo.send_message(f"player::{self.player}")
        self.elmo.send_message(f"move::{self.move}")
        if self.player == 1:
            self.elmo.move_left()  # Look at player 1
        else:
            self.elmo.move_right()  # Look at player 2

    def analyse_emotion(self):
        frame = self.elmo.take_picture()
        emotion = emotions[self.move]
        accuracy = self.elmo.analyse_picture(frame, emotion)
        accuracy = round(accuracy) if accuracy else 0

        return accuracy

    def give_feedback(self, accuracy):
        if accuracy < 50:
            face = random.choice(bad_face)
        elif accuracy < 80:
            face = random.choice(good_face)
        else:
            face = random.choice(awesome_face)

        self.elmo.set_image(face)
        self.elmo.play_sound(feedback_sounds[face])

    def player_move(self):
        if self.move == len(emotions):
            self.status = 2  # End game
            self.elmo.send_message(f"game::end")

        else:
            self.change_player()

            time.sleep(3)

            emotion = emotions[self.move]

            self.elmo.say_emotion(emotion)
            self.logger.log_message(f"emotion::{emotion}")
            time.sleep(2)

            accuracy = self.analyse_emotion()
            self.elmo.send_message(f"accuracy::{accuracy}")

            time.sleep(1)

            if self.player == 1 or (self.player == 2 and not self.attention):
                self.give_feedback(accuracy)

            self.move += 1

    def play_game(self):
        self.elmo.play_game()
        self.elmo.move_pan(0)  # Look in the middle
        self.elmo.introduce_game()

        time.sleep(16)

        while self.status == 1 and not self.restart_flag:
            self.elmo.send_message("game::loop")
            time.sleep(4)
            self.player_move()

        if self.status == 2:
            self.elmo.move_pan(0)  # Look in the middle
            self.elmo.end_game()

            # select winner and congrats
            winner = max(self.points, key=self.points.get)
            self.elmo.send_message(f"winner::{winner}")
            if winner == "1":
                self.elmo.move_left()  # Look at player 1
            else:
                self.elmo.move_right()  # Look at player 2

            time.sleep(2)

            self.elmo.congrats_winner()

        if self.restart_flag:
            self.restart_flag = False
            return

    def stop_game(self):
        self.restart_flag = True

    def restart_game(self):
        self.move = 0
        self.player = 1
        self.points = {"1": 0, "2": 0}
        self.status = 0
        self.restart_flag = False
