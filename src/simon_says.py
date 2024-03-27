import random
import time

# List of emotions to analyse
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

# Feedback reactions
bad_face = [
    "cry",
    "confused",
    "anger"
]
good_face = [
    "normal",
    "rolling_eyes",
    "thinking"
]
awesome_face = [
    "lovely",
    "images/simon_images/stars.gif",
    "blush"
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
    "blush": "blush.wav"
}


class SimonSays:
    """
    A class representing the Simon Says game.

    Attributes:
        elmo (object): The Elmo robot.
        logger (object): The logger object for logging messages.
        move (int): The current move.
        player (int): The current player.
        points (dict): The points of each player.
        shuffled_emotions (dict) : The shuffled emotions for each player.
        status (int): The status of the game (0: reset, 1: playing, 2: end game).
        attention (int): The attention mode (0: unequal attention, 1: equal attention).
        game_thread (object): The game thread.
        restart_flag (bool): Flag indicating if the game should be restarted.

    Methods:
        set_status(status): Sets the status of the game.
        set_attention(attention): Sets the attention mode.
        get_status(): Returns the status of the game.
        get_attention(): Returns the attention mode.
        toggle_attention(): Toggles the attention mode.
        shuffle_emotions(): Shuffles the emotions for each player.
        change_player(): Changes the current player.
        analyse_emotion(): Analyzes the emotion of the current move.
        give_feedback(accuracy): Gives feedback based on the accuracy of the emotion analysis.
        player_move(): Performs a move by the player.
        play_game(): Starts the game.
        stop_game(): Stops the game.
        restart_game(): Restarts the game.
    """

    def __init__(self, elmo, logger):
        self.elmo = elmo  # Elmo robot
        self.move = 0  # Current move
        self.player = 1  # Current player
        self.points = {"1": 0, "2": 0}  # Points of each player
        self.shuffled_emotions = {} # Shuffled emotions for each player
        self.status = 0  # 0: reset, 1: playing, 2: end game
        self.feedback = True  # Feedback mode

        self.logger = logger

        # Game thread
        self.game_thread = None
        self.restart_flag = False

    def set_status(self, status):
        """
        Sets the status of the game.

        Args:
            status (int): The status of the game.
        """
        self.status = status

    def set_feedback(self, feedback):
        """
        Sets the feedback mode.

        Args:
            feedback (boolean): The feedback mode.
        """
        self.feedback = feedback

    def get_status(self):
        """
        Returns the status of the game.

        Returns:
            int: The status of the game.
        """
        return self.status

    def get_feedback(self):
        """
        Returns the feedback mode.

        Returns:
            boolean: The feedback mode.
        """
        return self.feedback

    def get_player_move(self):
        """
        Returns the current move of the current player.

        Returns:
            int: The current player move.
        """
        player_move = self.move // 2
        return player_move

    def toggle_feedback(self):
        """
        Toggles the feedback mode.
        """
        self.set_feedback(not self.feedback)
        self.elmo.send_message(f"feedback::{self.feedback}")

    def shuffle_emotions(self):
        """
        Shuffles the emotions for each player.
        """
        self.shuffled_emotions["1"] = emotions.copy()
        self.shuffled_emotions["2"] = emotions.copy()

        random.shuffle(self.shuffled_emotions["1"])
        random.shuffle(self.shuffled_emotions["2"])

        self.logger.log_message(f"[EMOTIONS_1]: {self.shuffled_emotions["1"]}")
        self.logger.log_message(f"[EMOTIONS_2]: {self.shuffled_emotions["2"]}")

    def change_player(self):
        """
        Changes the current player.
        """
        self.player = self.move % 2 + 1
        self.elmo.send_message(f"player::{self.player}")
        self.elmo.send_message(f"move::{self.move}")
        if self.player == 1:
            self.elmo.move_left()  # Look at player 1
        else:
            self.elmo.move_right()  # Look at player 2

    def analyse_emotion(self):
        """
        Analyzes the emotion of the current move.

        Returns:
            int: The accuracy of the emotion analysis.
        """
        frame = self.elmo.take_picture()
        player_move = self.get_player_move();
        emotion = emotions[player_move]
        accuracy = self.elmo.analyse_picture(frame, emotion)
        accuracy = round(accuracy) if accuracy else 0

        if accuracy == 0:
            self.logger.log_error("Face not detected")

        return accuracy

    def give_feedback(self, accuracy):
        """
        Gives feedback based on the accuracy of the emotion analysis.

        Args:
            accuracy (int): The accuracy of the emotion analysis.
        """
        if accuracy < 50:
            face = random.choice(bad_face)
        elif accuracy < 80:
            face = random.choice(good_face)
        else:
            face = random.choice(awesome_face)

        self.elmo.set_image(face)
        self.elmo.play_sound(feedback_sounds[face])
        time.sleep(5)

    def player_move(self):
        """
        Performs a move by the player.
        """
        self.elmo.send_message("image::normal") # Set default image

        if self.move == 2*len(emotions):
            self.status = 2  # End game
            self.elmo.send_message(f"game::end")
        else:
            self.change_player()

            time.sleep(3)

            player_move = self.get_player_move()
            emotion = self.shuffled_emotions[str(self.player)][player_move]

            self.elmo.say_emotion(emotion)
            self.logger.log_message(f"emotion::{emotion}")

            time.sleep(1)

            accuracy = self.analyse_emotion()
            self.elmo.send_message(f"accuracy::{accuracy}")
            self.points[str(self.player)] += accuracy

            time.sleep(2)

            self.elmo.send_message("icon::elmo_idm.png")

            if self.player == 1 or (self.player == 2 and self.feedback):
                print("Receive feedback")
                self.give_feedback(accuracy)

            time.sleep(2)
            self.move += 1

    def play_game(self):
        """
        Starts the game.
        """
        self.elmo.play_game()
        self.elmo.send_message("image::normal")
        self.elmo.send_message("icon::elmo_idm.png")
        self.elmo.move_pan(0)  # Look in the middle

        time.sleep(2)
        
        self.elmo.introduce_game()

        time.sleep(16)

        self.shuffle_emotions()

        while self.status == 1 and not self.restart_flag:
            self.elmo.send_message("game::loop")
            self.player_move()

        if self.status == 2:
            self.elmo.move_pan(0)  # Look in the middle
            self.elmo.end_game()

            time.sleep(4)

            # Select winner and congrats
            winner = max(self.points, key=self.points.get)
            self.logger.log_message(self.points)
            self.logger.log_message(f"winner::{winner}")
            if winner == "1":
                self.elmo.move_left()  # Look at player 1
            else:
                self.elmo.move_right()  # Look at player 2

            time.sleep(2)

            self.elmo.congrats_winner()

            time.sleep(4)

        if self.restart_flag:
            self.restart_flag = False
            return

    def stop_game(self):
        """
        Stops the game.
        """
        self.restart_flag = True

    def restart_game(self):
        """
        Restarts the game.
        """
        self.move = 0
        self.player = 1
        self.points = {"1": 0, "2": 0}
        self.shuffled_emotions = {}
        self.status = 0
        self.restart_flag = False
