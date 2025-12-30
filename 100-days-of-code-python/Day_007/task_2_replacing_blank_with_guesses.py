# TODO-1 - Create a placeholder variable to store the 'blanks' that will replace
# the letters in the chosen_word. For example, if the chosen_word is "apple",
# the placeholder should be "_____" with 5 underscores.
# TODO-2 - Ask the user to guess a letter and assign their answer to a variable

import random

word_list = ["aardvark", "baboon", "camel"]

chosen_word = random.choice(word_list)

print(chosen_word)

placeholder = ""
word_length = len(chosen_word)

for position in range(word_length):
    placeholder += "_"

print(placeholder)

guess = input("Guess a letter: ").lower()

display = ""

for letter in chosen_word:
    if letter == guess:
        display += letter
    else:
        display += "_"

print(display)