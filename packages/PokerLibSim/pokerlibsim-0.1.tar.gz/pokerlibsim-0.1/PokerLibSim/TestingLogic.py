from .Cards import Deck
from collections import Counter
deck = Deck()
deck.shuffle()
my_hand = deck.deal(2)
community_cards = deck.deal_community_cards(5, [my_hand])
def check_hand(hand, community_cards=[]):
    cards = hand + community_cards

    ranks = [card.rank for card in cards]
    suits = [card.suit for card in cards]
    rank_values = []
    for r in ranks:
        if r == "J": rank_values.append(11)
        elif r == "Q": rank_values.append(12)
        elif r == "K": rank_values.append(13)
        elif r == "A": rank_values.append(14)
        else:
            rank_values.append(r)

    rank_counts = Counter(rank_values)
    suit_counts = Counter(suits)
    # full house
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        return "Full House"
    
    # 4 of a kind
    if 4 in rank_counts.values():
        return "Four of a Kind"
    
    # 3 of a kind
    if 3 in rank_counts.values():
        return "Three of a Kind"

    # 2 pair
    if list(rank_counts.values()).count(2) == 2:
        return "Two Pair"

    # pair
    if 2 in rank_counts.values():
        return "Pair"

    # flush (5 cards same suit)
    if 5 in suit_counts.values():
        return "Flush"

    # straight (5 consecutive ranks)
    rank_values_sorted = sorted(set(rank_values))
    for i in range(len(rank_values_sorted) - 4):
        if rank_values_sorted[i+4] - rank_values_sorted[i] == 4:
            return "Straight"

    # if nothing else
    return "High Card"
