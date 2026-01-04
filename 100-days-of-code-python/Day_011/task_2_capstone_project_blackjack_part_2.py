# Capstone Project - Blackjack Part 2

# TODO 1: Create a function to calculate the card value
# - Handle number cards (2-10) as their face value
# - Handle face cards (J, Q, K) as 10
# - Handle Ace as 11 or 1 based on the hand total

cards = {
    "Speades": ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'],
    "Hearts": ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'],
    "Diamonds": ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'],
    "Clubs": ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
}

card_values = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 10,
    'Q': 10,
    'K': 10,
    'A': 11
}


# TODO 2: Create a function to calculate the total score of a hand
# - Sum up all card values
# - Adjust for Aces (convert from 11 to 1 if total exceeds 21)

# TODO 3: Create a function to deal cards
# - Generate random cards from the deck
# - Return a single card or a hand of cards

# TODO 4: Create a function to display the game state
# - Show player's hand and score
# - Show only one dealer card initially
# - Show full dealer hand after dealer's turn

# TODO 5: Create the main game flow
# - Deal 2 cards to player and 2 cards to dealer
# - Display initial hands (hide one dealer card)
# - Player's turn: ask for hit or stand until they stand or bust
# - Check if player busted
# - Dealer's turn: dealer hits until score is 17 or higher
# - Compare scores and determine winner

# TODO 6: Create a function to determine the winner
# - Compare player and dealer scores
# - Handle player bust, dealer bust, tie, and win/loss scenarios
