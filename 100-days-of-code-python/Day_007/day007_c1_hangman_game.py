# TODO-1 - Create live variable to keep track of number of lives left. Set to 6 at start of the game.
# TODO-2 - If guess is not a letter in the chosen_word, then reduce '
# TODO-3 - Print the ASCII art from 'stages' that corresponds to the current number of lives the user has remaining.
import random

from day007_c1_f1_hangman_words import word_list

from day007_c1_f2_hangman_art import stages, logo

lives = 6  # total lives

# hangman ascii art array

print(logo)
chosen_word = random.choice(word_list)

placeholder = ""
word_length = len(chosen_word)

for position in range(word_length):
    placeholder += "_"

correct_letters = []


game_over = False

print(placeholder)

while not game_over:

    print(f"****************You have {lives}/6 Lives Left****************")
    display = ""
    guess = input("Guess a letter: ").lower()

    if guess in correct_letters:
        print(f"You've already guessed {guess}")

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
        print(f"OH Noo! You have chosen {guess}, that's not in the word. You lose a life.")
        if lives == 0:
            game_over = True
            print(f"*-^-;._.;-^**-^-;._.;-^*You lost! The word was {chosen_word}.*^-;._.;-^**-^-;._.;-^*")
    
    if "_" not in display:
        game_over = True
        print("*-^-;._.;-^**-^-;._.;-^*You won!*-^-;._.;-^**-^-;._.;-^*")

    print(stages[lives])