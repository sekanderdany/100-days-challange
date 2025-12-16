import random
rock = """
    _______
---'   ____)
      (_____)
      (_____)
      (____)
---.__(___)
"""

paper = """
     _______
---'    ____)____
           ______)
          _______)
         _______)
---.__________)
"""

scissors = """
    _______
---'   ____)____
          ______)
       __________)
      (____)
---.__(___)
"""


choice = input("what do you choose? Type 0 for Rock, 1 for Paper or 2 for Scissors.\n")

if choice not in ["0", "1", "2"]:
    print("Invalid input! You lose!")
else:
    user_choice = int(choice)
    computer_choice = random.randint(0, 2)

    choices = ["Rock", "Paper", "Scissors"]
    ascii_art = [rock, paper, scissors]

    print(f"You chose: {choices[user_choice]}")
    print(ascii_art[user_choice])
    print(f"Computer chose: {choices[computer_choice]}")
    print(ascii_art[computer_choice])

    if user_choice == computer_choice:
        print("It's a draw!")
    elif (user_choice == 0 and computer_choice == 2) or \
         (user_choice == 1 and computer_choice == 0) or \
         (user_choice == 2 and computer_choice == 1):
        print("You win!")
    else:
        print("You lose!")