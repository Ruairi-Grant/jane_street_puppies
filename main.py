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

# Evaluate a hand of 5 or 7 cards
def evaluate_hand(card_strs):
    try:
        cards = [to_deuces(c) for c in card_strs]
        # Debug: print the cards being evaluated
        # print(f"Debug: Evaluating cards: {card_strs} -> {[Card.print_pretty_card(c) for c in cards]}")
        
        if len(cards) == 5:
            # For 5-card hands, evaluate directly
            return evaluator.evaluate([], cards)  # No hole cards, all board
        elif len(cards) == 7:
            # For 7-card hands, use hole cards + board format (player 2 + river 5)
            return evaluator.evaluate(cards[:2], cards[2:])  # [hole, board]
        else:
            raise ValueError(f"Hand must have 5 or 7 cards, got {len(cards)}")
    except Exception as e:
        print(f"Error evaluating hand {card_strs}: {e}")
        # Return a high score (bad hand) for errors
        raise RuntimeError(f"Failed to evaluate hand {card_strs}: {e}")

# Optional: readable hand class for 5 or 7 card hands
def hand_class(card_strs):
    cards = [to_deuces(c) for c in card_strs]
    if len(cards) == 5:
        return evaluator.class_to_string(evaluator.get_rank_class(evaluator.evaluate([], cards)))
    elif len(cards) == 7:
        return evaluator.class_to_string(evaluator.get_rank_class(evaluator.evaluate(cards[:2], cards[2:])))
    else:
        raise ValueError(f"Hand must have 5 or 7 cards, got {len(cards)}")

# Check how much a player's hand improves with river cards
def check_hand_improvement(player_cards, river_cards):
    """
    Returns improvement metrics for a player's hand with given river cards.
    Lower scores are better in deuces, so improvement = worse_score - better_score
    """
    # Player hand: evaluate player cards + river
    full_hand = player_cards + river_cards
    player_score = evaluate_hand(full_hand)
    # Baseline: evaluate just the river cards as a 5-card hand (no hole cards)
    baseline_score = evaluate_hand(river_cards)  # Use our updated function for 5-card evaluation
    
    # Improvement (positive = better than baseline)
    improvement = baseline_score - player_score
    
    return {
        'baseline_score': baseline_score,
        'player_score': player_score, 
        'improvement': improvement,
        'hand_type': hand_class(full_hand)
    }

# Analyze all players for a given river
# Analyze all players for a given river
def analyze_players_for_river(players_df, river_cards):
    """Analyze how each player performs with the given river cards"""
    results = []
    
    for _, player_row in players_df.iterrows():
        player_cards = [str(player_row["Card 1"]).strip(), str(player_row["Card 2"]).strip()]
        player_no = player_row["Player No"]
        
        # Skip players with unknown cards
        if '??' in player_cards:
            continue
        
        improvement_data = check_hand_improvement(player_cards, river_cards)
        
        results.append({
            'player_no': player_no,
            'player_cards': player_cards,
            'improvement': improvement_data['improvement'],
            'player_score': improvement_data['player_score'],
            'hand_type': improvement_data['hand_type']
        })
    
    # Sort by improvement (highest improvement first)
    results.sort(key=lambda x: x['improvement'], reverse=True)
    return results

# --- Step 1: Build a deck ---
suits = ["s", "h", "d", "c"]  # Spades, Hearts, Diamonds, Clubs (lowercase to match CSV)
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
    
    # --- Step 5: Analyze hand improvements for sample river ---
    print(f"\n--- Analysis for river: {river} ---")
    analysis_results = analyze_players_for_river(players_df, river)
    
    print("Player improvements (sorted by improvement):")
    for result in analysis_results:
        print(f"Player {result['player_no']}: {result['player_cards']} -> "
              f"{result['hand_type']} (score: {result['player_score']}, "
              f"improvement: {result['improvement']:+d})")
    
    # --- Find best and worst performing players for this river ---
    best_player = analysis_results[0]
    worst_player = analysis_results[-1]
    
    print(f"\nBest performer: Player {best_player['player_no']} "
          f"(improvement: {best_player['improvement']:+d})")
    print(f"Worst performer: Player {worst_player['player_no']} "
          f"(improvement: {worst_player['improvement']:+d})")
    
    # --- Sample analysis for multiple rivers ---
    print("\n--- Quick analysis of first 5 river combinations ---")
    for i in range(min(5, len(river_combos))):
        river = list(river_combos[i])
        results = analyze_players_for_river(players_df, river)
        best = results[0]
        worst = results[-1]
        improvement_range = best['improvement'] - worst['improvement']
        print(f"River {i+1}: Best improvement {best['improvement']:+d} "
              f"(Player {best['player_no']}), "
              f"Worst {worst['improvement']:+d} (Player {worst['player_no']}), "
              f"Range: {improvement_range}")

