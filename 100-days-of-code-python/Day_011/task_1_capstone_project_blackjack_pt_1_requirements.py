# Capstone Project - Blackjack Part 1

'''
Understanding Project Requirements
------------------------------
Rules:
- The deck is unlimited in size.
- There are no jokers.
- The Jack/Queen/King all count as 10.
- The Ace can count as 11 or 1.
- The cards in the list have equal probability of being drawn.
- Cards are not removed from the deck as they are drawn.
- The computer is the dealer.
- whoever has the highest score without going over 21 wins.

- The game starts by dealing two cards to the player and two cards to the dealer.
- The player only sees one of the dealer's cards.
- The player is asked whether they want to draw another card (hit) or pass (stand).
- If the player goes over 21 they bust and lose the game.
- After the player stands, it's the dealer's turn. The dealer draws cards until their score is 17 or higher.
- The scores are then compared to determine the winner.
'''
# TODO 1: Create a function to calculate the card value
# - Handle number cards (2-10) as their face value
# - Handle face cards (J, Q, K) as 10
# - Handle Ace as 11 or 1 based on the hand total

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
