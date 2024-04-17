import random
import time
import cv2

from deepface import DeepFace

# List of emotions to analyse
emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

transitions = ["alright", "checkpoint", "dont_blink", "feeling_inspired", 
                "get_ready", "just_checking", "make_us_glad", "next_player_turn", 
                "one_emotion_down", "say_cheese", "showtime", "next_challenge", 
                "lets_go", "surprise_me"]

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
        feedback (boolean): The feedback mode (False: unequal feedback, True: equal feedback).
        remaining_transitions (list): The remaining transitions between moves.
        logger (object): The logger object for logging messages.
        game_thread (object): The game thread.
        restart_flag (bool): Flag indicating if the game should be restarted.

    Methods:
        set_status(status): Sets the status of the game.
        set_attention(attention): Sets the attention mode.
        get_status(): Returns the status of the game.
        get_attention(): Returns the attention mode.
        toggle_attention(): Toggles the attention mode.
        shuffle_emotions(): Shuffles the emotions for each player.
        dynamic_intro(): Plays the dynamics for the intro of the game.
        dynamic_conclusion(): Plays the dynamics for the conclusion of the game.
        change_player(): Changes the current player.
        center_player(): Centers the player in the frame.
        play_transition(): Play a transition sound while changing player  
        take_picture(): Takes a picture sequence.
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
        self.remaining_transitions = transitions # Transitions between moves

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

    def dynamic_intro(self):
        """
        Plays the dynamics for the intro of the game.
        """
        self.elmo.play_sound("introduction_1.wav")
        time.sleep(4.12)
        self.elmo.move_left()
        time.sleep(2) 
        self.elmo.play_sound("introduction_2.wav") 
        time.sleep(7)
        
        # Show icons
        self.elmo.move_pan(0)
        time.sleep(2)
        self.elmo.play_sound("introduction_3.wav")
        time.sleep(2.8)
        self.elmo.set_icon("3.png")
        time.sleep(1)
        self.elmo.set_icon("2.png")
        time.sleep(0.5)
        self.elmo.set_icon("1.png")
        time.sleep(0.7)
        self.elmo.set_icon("camera.png")
        time.sleep(1)
        self.elmo.set_icon("slow_loading.gif")
        time.sleep(6)  
        self.elmo.set_icon("black.png")
        
        self.elmo.move_right()
        time.sleep(2)
        self.elmo.play_sound("introduction_4.wav")
        time.sleep(5)
        
        self.elmo.move_pan(0)
        time.sleep(2)
        self.elmo.play_sound("introduction_5.wav")
        time.sleep(6)
        
    def dynamic_conclusion(self):
        """
        Plays the dynamics for the conclusion of the game.
        """
        self.elmo.move_pan(0)
        time.sleep(2)
        
        self.elmo.set_icon("heart.png")
        self.elmo.play_sound("conclusion_1.wav")
        time.sleep(2.5)
        
        self.elmo.move_left()
        time.sleep(2)
        self.elmo.play_sound("conclusion_2.wav")
        time.sleep(8.5)
        
        self.elmo.move_right()
        time.sleep(2)
        self.elmo.play_sound("conclusion_3.wav")
        time.sleep(7)
        
        self.elmo.move_pan(0)
        time.sleep(2)
        self.elmo.play_sound("conclusion_4.wav")
        time.sleep(3)
        
        # Joke Time        
        self.elmo.move_left()
        time.sleep(2)
        self.elmo.play_sound("joke_1.wav")
        time.sleep(4)
        
        self.elmo.move_right()
        time.sleep(2)
        self.elmo.play_sound("joke_2.wav")
        time.sleep(4)
        
        self.elmo.move_pan(0)
        time.sleep(2)
        self.elmo.play_sound("joke_3.wav")
        time.sleep(14)
        
        self.elmo.set_icon("black.png") # Default icon

    def center_player(self):
        """
        Centers the player's face in the frame by adjusting the robot's pan and 
        tilt angles. If no faces detected, returns and continues the game.
        """
        frame = self.elmo.grab_image()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))

        if len(faces) == 0:
            self.logger.log_error("Cannot center player. No faces detected.")
            return

        # Get frame center and dimensions
        frame_width, frame_height = frame.shape[1], frame.shape[0]
        frame_center_x = frame_width / 2
        frame_center_y = frame_height / 2

        # Extract face bounding box
        x, y, w, h = faces[0]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Calculate adjustments
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
        time.sleep(2)
        self.elmo.move_tilt(new_tilt_angle)

        # Save changes
        self.logger.log_message(f"Horizontal adjustment: {int(horizontal_adjustment/3)}")
        self.logger.log_message(f"Vertical adjustment: {int(vertical_adjustment/3)}")
        
    def change_player(self):
        """
        Changes the current player.
        """
        self.player = self.move % 2 + 1
        
        if (self.first_player == 2):
            if (self.player == 1):
                self.player = 2
            else:
                self.player = 1
        
        print("player: ", self.player)
        self.logger.log_message(f"Player: {self.player}")
        self.logger.log_message(f"Move: {self.move}")
        
        if self.player == 1:
            self.elmo.move_left()
        else:
            self.elmo.move_right()
        
        time.sleep(1)
        
        self.center_player() # center player in the frame if needed
    
    def play_transition(self):
        """
        Play a transition sound while is changing player 
        """
        transition = random.choice(self.remaining_transitions)
        self.remaining_transitions.remove(transition)
        self.elmo.play_sound(f"transitions/{transition}.wav")
    
    def take_picture(self):
        """
        Plays a sound, displays a countdown sequence of icons (3, 2, 1), and 
        captures an image.

        Returns:
            np.ndarray: The captured picture.
        """
        self.elmo.play_sound("picture.wav")
        time.sleep(0.1)

        # show 3, 2, 1 and take a picture
        self.elmo.set_icon("3.png")
        time.sleep(1)
        self.elmo.set_icon("2.png")
        time.sleep(0.5)
        self.elmo.set_icon("1.png")
        time.sleep(0.7)
        self.elmo.set_icon("camera.png")

        return self.elmo.grab_image()
    
    def analyse_emotion(self):
        """
        Analyzes the emotion of the current move.

        Returns:
            int: The accuracy of the emotion analysis.
        """
        frame = self.take_picture()
        
        # Save frames to analyze later
        cv2.imwrite(f"frames/frame_{self.move}.png", frame) 
        
        time.sleep(1.5)
        self.elmo.set_icon("slow_loading.gif") # Set loading icon
        time.sleep(6)    
        self.elmo.set_icon("black.png") # After progress gif ended
        
        player_move = self.get_player_move();
        emotion = self.get_player_emotions()[player_move]
        
        # DeepFace analysis
        try:
            face_analysis = DeepFace.analyze(frame, actions=["emotion"])
            self.logger.log_message(face_analysis[0])
            accuracy = round(face_analysis[0]["emotion"][emotion])
        except Exception as e:
            self.logger.log_error(e)
            accuracy = 0

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
            self.elmo.set_image("star.png")
            self.elmo.play_sound("good_feedback.wav")

        time.sleep(5)
        
        self.elmo.set_image("normal.png") # Set default image 

    def player_move(self):
        """
        Performs a move by the player.
        """
        self.elmo.set_image("normal.png") # Set default image

        if self.move == 2*len(emotions):
            self.status = 2  # Game Over
        else:
            self.change_player()
            
            if (self.move == 0):
                self.elmo.play_sound("first_emotion.wav")
                time.sleep(5)
            
            else:
                self.play_transition()
                time.sleep(4)

            player_move = self.get_player_move()
            emotion = self.shuffled_emotions[str(self.player)][player_move]

            # Say emotion
            self.logger.log_message(f"Emotion: {emotion}")
            self.elmo.play_sound(f"emotions/{emotion}.wav")
            self.elmo.set_image(f"emotions/{emotion}.png")

            time.sleep(3)
            
            # Take a picture and analyse emotion
            accuracy = self.analyse_emotion() 
            self.logger.log_message(f"Accuracy: {accuracy}")
            self.points[str(self.player)] += accuracy
            print("accuracy: ", accuracy)
            print(self.points)
            self.logger.log_message(f"Player: {str(self.player)}, points: \
                {self.points[str(self.player)]}")

            if self.player == 1 or (self.player == 2 and self.feedback):
                self.give_feedback(accuracy)
            else:
                # Excluded participant only receive feedback on 2nd and 6th emotion
                if not self.feedback and (self.move == 3 or self.move == 11):
                    self.give_feedback(accuracy)
                else:
                    time.sleep(3)

            self.move += 1

    def play_game(self):
        """
        Starts the game.
        """
        self.elmo.set_image("normal.png")
        self.elmo.set_icon("black.png")
        self.elmo.move_pan(0)  # Look in the middle

        time.sleep(2)
        
        self.dynamic_intro()

        self.first_player = random.randint(1, 2)
        
        self.logger.log_message(f"First player: {self.first_player}")
        print("first player: ", self.first_player)
        
        if not self.feedback:
            self.excluded_player = random.randint(1, 2)
            self.logger.log_message(f"Excluded player: {self.excluded_player}")
            print("excluded player: ", self.excluded_player)
            
        self.shuffle_emotions()
        
        while self.status == 1 and not self.restart_flag:
            self.logger.log_message("New emotion...")
            self.player_move()

        if self.status == 2:
            self.elmo.set_image("normal.png")
            self.elmo.move_pan(0)  # Look in the middle
            self.elmo.set_icon("fireworks.gif")
            self.elmo.play_sound("end_game_song.wav")

            time.sleep(3)

            # Find winner
            winner = int(max(self.points, key=self.points.get))
            print(winner)
            self.logger.log_message(self.points)
            self.logger.log_message(f"winner::{winner}")
            
            if winner == 1:
                self.elmo.move_left()
            else:
                self.elmo.move_right()

            time.sleep(2)
            self.elmo.play_sound("winner.wav") # Congrats winner
            time.sleep(6)
            
            self.dynamic_conclusion() # Thanks players for playing

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
        self.remaining_transitions = transitions
        self.elmo.set_image("normal.png")
        self.elmo.set_icon("black.png")
