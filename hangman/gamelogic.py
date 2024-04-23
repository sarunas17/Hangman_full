import random
from flask_login import current_user
from hangman.mongo_file import MongoCRUD, database
from datetime import datetime
from flask import session

sport_words = ["football", "basketball", "tennis", "soccer", "swimming", "golf", "boxing", "cricket"]
food_words = ["pizza", "hamburger", "sushi", "pasta", "steak", "salad", "sandwich", "chocolate"]
country_words = ["lithuania", "france", "canada", "brazil", "china", "india", "germany", "japan"]
max_guesses = 10
max_mistakes = 6

class Hangman:
    def __init__(self) -> None:
        topics = ["sport", "food", "countries"]
        self.topic = random.choice(topics)
        if self.topic == "sport":
            self.word_to_guess = random.choice(sport_words)
        elif self.topic == "food":
            self.word_to_guess = random.choice(food_words)
        elif self.topic == "countries":
            self.word_to_guess = random.choice(country_words)

        self.max_guesses = max_guesses
        self.max_mistakes = max_mistakes
        self.incorrect_guesses = 0
        self.guessed_letters = []
       

    def display_word(self) -> str:
        guessed_letters_display = [letter if letter in self.guessed_letters else '_' for letter in self.word_to_guess]
        display_string = ' '.join(guessed_letters_display)
        return display_string.upper()
    

    def display_topic(self) ->str:
        return self.topic.upper()
    

    def display_guessed_letters(self) -> str:
        return ", ".join(letter.upper() for letter in self.guessed_letters)
    

    def validate_input(self, guess: str) -> bool:
        try:
            if not guess.isalpha() or len(guess) != 1 and len(guess) != len(self.word_to_guess):
                return True
        except Exception as e:
            print("Error:", e)
    

    def is_already_checked(self, guess: str) -> bool:
        if guess.isalpha() and len(guess) == 1 or len(guess) == len(self.word_to_guess):
            if guess in self.guessed_letters:
                return True
     
    

    def check_guess(self, guess: str) -> bool:
        try:
            self.max_guesses -= 1
            if len(guess) == 1 and guess.isalpha():
                if guess in self.word_to_guess:
                    self.guessed_letters.append(guess)
                    return True
                else:
                    self.incorrect_guesses += 1
                    self.guessed_letters.append(guess)
                    return False
            elif len(guess) == len(self.word_to_guess):
                if guess == self.word_to_guess:
                    for letter in guess:
                        self.guessed_letters.append(letter)
                        self.guessed_letters = list(set(self.guessed_letters))
                    return True
                else:
                    self.incorrect_guesses += 1
                    return False
        except Exception as e:
            print("Error:", e)
            
   
    def is_game_over(self) -> bool:
        if self.incorrect_guesses >= self.max_mistakes:
            if current_user.is_authenticated:
                document = {"user_email": current_user.email, "mistakes_made": self.incorrect_guesses, "guesses_made": 10 - self.max_guesses, "guessed_letters": self.guessed_letters, "word_to_guess": self.word_to_guess, "status": "lost", "timestamp": datetime.now()}
                database.insert_one_document(document)
            print("You have reached the maximum number of mistakes. Game over!")
            return True
        elif set(self.word_to_guess).issubset(set(self.guessed_letters)):
            if current_user.is_authenticated:
                document = {"user_email": current_user.email, "mistakes_made": self.incorrect_guesses, "guesses_made": 10 - self.max_guesses, "guessed_letters": self.guessed_letters, "word_to_guess": self.word_to_guess, "status": "win", "timestamp": datetime.now()}
                database.insert_one_document(document)
            print("Congratulations! You guessed the word correctly!")
            return True
        elif self.max_guesses == 0:
            if current_user.is_authenticated:
                document = {"user_email": current_user.email, "mistakes_made": self.incorrect_guesses, "guesses_made": 10 - self.max_guesses, "guessed_letters": self.guessed_letters,"word_to_guess": self.word_to_guess, "status": "lost", "timestamp": datetime.now()}
                database.insert_one_document(document)
            print("You have used all your guesses. Game over!")
            return True
        else:
            return False
        
 
    def to_dict(self) -> dict:
        return {
            "word_to_guess": self.word_to_guess,
            "topic": self.topic,
            "max_guesses": self.max_guesses,
            "max_mistakes": self.max_mistakes,
            "incorrect_guesses": self.incorrect_guesses,
            "guessed_letters": self.guessed_letters
    }

    @classmethod
    def from_dict(cls, data: dict) -> "Hangman":
        hangman = cls()
        hangman.word_to_guess = data["word_to_guess"]
        hangman.topic = data["topic"]
        hangman.max_guesses = data["max_guesses"]
        hangman.max_mistakes = data["max_mistakes"]
        hangman.incorrect_guesses = data["incorrect_guesses"]
        hangman.guessed_letters = data["guessed_letters"]
        return hangman
        