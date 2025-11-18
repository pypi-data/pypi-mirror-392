from collections import Counter

from PokerLib.Cards import Deck
from PokerLib.TestingLogic import check_hand
results = []

for _ in range(100):
    
    deck = Deck()
    deck.shuffle()
    my_hand = deck.deal(2)
    community_cards = deck.deal_community_cards(5, [my_hand])
    
    hand_type = check_hand(my_hand, community_cards)
    results.append(hand_type)


counted_results = Counter(results)

print(counted_results)
