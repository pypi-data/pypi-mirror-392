import random
ranks = [2,3,4,5,6,7,8,9,10,"J", "Q", "K", "A"]
suits = ['hearts', 'spades', 'diamonds', 'clubs']


card = ('A', 'spades')

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"



class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, n):
        hand = self.cards[:n]
        self.cards = self.cards[n:]
        return hand
    def deal_community_cards(self, num_cards, player_hands):
        used_cards = {card for hand in player_hands for card in hand}
        community_cards = []
        for card in self.cards:
            if card not in used_cards:
                community_cards.append(card)
                if len(community_cards) == num_cards:
                    break
        for card in community_cards:
                self.cards.remove(card)
        return community_cards