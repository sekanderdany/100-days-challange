# Number Guessing game
'''
Instructions
You are going to write a number guessing game. The game will work as follows:
- There will be a variable called `answer` which is set to a number between 1 and 100. This is the number the player has to guess.
- The player will have 10 attempts for 'easy' difficulty and 5 attempts for 'hard' difficulty to guess the number.
- If the player guesses the number correctly, they win the game.
- If the player guesses incorrectly, they will be told whether their guess is too high or too low and they will lose an attempt.
- If the player runs out of attempts, they lose the game.
'''

import random


def number_guessing_game():
    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")

    answer = random.randint(1, 100)
    attempts = 0

    difficulty = input("Choose a difficulty. Type 'easy' or 'hard': ").lower()
    if difficulty == 'easy':
        attempts = 10
    elif difficulty == 'hard':
        attempts = 5
    else:
        print("Invalid difficulty choice. Please restart the game.")
        return

    while attempts > 0:
        print(f"You have {attempts} attempts remaining to guess the number.")
        guess = int(input("Make a guess: "))

        if guess == answer:
            print(f"You got it! The answer was {answer}.")
            return
        elif guess < answer:
            print("Too low.")
        else:
            print("Too high.")

        attempts -= 1

        if attempts == 0:
            print(
                f"You've run out of guesses. The number was {answer}. You lose.")
        else:
            print("Guess again.")


number_guessing_game()
