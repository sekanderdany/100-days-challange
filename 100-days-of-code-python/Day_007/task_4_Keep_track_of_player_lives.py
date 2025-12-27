# TODO-1 - Create live variable to keep track of number of lives left. Set to 6 at start of the game.
# TODO-2 - If guess is not a letter in the chosen_word, then reduce '
# TODO-3 - Print the ASCII art from 'stages' that corresponds to the current number of lives the user has remaining.
import random

# hangman ascii art array
stages = [
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
         |
         |
         |
    =========
    """,
    """
     +---+
     |   |
         |
         |
         |
         |
    =========
    """,
]

word_list = ["ardvark", "baboon", "camel"]

chosen_word = random.choice(word_list)

print(chosen_word)

placeholder = ""
word_length = len(chosen_word)

for position in range(word_length):
    placeholder += "_"

print(placeholder)

correct_letters = []

lives = 6  # total lives
game_over = False

while not game_over:
    display = ""
    guess = input("Guess a letter: ").lower()

    for letter in chosen_word:
        if letter == guess:
            display += letter
            correct_letters.append(letter)
        elif letter in correct_letters:
            display += letter
        else:
            display += "_"
    print(display)
    if guess not in chosen_word:
        lives -= 1
        print(f"You lost a life. Lives remaining: {lives}")
        if lives == 0:
            game_over = True
            print("You lost all your lives. Game over!")
    
    if "_" not in display:
        game_over = True
        print("You won!")

    print(stages[lives])