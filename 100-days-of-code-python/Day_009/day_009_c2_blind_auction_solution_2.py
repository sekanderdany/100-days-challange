'''
TODO 1: Ask the user for input
TODO 2: Save data into dictionary {name: prince}
TODO 3: Whether if new bids needs to be added
TODO 4: Compare the bids in dictionary to find highest bidder
''' 

import day_009_c2_art

print(day_009_c2_art.logo)
print("Welcome to the secret auction program.")

#TODO 1: Ask the user for input
#TODO 2: Save data into dictionary {name: prince}
#TODO 3: Whether if new bids needs to be added

bids = {}
continue_bidding = True

while continue_bidding:
    name = input("What's your name? :")
    price = int(input("What's your bid? :"))
    bids[name] = price
    should_continue = input("Are there any other bidders? Type 'yes' or 'no'.").lower()
    if should_continue == "no":
        continue_bidding = False
    elif should_continue == "yes":
        print("\n" * 50)


#TODO 4: Compare the bids in dictionary to find highest bidder

def find_highest_bidder(bidding_dictionary):
    highest_bid = 0
    winner = ""
    for bidder in bidding_dictionary:
        bid_amount = bidding_dictionary[bidder]
        if bid_amount > highest_bid:
            highest_bid = bid_amount
            winner = bidder
    print(f"The winner is {winner} with a bid of ${highest_bid}.")

find_highest_bidder(bids)