# Capstone Project - Blackjack Part 2

import random # for TODO 3


# TODO 1: Create a function to calculate the card value
# - Handle number cards (2-10) as their face value
# - Handle face cards (J, Q, K) as 10
# - Handle Ace as 11 or 1 based on the hand total

deck_of_cards = {
    "Speades": ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'],
    "Hearts": ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'],
    "Diamonds": ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'],
    "Clubs": ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
}

real_values = {
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

def calculate_card_value(card):
    for suit in deck_of_cards:
        if card in deck_of_cards[suit]:
            return real_values[card]
#print(calculate_card_value('9'))  # Example usage

# TODO 2: Create a function to calculate the total score of a hand
# - Sum up all card values
# - Adjust for Aces (convert from 11 to 1 if total exceeds 21)

def calculate_hand_score(hand):
    score = 0
    ace_count = 0

    for card in hand:
        card_value = calculate_card_value(card)
        score += card_value
        if card == 'A':
            ace_count += 1

    while score > 21 and ace_count:
        score -= 10
        ace_count -= 1
    return score

# print(calculate_hand_score(['A', 'A', 'A']))  # Example usage

# TODO 3: Create a function to deal cards
# - Generate random cards from the deck
# - Return a single card or a hand of cards

def deal_card():
    suit = random.choice(list(deck_of_cards.keys()))
    card = random.choice(deck_of_cards[suit])
    return card

# print(deal_card())  # Example usage

# TODO 4: Create a function to display the game state
# - Show player's hand and score
# - Show only one dealer card initially
# - Show full dealer hand after dealer's turn

def display_game_state(player_hand, dealer_hand, hide_dealer_card=True):
    player_score = calculate_hand_score(player_hand)
    dealer_score = calculate_hand_score(dealer_hand)

    print(f"Player's hand: {player_hand}, score: {player_score}")
    if hide_dealer_card:
        print(f"Dealer's hand: [{dealer_hand[0]}, '?']")
    else:
        print(f"Dealer's hand: {dealer_hand}, score: {dealer_score}")

# print(display_game_state(['A', '7'], ['K', '5']))  # Example usage


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

def blackjack_game():
    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]

    game_over = False

    while not game_over:
        display_game_state(player_hand, dealer_hand)

        player_score = calculate_hand_score(player_hand)
        if player_score == 21:
            print("Blackjack! You win!")
            return
        elif player_score > 21:
            print("You busted! Dealer wins.")
            return

        action = input("Type 'h' to hit or 's' to stand: ")
        while action not in ['h', 's']:
            action = input("Invalid input. Type 'h' to hit or 's' to stand: ")
        if action == 'h':
            player_hand.append(deal_card())
        else:
            game_over = True

    while calculate_hand_score(dealer_hand) < 17:
        dealer_hand.append(deal_card())

    display_game_state(player_hand, dealer_hand, hide_dealer_card=False)

    # Determine winner
    player_score = calculate_hand_score(player_hand)
    dealer_score = calculate_hand_score(dealer_hand)

    if dealer_score > 21:
        print("Dealer busted! You win!")
    elif player_score > dealer_score:
        print("You win!")
    elif player_score < dealer_score:
        print("Dealer wins!")
    else:
        print("It's a tie!")

continue_game = 'y'
while continue_game == 'y':
    blackjack_game()
    continue_game = input("Do you want to play again? Type 'y' or 'n': ")
    while continue_game not in ['y', 'n']:
        continue_game = input("Invalid input. Do you want to play again? Type 'y' or 'n': ")
    if continue_game != 'y':
        print("Thanks for playing!")
        break