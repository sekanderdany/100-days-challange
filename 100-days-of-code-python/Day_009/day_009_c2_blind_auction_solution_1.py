''' 
Requirements
-------------

- On initial screen The program will show-
## Welcome to the secret auction program.
What's your name? :
What's your bid? :

- after the input the program will ask-
# Are there any other bidders? Type 'yes' or 'no'.

- if yes then the program will clear the screen and ask the same question.
- if no then the program will show the highest bidders information
'''

print("Welcome to the secret auction program.")

next_bidder = True

highest_bid = 0
winner = ""

auction = {}


print(auction)


while next_bidder == True:
    name = input("What's your name? :")
    bid = int(input("What's your bid? :"))
    ask_bidder = input("Are there any other bidders? Type 'yes' or 'no'.")
    auction[name] = bid
    if bid > highest_bid:
        highest_bid = bid
        winner = name
    if ask_bidder == "no":
        next_bidder = False
    elif ask_bidder == "yes":
        print("\n" * 50)
    else:
        print("Invalid input. Exiting the auction.")
        break

print(f"The winner is {winner} with a bid of ${highest_bid}.")