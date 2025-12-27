# TODO-1 - Using while loop to let user guess again if they haven't got all the letters.
# TODO-2 - Change the for loop so that you keep the previous correct guesses in the placeholder.

import random

word_list = ["ardvark", "baboon", "camel"]

chosen_word = random.choice(word_list)

print(chosen_word)

placeholder = ""
word_length = len(chosen_word)

for position in range(word_length):
    placeholder += "_"

print(placeholder)

correct_letters = []

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
    
    if "_" not in display:
        game_over = True
        print("You won!")