import random
import time
import cv2

# List of emotions to analyse
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

# Load the Haar Cascade model
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 
                                        "haarcascade_frontalface_default.xml")


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
        center_player(): Centers the player in the frame.
        play_transition(): Play a transition sound while changing player  
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
    
    def get_player_emotions(self):
        """
        Returns the list of shuffled emotions of the current player.

        Returns:
            list: The current player move.
        """
        return self.shuffled_emotions[str(self.player)]

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

    def center_player(self):
        """
        Centers the player in the frame, adjusting pan and tilt angles, with 
        dead zones on all sides. If no faces detected, returns and continues 
        the game.
        """
        frame = self.elmo.grab_image()
        cv2.imwrite("pre_centered_player.png", frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))

        if len(faces) == 0:
            self.logger.log_error("No faces detected. Cannot center player")
            return

        # Get frame center and dimensions
        frame_width, frame_height = frame.shape[1], frame.shape[0]
        frame_center_x = frame_width / 2
        frame_center_y = frame_height / 2

        # Extract face bounding box
        x, y, w, h = faces[0]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imwrite("centered_player.png", frame)  # Save image

        # Calculate adjustments
        horizontal_adjustment = 0
        vertical_adjustment = 0
        # if not is_in_center_zone:
        horizontal_adjustment = ((frame_center_x - (x + w / 2)) // 4)
        vertical_adjustment = ((frame_center_y - (y + h / 2)) // 8)

        # Get default pan and tilt angles
        if self.player == 1:
            default_pan = self.elmo.get_default_pan_left()
            default_tilt = self.elmo.get_default_tilt_left()
        else:
            default_pan = self.elmo.get_default_pan_right()
            default_tilt = self.elmo.get_default_tilt_right()
        
        new_pan_angle = default_pan + int(horizontal_adjustment/3)
        new_tilt_angle = default_tilt - int(vertical_adjustment/3)
        
        # Check if values are within bounds
        new_pan_angle = self.elmo.check_pan_angle(new_pan_angle)
        new_tilt_angle = self.elmo.check_tilt_angle(new_tilt_angle)
        
        # Update default values
        if self.player == 1:
            self.elmo.set_default_pan_left(new_pan_angle)
            self.elmo.set_default_tilt_left(new_tilt_angle)
        else:
            self.elmo.set_default_pan_right(new_pan_angle)
            self.elmo.set_default_tilt_right(new_tilt_angle)
            
        self.elmo.move_pan(new_pan_angle)
        time.sleep(2)  # Adjust delay as needed
        self.elmo.move_tilt(new_tilt_angle)

        # Save changes
        self.logger.log_message(f"Horizontal adjustment: {horizontal_adjustment}")
        self.logger.log_message(f"Vertical adjustment: {vertical_adjustment}")
        
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
        
        time.sleep(3)
        
        self.center_player() # center player in the frame if needed
    
    def play_transition(self):
        """
        Play a transition sound while is changing player 
        """
        transitions = ["alright", "checkpoint", "dont_blink", 
                        "feeling_inspired", "get_ready", "just_checking", 
                        "make_us_glad", "next_player_turn", "one_emotion_down",
                        "say_cheese", "showtime", "top_that"]
        
        transition = random.choice(transitions)
        self.elmo.play_sound(f"transitions/{transition}.wav")
        
    def analyse_emotion(self):
        """
        Analyzes the emotion of the current move.

        Returns:
            int: The accuracy of the emotion analysis.
        """
        frame = self.elmo.take_picture()
        cv2.imwrite(f"frames/frame_{self.move}.png", frame)
        
        time.sleep(1.5)
        
        self.elmo.set_icon("slow_loading.gif") # Set loading icon
        
        time.sleep(6)
        
        self.elmo.set_icon("black.png") # After progress gif ended
        
        player_move = self.get_player_move();
        emotion = self.get_player_emotions()[player_move]
        print(emotion)
        
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
            self.elmo.set_image("cry.png")
            self.elmo.play_sound("bad_feedback.wav")
        else:
            self.elmo.set_image("images/emotions_game/stars.gif")
            self.elmo.play_sound("good_feedback.wav")

        time.sleep(5)
        
        self.elmo.set_image("normal.png") # Set default image 

    def player_move(self):
        """
        Performs a move by the player.
        """
        self.elmo.set_image("normal.png") # Set default image
        print("p[layer move]")

        if self.move == 2*len(emotions):
            self.status = 2  # End game
            self.elmo.send_message(f"game::end")
        else:
            self.change_player()
            
            if (self.move == 0):
                self.elmo.play_sound("first_emotion.wav")
                time.sleep(4)
            
            else:
                self.play_transition()
                time.sleep(4)

            player_move = self.get_player_move()
            emotion = self.shuffled_emotions[str(self.player)][player_move]

            self.elmo.say_emotion(emotion)
            self.elmo.set_image(f"emotions/{emotion}.png")
            self.logger.log_message(f"emotion::{emotion}")

            time.sleep(3)
            
            # Take a picture and analyse emotion
            accuracy = self.analyse_emotion() 
            self.elmo.send_message(f"accuracy::{accuracy}")
            self.points[str(self.player)] += accuracy

            if self.player == 1 or (self.player == 2 and self.feedback):
                self.give_feedback(accuracy)
            else:
                time.sleep(3)

            self.move += 1

    def play_game(self):
        """
        Starts the game.
        """
        
        self.elmo.play_game()
        self.elmo.set_image("normal.png")
        self.elmo.set_icon("black.png")
        self.elmo.move_pan(0)  # Look in the middle

        time.sleep(2)
        
        self.elmo.introduce_game()

        time.sleep(34)

        self.shuffle_emotions()

        while self.status == 1 and not self.restart_flag:
            self.elmo.send_message("game::loop")
            self.player_move()

        if self.status == 2:
            self.elmo.set_image("normal.png")
            self.elmo.move_pan(0)  # Look in the middle
            self.elmo.set_icon("fireworks.gif")
            self.elmo.end_game()

            time.sleep(3)

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

            time.sleep(6)
            
            self.elmo.move_pan(0)
            
            time.sleep(3)
            
            self.elmo.set_icon("heart.png")
            self.elmo.play_sound("conclusion.wav")
            
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
