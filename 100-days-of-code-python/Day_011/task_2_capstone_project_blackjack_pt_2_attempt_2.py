"""
╔══════════════════════════════════════════════════════════════════╗
║         ULTIMATE BLACKJACK - The Best Version Ever!              ║
║                                                                  ║
║  Features:                                                       ║
║  ✓ Professional card rendering with ASCII art                   ║
║  ✓ Complete betting system with bankroll management             ║
║  ✓ Split pairs functionality                                    ║
║  ✓ Double down option                                           ║
║  ✓ Insurance against dealer blackjack                           ║
║  ✓ Proper deck management (6-deck shoe with shuffle tracking)   ║
║  ✓ Game statistics and session tracking                         ║
║  ✓ Surrender option                                             ║
║  ✓ Blackjack pays 3:2                                           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import random
import os
from typing import List, Tuple, Optional


# ═══════════════════════════════════════════════════════════════════
#                         CARD CLASS
# ═══════════════════════════════════════════════════════════════════

class Card:
    """Represents a playing card with suit and rank."""
    
    SUITS = {'♠': 'Spades', '♥': 'Hearts', '♦': 'Diamonds', '♣': 'Clubs'}
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
    }
    
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
        self.value = self.VALUES[rank]
    
    def __str__(self):
        return f"{self.rank}{self.suit}"
    
    def __repr__(self):
        return self.__str__()
    
    def get_ascii_art(self) -> List[str]:
        """Returns ASCII art representation of the card."""
        rank_display = self.rank.ljust(2)
        return [
            "┌─────────┐",
            f"│{rank_display}       │",
            "│         │",
            f"│    {self.suit}    │",
            "│         │",
            f"│       {rank_display}│",
            "└─────────┘"
        ]


# ═══════════════════════════════════════════════════════════════════
#                         DECK CLASS
# ═══════════════════════════════════════════════════════════════════

class Deck:
    """Represents a 6-deck shoe used in casino blackjack."""
    
    def __init__(self, num_decks: int = 6):
        self.num_decks = num_decks
        self.cards = []
        self.discards = []
        self.shuffle_point = 0
        self.reset()
    
    def reset(self):
        """Creates a fresh shoe with multiple decks and shuffles."""
        self.cards = []
        for _ in range(self.num_decks):
            for suit in Card.SUITS.keys():
                for rank in Card.RANKS:
                    self.cards.append(Card(suit, rank))
        random.shuffle(self.cards)
        # Shuffle point at 75% penetration (casino standard)
        self.shuffle_point = len(self.cards) // 4
        self.discards = []
    
    def deal_card(self) -> Card:
        """Deals one card from the shoe."""
        if len(self.cards) <= self.shuffle_point:
            print("\n♠♥♦♣ Shuffling cards... ♠♥♦♣\n")
            self.reset()
        return self.cards.pop()
    
    def discard(self, card: Card):
        """Adds a card to the discard pile."""
        self.discards.append(card)


# ═══════════════════════════════════════════════════════════════════
#                         HAND CLASS
# ═══════════════════════════════════════════════════════════════════

class Hand:
    """Represents a blackjack hand."""
    
    def __init__(self):
        self.cards: List[Card] = []
        self.bet = 0
        self.is_split = False
        self.is_doubled = False
        self.is_surrendered = False
        self.is_settled = False
    
    def add_card(self, card: Card):
        """Adds a card to the hand."""
        self.cards.append(card)
    
    def get_value(self) -> int:
        """Calculates the best value for the hand."""
        total = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'A')
        
        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def is_blackjack(self) -> bool:
        """Checks if hand is a natural blackjack."""
        return len(self.cards) == 2 and self.get_value() == 21
    
    def is_busted(self) -> bool:
        """Checks if hand is busted."""
        return self.get_value() > 21
    
    def can_split(self) -> bool:
        """Checks if hand can be split."""
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank
    
    def can_double(self) -> bool:
        """Checks if hand can be doubled down."""
        return len(self.cards) == 2 and not self.is_split
    
    def __str__(self):
        return f"{[str(card) for card in self.cards]} (Value: {self.get_value()})"


# ═══════════════════════════════════════════════════════════════════
#                         PLAYER CLASS
# ═══════════════════════════════════════════════════════════════════

class Player:
    """Represents the player with bankroll and statistics."""
    
    def __init__(self, starting_chips: int = 1000):
        self.chips = starting_chips
        self.starting_chips = starting_chips
        self.hands_won = 0
        self.hands_lost = 0
        self.hands_pushed = 0
        self.blackjacks = 0
        self.total_wagered = 0
        self.total_won = 0
    
    def can_bet(self, amount: int) -> bool:
        """Checks if player has enough chips to bet."""
        return self.chips >= amount
    
    def place_bet(self, amount: int) -> bool:
        """Places a bet if player has enough chips."""
        if self.can_bet(amount):
            self.chips -= amount
            self.total_wagered += amount
            return True
        return False
    
    def win_bet(self, amount: int):
        """Awards chips for winning."""
        self.chips += amount
        self.total_won += amount
        self.hands_won += 1
    
    def lose_bet(self):
        """Records a loss."""
        self.hands_lost += 1
    
    def push_bet(self, amount: int):
        """Returns bet for a push."""
        self.chips += amount
        self.hands_pushed += 1
    
    def get_stats(self) -> str:
        """Returns formatted statistics."""
        total_hands = self.hands_won + self.hands_lost + self.hands_pushed
        win_rate = (self.hands_won / total_hands * 100) if total_hands > 0 else 0
        net_profit = self.chips - self.starting_chips
        
        stats = f"""
╔══════════════════════════════════════════════════════════════════╗
║                      SESSION STATISTICS                          ║
╠══════════════════════════════════════════════════════════════════╣
║  Bankroll: ${self.chips:,}  (Starting: ${self.starting_chips:,})
║  Net Profit/Loss: ${net_profit:+,}
║  
║  Hands Won: {self.hands_won}
║  Hands Lost: {self.hands_lost}
║  Hands Pushed: {self.hands_pushed}
║  Blackjacks: {self.blackjacks}
║  
║  Total Hands: {total_hands}
║  Win Rate: {win_rate:.1f}%
║  
║  Total Wagered: ${self.total_wagered:,}
║  Total Won: ${self.total_won:,}
╚══════════════════════════════════════════════════════════════════╝
        """
        return stats


# ═══════════════════════════════════════════════════════════════════
#                      DISPLAY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_cards(hands: List[Hand], labels: List[str], hide_first: bool = False):
    """Displays multiple hands side by side with ASCII art."""
    for idx, (hand, label) in enumerate(zip(hands, labels)):
        print(f"\n{label}:")
        
        if hide_first and idx == 0:
            # Show only first card for dealer
            card_arts = [hand.cards[0].get_ascii_art()]
            hidden_card = [
                "┌─────────┐",
                "│░░░░░░░░░│",
                "│░░░░░░░░░│",
                "│░░░░░░░░░│",
                "│░░░░░░░░░│",
                "│░░░░░░░░░│",
                "└─────────┘"
            ]
            card_arts.append(hidden_card)
        else:
            card_arts = [card.get_ascii_art() for card in hand.cards]
        
        # Print cards side by side
        for line_idx in range(7):
            line = "  ".join(art[line_idx] for art in card_arts)
            print(line)
        
        # Show value
        if not (hide_first and idx == 0):
            value = hand.get_value()
            if hand.is_blackjack():
                print(f"  ★ BLACKJACK! ★ (21)")
            elif hand.is_busted():
                print(f"  ✗ BUSTED! ({value})")
            else:
                print(f"  Value: {value}")


def display_welcome():
    """Displays welcome banner."""
    clear_screen()
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║      ♠♥  ULTIMATE BLACKJACK CASINO  ♦♣                          ║
║                                                                  ║
║              The Best Blackjack Game Ever!                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Welcome to the most feature-rich command-line blackjack experience!

Rules:
• Dealer stands on all 17s
• Blackjack pays 3:2
• You can split pairs (including Aces)
• You can double down on any first two cards
• Insurance available when dealer shows Ace
• Surrender available before playing hand

Good luck at the tables!
""")
    input("Press Enter to start playing...")


# ═══════════════════════════════════════════════════════════════════
#                      GAME LOGIC FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def get_bet(player: Player) -> Optional[int]:
    """Gets bet amount from player."""
    print(f"\nYour chips: ${player.chips:,}")
    print("Enter bet amount (or 'q' to quit, 's' for stats):")
    
    while True:
        bet_input = input("$ ").strip().lower()
        
        if bet_input == 'q':
            return None
        
        if bet_input == 's':
            print(player.get_stats())
            print(f"\nYour chips: ${player.chips:,}")
            print("Enter bet amount (or 'q' to quit):")
            continue
        
        try:
            bet = int(bet_input)
            if bet < 1:
                print("Minimum bet is $1. Try again:")
                continue
            if not player.can_bet(bet):
                print(f"Insufficient chips! You have ${player.chips:,}. Try again:")
                continue
            return bet
        except ValueError:
            print("Invalid input. Enter a number:")


def offer_insurance(player: Player, dealer_hand: Hand, initial_bet: int) -> int:
    """Offers insurance bet if dealer shows Ace."""
    if dealer_hand.cards[0].rank != 'A':
        return 0
    
    max_insurance = initial_bet // 2
    print(f"\n💡 Dealer shows an Ace! Insurance available (max ${max_insurance}).")
    print("Insurance pays 2:1 if dealer has blackjack.")
    
    choice = input("Buy insurance? (y/n): ").strip().lower()
    if choice == 'y':
        if player.can_bet(max_insurance):
            player.place_bet(max_insurance)
            return max_insurance
        else:
            print("Insufficient chips for insurance!")
    return 0


def player_turn(hand: Hand, deck: Deck, player: Player, can_split: bool = True) -> bool:
    """Handles player's turn. Returns True if player wants to split."""
    if hand.is_surrendered:
        return False
    
    while not hand.is_busted() and not hand.is_blackjack():
        print("\nYour options:")
        options = "[H]it / [S]tand"
        
        if hand.can_double() and player.can_bet(hand.bet):
            options += " / [D]ouble down"
        
        if hand.can_split() and can_split and player.can_bet(hand.bet):
            options += " / S[P]lit"
        
        if len(hand.cards) == 2:
            options += " / S[U]rrender"
        
        choice = input(f"{options}: ").strip().lower()
        
        if choice == 'h':
            hand.add_card(deck.deal_card())
            display_cards([hand], ["Your hand"])
            if hand.is_busted():
                print("\n💥 BUSTED!")
        
        elif choice == 's':
            break
        
        elif choice == 'd' and hand.can_double() and player.can_bet(hand.bet):
            player.place_bet(hand.bet)
            hand.bet *= 2
            hand.is_doubled = True
            hand.add_card(deck.deal_card())
            display_cards([hand], ["Your hand"])
            print("(Doubled down - no more cards)")
            break
        
        elif choice == 'p' and hand.can_split() and can_split and player.can_bet(hand.bet):
            return True  # Signal to split
        
        elif choice == 'u' and len(hand.cards) == 2:
            hand.is_surrendered = True
            print("Hand surrendered. You lose half your bet.")
            break
        
        else:
            print("Invalid choice. Try again.")
    
    return False


def dealer_turn(hand: Hand, deck: Deck):
    """Handles dealer's turn."""
    while hand.get_value() < 17:
        hand.add_card(deck.deal_card())
    
    display_cards([hand], ["Dealer's hand"])


def settle_hand(player_hand: Hand, dealer_hand: Hand, player: Player, insurance_bet: int = 0):
    """Settles the hand and updates player chips/stats."""
    if player_hand.is_settled:
        return
    
    player_hand.is_settled = True
    dealer_value = dealer_hand.get_value()
    player_value = player_hand.get_value()
    
    # Handle insurance
    if insurance_bet > 0:
        if dealer_hand.is_blackjack():
            payout = insurance_bet * 3  # 2:1 payout plus original bet
            player.win_bet(payout)
            print(f"\n✓ Insurance wins! +${insurance_bet * 2}")
        else:
            print(f"\n✗ Insurance loses. -${insurance_bet}")
    
    # Handle surrender
    if player_hand.is_surrendered:
        refund = player_hand.bet // 2
        player.push_bet(refund)
        print(f"\n→ Surrendered. Refund: ${refund}")
        return
    
    # Handle results
    print("\n" + "═" * 66)
    
    if player_hand.is_busted():
        player.lose_bet()
        print("💥 YOU BUSTED - DEALER WINS")
    elif dealer_hand.is_busted():
        payout = player_hand.bet * 2
        player.win_bet(payout)
        print(f"💥 DEALER BUSTED - YOU WIN ${player_hand.bet}! 💰")
    elif player_hand.is_blackjack() and not dealer_hand.is_blackjack():
        payout = int(player_hand.bet * 2.5)  # 3:2 payout
        player.win_bet(payout)
        player.blackjacks += 1
        print(f"★ BLACKJACK! YOU WIN ${int(player_hand.bet * 1.5)}! ★ (3:2 payout) 💰")
    elif dealer_hand.is_blackjack() and not player_hand.is_blackjack():
        player.lose_bet()
        print("★ DEALER BLACKJACK - DEALER WINS")
    elif player_value > dealer_value:
        payout = player_hand.bet * 2
        player.win_bet(payout)
        print(f"🎉 YOU WIN ${player_hand.bet}! 💰")
    elif player_value < dealer_value:
        player.lose_bet()
        print("DEALER WINS")
    else:
        player.push_bet(player_hand.bet)
        print(f"🤝 PUSH - Bet returned (${player_hand.bet})")
    
    print("═" * 66)


# ═══════════════════════════════════════════════════════════════════
#                         MAIN GAME FUNCTION
# ═══════════════════════════════════════════════════════════════════

def play_blackjack():
    """Main game loop."""
    display_welcome()
    
    # Initialize game components
    player = Player(starting_chips=1000)
    deck = Deck(num_decks=6)
    
    # Outer loop for play again functionality
    play_again = True
    
    while play_again:
        # Main game loop
        while player.chips > 0:
            clear_screen()
            print("═" * 66)
            print(f"  💰 CHIPS: ${player.chips:,}")
            print("═" * 66)
            
            # Get bet
            bet = get_bet(player)
            if bet is None:
                break
            
            # Place bet and create initial hands
            player.place_bet(bet)
            player_hands = [Hand()]
            player_hands[0].bet = bet
            dealer_hand = Hand()
            
            # Deal initial cards
            for _ in range(2):
                player_hands[0].add_card(deck.deal_card())
                dealer_hand.add_card(deck.deal_card())
            
            # Display initial deal
            clear_screen()
            print("═" * 66)
            display_cards([dealer_hand], ["Dealer's hand"], hide_first=True)
            display_cards(player_hands, ["Your hand"])
            
            # Check for dealer blackjack (peek)
            dealer_shows_ace = dealer_hand.cards[0].rank == 'A'
            dealer_shows_ten = dealer_hand.cards[0].value == 10
            
            insurance_bet = 0
            if dealer_shows_ace:
                insurance_bet = offer_insurance(player, dealer_hand, bet)
            
            # Check for blackjacks
            if dealer_hand.is_blackjack():
                display_cards([dealer_hand], ["Dealer's hand"])
                if player_hands[0].is_blackjack():
                    print("\n🤝 Both have BLACKJACK - PUSH!")
                    player.push_bet(bet)
                    player.hands_pushed += 1
                else:
                    print("\n★ DEALER BLACKJACK!")
                    player.lose_bet()
                
                if insurance_bet > 0:
                    payout = insurance_bet * 3
                    player.win_bet(payout)
                    print(f"✓ Insurance wins! +${insurance_bet * 2}")
                
                input("\nPress Enter to continue...")
                continue
            
            if player_hands[0].is_blackjack():
                display_cards([dealer_hand], ["Dealer's hand"])
                payout = int(bet * 2.5)
                player.win_bet(payout)
                player.blackjacks += 1
                print(f"\n★ BLACKJACK! YOU WIN ${int(bet * 1.5)}! ★ (3:2 payout) 💰")
                input("\nPress Enter to continue...")
                continue
            
            # Play each hand (support for splits)
            hand_idx = 0
            while hand_idx < len(player_hands):
                current_hand = player_hands[hand_idx]
                
                if len(player_hands) > 1:
                    clear_screen()
                    print("═" * 66)
                    display_cards([dealer_hand], ["Dealer's hand"], hide_first=True)
                    print(f"\n--- Playing Hand {hand_idx + 1} of {len(player_hands)} ---")
                    display_cards([current_hand], ["Your hand"])
                
                # Player's turn
                should_split = player_turn(current_hand, deck, player, can_split=(len(player_hands) < 4))
                
                if should_split:
                    # Create split hand
                    new_hand = Hand()
                    new_hand.bet = current_hand.bet
                    new_hand.is_split = True
                    new_hand.add_card(current_hand.cards.pop())
                    current_hand.is_split = True
                    
                    # Deal new card to each hand
                    current_hand.add_card(deck.deal_card())
                    new_hand.add_card(deck.deal_card())
                    
                    player_hands.insert(hand_idx + 1, new_hand)
                    player.place_bet(new_hand.bet)
                    
                    print(f"\n✂ Hand split! Now playing hand {hand_idx + 1}...")
                    display_cards([current_hand], ["Your hand"])
                    continue  # Replay this hand
                
                hand_idx += 1
            
            # Dealer's turn (if any player hand is not busted)
            any_hand_active = any(not hand.is_busted() and not hand.is_surrendered for hand in player_hands)
            
            if any_hand_active:
                print("\n" + "═" * 66)
                print("Dealer's turn...")
                print("═" * 66)
                dealer_turn(dealer_hand, deck)
            
            # Settle all hands
            for idx, hand in enumerate(player_hands):
                if len(player_hands) > 1:
                    print(f"\n--- Hand {idx + 1} ---")
                    display_cards([hand], ["Your hand"])
                settle_hand(hand, dealer_hand, player, insurance_bet if idx == 0 else 0)
            
            input("\nPress Enter to continue...")
        
        # Out of chips - offer to play again
        if player.chips <= 0:
            clear_screen()
            print("\n" + "═" * 66)
            print("💸 OUT OF CHIPS!")
            print("═" * 66)
            print(player.get_stats())
            
            choice = input("\n🎰 Want to play again with a fresh bankroll? (y/n): ").strip().lower()
            
            if choice == 'y':
                # Reset chips but keep statistics for the session
                player.chips = player.starting_chips
                print(f"\n✓ Bankroll reset to ${player.starting_chips:,}!")
                print("♠♥♦♣ Good luck! ♠♥♦♣")
                input("\nPress Enter to continue...")
            else:
                play_again = False
        else:
            # Player chose to quit
            play_again = False
    
    # Final goodbye
    clear_screen()
    print("\n" + "═" * 66)
    print("THANKS FOR PLAYING!")
    print("═" * 66)
    print(player.get_stats())
    print("\nCome back soon to Ultimate Blackjack! 🎰")


# ═══════════════════════════════════════════════════════════════════
#                         RUN GAME
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    play_blackjack()