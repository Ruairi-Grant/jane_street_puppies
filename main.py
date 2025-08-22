import pandas as pd
import itertools

# --- Step 0: Deuces poker hand evaluator ---
from deuces import Card, Evaluator

evaluator = Evaluator()

# Helper: convert 'AS', '10H', etc. to Deuces format
def to_deuces(card_str):
    rank_map = {'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J', 'T': 'T', '10': 'T', '9': '9', '8': '8', '7': '7', '6': '6', '5': '5', '4': '4', '3': '3', '2': '2'}
    suit_map = {'S': 's', 'H': 'h', 'D': 'd', 'C': 'c', 's': 's', 'h': 'h', 'd': 'd', 'c': 'c'}
    card_str = card_str.strip()
    suit = suit_map[card_str[-1]]
    rank = card_str[:-1]
    rank = rank_map[rank] if rank in rank_map else rank
    return Card.new(rank + suit)

# Evaluate a 7-card hand (player 2 + river 5)
def evaluate_hand(card_strs):
    cards = [to_deuces(c) for c in card_strs]
    return evaluator.evaluate(cards[:2], cards[2:])  # [hole, board]

# Optional: readable hand class
def hand_class(card_strs):
    cards = [to_deuces(c) for c in card_strs]
    return evaluator.class_to_string(evaluator.get_rank_class(evaluator.evaluate(cards[:2], cards[2:])))

# --- Step 1: Build a deck ---
suits = ["S", "H", "D", "C"]  # Spades, Hearts, Diamonds, Clubs
ranks = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]

deck = [r + s for r, s in itertools.product(ranks, suits)]

# --- Step 2: Load CSV of players ---
def load_players(csv_path: str):
    df = pd.read_csv(csv_path)
    return df

# --- Step 3: Build known / unknown card sets ---
def build_exclusion_table(players_df):
    known_cards = set()
    unknowns = []

    for _, row in players_df.iterrows():
        for col in ["Card 1", "Card 2"]:
            card = str(row[col]).strip()
            if card != "??":
                known_cards.add(card)
            else:
                unknowns.append((row["Player No"], col))

    remaining_deck = [c for c in deck if c not in known_cards]

    return {
        "known_cards": known_cards,
        "unknowns": unknowns,
        "remaining_deck": remaining_deck,
    }

# --- Example usage ---
if __name__ == "__main__":
    # Example CSV path
    csv_path = "player_hands.csv"
    players_df = load_players(csv_path)
    table = build_exclusion_table(players_df)

    print("Known cards:", table["known_cards"])
    print("Unknown slots:", table["unknowns"])
    print("Remaining deck (available):", table["remaining_deck"])

    # --- Step 4: Generate all possible 5-card river combinations ---
    from itertools import combinations

    river_combos = list(combinations(table["remaining_deck"], 5))
    print(f"Total possible river combinations: {len(river_combos):,}")

    # --- Example: Evaluate a sample hand (first player, first river combo) ---
    player_row = players_df.iloc[0]
    player_cards = [str(player_row["Card 1"]).strip(), str(player_row["Card 2"]).strip()]
    # Use first river combo as example
    river = list(river_combos[0])
    full_hand = player_cards + river
    score = evaluate_hand(full_hand)
    handtype = hand_class(full_hand)
    print(f"Player hand: {player_cards}, River: {river}")
    print(f"Hand score (lower is better): {score}, Hand type: {handtype}")

