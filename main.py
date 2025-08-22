import pandas as pd
import itertools

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
