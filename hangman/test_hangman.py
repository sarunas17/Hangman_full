import unittest
from gamelogic import Hangman

class HangmanTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Hangman()

    def test_start_game(self):
        self.game.start_game()
        self.assertIsNotNone(self.game.topic)
        self.assertIsNotNone(self.game.word_to_guess)
        self.assertEqual(self.game.max_guesses, 10)
        self.assertEqual(self.game.max_mistakes, 6)
        self.assertEqual(self.game.incorrect_guesses, 0)
        self.assertEqual(self.game.guessed_letters, [])

    def test_display_word(self):
        self.game.word_to_guess = "test"
        self.game.guessed_letters = ['t', 'e']
        self.assertEqual(self.game.display_word(), "T E _ T")

    def test_display_topic(self):
        self.game.topic = "sport"
        self.assertEqual(self.game.display_topic(), "SPORT")

    def test_display_guessed_letters(self):
        self.game.guessed_letters = ['a', 'b', 'c']
        self.assertEqual(self.game.display_guessed_letters(), "A, B, C")

    def test_input_is_valid(self):
        self.assertTrue(self.game.input_is_valid('a'))
        self.assertTrue(self.game.input_is_valid('test'))
        self.assertFalse(self.game.input_is_valid('123'))
        self.assertFalse(self.game.input_is_valid('!@#'))

    def test_is_already_checked(self):
        self.game.guessed_letters = ['a', 'b', 'c']
        self.assertTrue(self.game.is_already_checked('a'))
        self.assertFalse(self.game.is_already_checked('d'))

    def test_check_guess(self):
        self.game.word_to_guess = "test"
        self.assertTrue(self.game.check_guess('t'))
        self.assertFalse(self.game.check_guess('z'))
        self.assertTrue(self.game.check_guess('test'))
        self.assertFalse(self.game.check_guess('wrong'))

    def test_word_guessed_correctly(self):
        self.game.word_to_guess = "test"
        self.game.guessed_letters = ['t', 'e', 's']
        self.assertTrue(self.game.word_guessed_correctly())
        self.game.guessed_letters = ['t', 'e']
        self.assertFalse(self.game.word_guessed_correctly())

    def test_is_game_over(self):
        self.game.incorrect_guesses = 6
        self.assertTrue(self.game.is_game_over())
        self.game.incorrect_guesses = 5
        self.assertFalse(self.game.is_game_over())
        self.game.word_to_guess = "test"
        self.game.guessed_letters = ['t', 'e', 's']
        self.assertTrue(self.game.is_game_over())
        self.game.guessed_letters = ['t', 'e']
        self.assertFalse(self.game.is_game_over())
        self.game.max_guesses = 0
        self.assertTrue(self.game.is_game_over())

   

if __name__ == '__main__':
    unittest.main()
